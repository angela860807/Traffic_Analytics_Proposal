package com.example.traffic.service;

import com.example.traffic.common.enums.*;
import com.example.traffic.domain.*;
import com.example.traffic.dto.request.predictive.*;
import com.example.traffic.dto.response.predictive.*;
import com.example.traffic.etc.BusinessException;
import com.example.traffic.repository.*;
import com.example.traffic.util.PredictiveTimeUtils;
import jakarta.persistence.criteria.JoinType;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.http.HttpStatus;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.security.core.Authentication;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.time.OffsetDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;

@Service
@Transactional(readOnly = true)
@RequiredArgsConstructor
public class PredictiveOperationsService {
    private static final Set<UserRole> ASSIGNABLE_ROLES = EnumSet.of(
            UserRole.MAINTAINER,
            UserRole.OPERATOR,
            UserRole.ADMIN
    );

    private static final Map<String, String> ANOMALY_SORTS = Map.of(
            "firstDetectedAt", "firstDetectedAt",
            "lastDetectedAt", "lastDetectedAt",
            "severity", "severity",
            "anomalyScore", "anomalyScore"
    );

    private static final Map<String, String> TICKET_SORTS = Map.of(
            "createdAt", "createdAt",
            "dueAckAt", "dueAckAt",
            "dueStartAt", "dueStartAt",
            "priority", "priority"
    );

    private final AnomalyEventRepository anomalyEventRepository;
    private final AnomalyEventEvidenceRepository evidenceRepository;
    private final MaintenanceTicketRepository maintenanceTicketRepository;
    private final MaintenanceTicketHistoryRepository ticketHistoryRepository;
    private final ModelPredictionLogRepository modelPredictionLogRepository;
    private final AnomalyPolicyRepository anomalyPolicyRepository;
    private final MemberRepository memberRepository;
    private final MaintenanceTicketStateTransitionService ticketStateTransitionService;
    private final JdbcTemplate jdbcTemplate;

    public PageResponse<AnomalyEventSummaryResponse> getAnomalyEvents(AnomalyEventSearchRequest request) {
        validateDateRange(request.getFrom(), request.getTo());
        Pageable pageable = toPageable(request.getPage(), request.getSize(), request.getSort(), ANOMALY_SORTS);
        Page<AnomalyEvent> page = anomalyEventRepository.findAll(anomalySpec(request), pageable);
        return PageResponse.<AnomalyEventSummaryResponse>builder()
                .content(page.getContent().stream().map(this::toAnomalySummary).toList())
                .page(page.getNumber())
                .size(page.getSize())
                .totalElements(page.getTotalElements())
                .totalPages(page.getTotalPages())
                .sort(request.getSort())
                .build();
    }

    public AnomalyEventDetailResponse getAnomalyEvent(Long eventId) {
        AnomalyEvent event = findAnomalyEvent(eventId);
        List<AnomalyEventEvidence> evidence = evidenceRepository
                .findByAnomalyEvent_IdOrderBySampledAtDescIdDesc(eventId);
        MaintenanceTicket ticket = maintenanceTicketRepository.findByAnomalyEvent_Id(eventId).orElse(null);
        ModelPredictionLog shadowModel = event.getTargetCamera() == null
                ? null
                : modelPredictionLogRepository
                .findFirstByCamera_CameraIdAndDataSourceOrderByEvaluatedAtDesc(
                        event.getTargetCamera().getCameraId(),
                        event.getDataSource()
                )
                .orElse(null);
        return toAnomalyDetail(event, evidence, ticket, shadowModel);
    }

    @Transactional
    public AnomalyEventDetailResponse acknowledgeAnomalyEvent(
            Long eventId,
            AnomalyAcknowledgeRequest request,
            Authentication authentication
    ) {
        Member member = currentMember(authentication);
        AnomalyEvent event = findAnomalyEvent(eventId);
        try {
            event.acknowledge(member, LocalDateTime.now(PredictiveTimeUtils.SERVICE_ZONE));
        } catch (IllegalStateException exc) {
            throw new BusinessException(exc.getMessage(), HttpStatus.CONFLICT);
        }
        return getAnomalyEvent(eventId);
    }

    @Transactional
    public AnomalyEventDetailResponse resolveAnomalyEvent(
            Long eventId,
            AnomalyResolveRequest request,
            Authentication authentication
    ) {
        Member member = currentMember(authentication);
        AnomalyEvent event = findAnomalyEvent(eventId);
        try {
            event.resolve(
                    member,
                    request.getConfirmedCause(),
                    request.getResolutionNote(),
                    LocalDateTime.now(PredictiveTimeUtils.SERVICE_ZONE)
            );
        } catch (IllegalStateException exc) {
            throw new BusinessException(exc.getMessage(), HttpStatus.CONFLICT);
        }
        return getAnomalyEvent(eventId);
    }

    @Transactional
    public AnomalyEventDetailResponse dismissAnomalyEvent(
            Long eventId,
            AnomalyDismissRequest request,
            Authentication authentication
    ) {
        Member member = currentMember(authentication);
        AnomalyEvent event = findAnomalyEvent(eventId);
        try {
            event.dismiss(member, request.getReason(), LocalDateTime.now(PredictiveTimeUtils.SERVICE_ZONE));
        } catch (IllegalStateException exc) {
            throw new BusinessException(exc.getMessage(), HttpStatus.CONFLICT);
        }
        return getAnomalyEvent(eventId);
    }

    public PageResponse<MaintenanceTicketResponse> getMaintenanceTickets(MaintenanceTicketSearchRequest request) {
        Pageable pageable = toPageable(request.getPage(), request.getSize(), request.getSort(), TICKET_SORTS);
        Page<MaintenanceTicket> page = maintenanceTicketRepository.findAll(ticketSpec(request), pageable);
        return PageResponse.<MaintenanceTicketResponse>builder()
                .content(page.getContent().stream().map(this::toTicketResponse).toList())
                .page(page.getNumber())
                .size(page.getSize())
                .totalElements(page.getTotalElements())
                .totalPages(page.getTotalPages())
                .sort(request.getSort())
                .build();
    }

    public List<PredictiveAssigneeResponse> getAssignees(List<UserRole> requestedRoles) {
        Set<UserRole> roles = requestedRoles == null || requestedRoles.isEmpty()
                ? ASSIGNABLE_ROLES
                : EnumSet.copyOf(requestedRoles);
        roles.retainAll(ASSIGNABLE_ROLES);
        if (roles.isEmpty()) {
            return List.of();
        }
        return memberRepository.findByRoleInOrderByRoleAscNameAsc(roles).stream()
                .map(member -> PredictiveAssigneeResponse.builder()
                        .memberId(member.getMemberId())
                        .name(member.getName())
                        .email(member.getEmail())
                        .role(member.getRole())
                        .build())
                .toList();
    }

    public List<MaintenanceTicketHistoryResponse> getMaintenanceTicketHistories(Long ticketId) {
        findMaintenanceTicket(ticketId);
        return ticketHistoryRepository.findByMaintenanceTicket_IdOrderByChangedAtAscIdAsc(ticketId).stream()
                .map(this::toTicketHistoryResponse)
                .toList();
    }

    @Transactional
    public MaintenanceTicketResponse createMaintenanceTicket(
            MaintenanceTicketCreateRequest request,
            Authentication authentication
    ) {
        Member member = currentMember(authentication);
        AnomalyEvent event = findAnomalyEvent(request.getAnomalyEventId());
        if (maintenanceTicketRepository.findByAnomalyEvent_Id(event.getId()).isPresent()) {
            throw new BusinessException("Maintenance ticket already exists for anomaly event: " + event.getId(), HttpStatus.CONFLICT);
        }
        LocalDateTime now = LocalDateTime.now(PredictiveTimeUtils.SERVICE_ZONE);
        MaintenanceTicket ticket = maintenanceTicketRepository.save(MaintenanceTicket.builder()
                .anomalyEvent(event)
                .ticketNumber(nextTicketNumber(now))
                .priority(request.getPriority())
                .status(MaintenanceStatus.OPEN)
                .dueAckAt(resolveDueAckAt(request.getPriority(), now))
                .dueStartAt(resolveDueStartAt(request.getPriority(), now))
                .actionNote(request.getActionNote())
                .createdBy(member)
                .build());
        appendTicketHistory(ticket, null, ticket.getStatus(), member, request.getActionNote());
        return toTicketResponse(ticket);
    }

    @Transactional
    public MaintenanceTicketResponse assignMaintenanceTicket(
            Long ticketId,
            MaintenanceTicketAssignRequest request,
            Authentication authentication
    ) {
        Member member = currentMember(authentication);
        MaintenanceTicket ticket = findMaintenanceTicket(ticketId);
        Member assignee = memberRepository.findById(request.getAssigneeId())
                .orElseThrow(() -> new BusinessException("Assignee not found: " + request.getAssigneeId(), HttpStatus.NOT_FOUND));
        if (!ASSIGNABLE_ROLES.contains(assignee.getRole())) {
            throw new BusinessException("Assignee role is not assignable: " + assignee.getRole(), HttpStatus.BAD_REQUEST);
        }
        MaintenanceStatus fromStatus = ticket.getStatus();
        if (MaintenanceStatus.OPEN.equals(fromStatus)) {
            ticketStateTransitionService.validateTransition(fromStatus, MaintenanceStatus.ASSIGNED, member.getRole(), request.getNote());
        } else if (MaintenanceStatus.RESOLVED.equals(fromStatus) || MaintenanceStatus.CLOSED.equals(fromStatus)) {
            throw new BusinessException("Closed maintenance ticket cannot be assigned.", HttpStatus.CONFLICT);
        }
        ticket.assign(assignee, request.getNote());
        appendTicketHistory(ticket, fromStatus, ticket.getStatus(), member, request.getNote());
        return toTicketResponse(ticket);
    }

    @Transactional
    public MaintenanceTicketResponse changeMaintenanceTicketStatus(
            Long ticketId,
            MaintenanceTicketStatusRequest request,
            Authentication authentication
    ) {
        Member member = currentMember(authentication);
        MaintenanceTicket ticket = findMaintenanceTicket(ticketId);
        MaintenanceStatus fromStatus = ticket.getStatus();
        ticketStateTransitionService.validateTransition(fromStatus, request.getToStatus(), member.getRole(), request.getNote());
        ticket.changeStatus(request.getToStatus(), request.getNote());
        appendTicketHistory(ticket, fromStatus, ticket.getStatus(), member, request.getNote());
        return toTicketResponse(ticket);
    }

    @Transactional
    public AnomalyPolicyResponse updatePolicy(
            String policyCode,
            AnomalyPolicyUpdateRequest request,
            Authentication authentication
    ) {
        Member member = currentMember(authentication);
        AnomalyPolicy policy = anomalyPolicyRepository.findByPolicyCode(policyCode)
                .orElseThrow(() -> new BusinessException("Anomaly policy not found: " + policyCode, HttpStatus.NOT_FOUND));
        policy.updateRuntimePolicy(
                request.getPredictionHorizonMinutes(),
                request.getMinimumSampleCount(),
                request.getConfig(),
                request.getEnabled(),
                member
        );
        return toPolicyResponse(policy);
    }

    private Specification<AnomalyEvent> anomalySpec(AnomalyEventSearchRequest request) {
        return (root, query, cb) -> {
            if (query.getResultType() != Long.class && query.getResultType() != long.class) {
                root.fetch("targetCamera", JoinType.LEFT);
                root.fetch("policy", JoinType.LEFT);
                root.fetch("detectorVersion", JoinType.LEFT);
            }
            List<jakarta.persistence.criteria.Predicate> predicates = new ArrayList<>();
            if (request.getCameraId() != null) {
                predicates.add(cb.equal(root.get("targetCamera").get("cameraId"), request.getCameraId()));
            }
            if (request.getSeverity() != null) {
                predicates.add(cb.equal(root.get("severity"), request.getSeverity()));
            }
            if (request.getStatus() != null) {
                predicates.add(cb.equal(root.get("status"), request.getStatus()));
            }
            if (request.getAnomalyType() != null) {
                predicates.add(cb.equal(root.get("anomalyType"), request.getAnomalyType()));
            }
            if (request.getDetectionMethod() != null) {
                predicates.add(cb.equal(root.get("detectionMethod"), request.getDetectionMethod()));
            }
            if (request.getDataSource() != null) {
                predicates.add(cb.equal(root.get("dataSource"), request.getDataSource()));
            }
            if (request.getFrom() != null) {
                predicates.add(cb.greaterThanOrEqualTo(root.get("firstDetectedAt"), toLocalDateTime(request.getFrom())));
            }
            if (request.getTo() != null) {
                predicates.add(cb.lessThan(root.get("firstDetectedAt"), toLocalDateTime(request.getTo())));
            }
            return cb.and(predicates.toArray(new jakarta.persistence.criteria.Predicate[0]));
        };
    }

    private Specification<MaintenanceTicket> ticketSpec(MaintenanceTicketSearchRequest request) {
        return (root, query, cb) -> {
            if (query.getResultType() != Long.class && query.getResultType() != long.class) {
                root.fetch("anomalyEvent", JoinType.LEFT).fetch("targetCamera", JoinType.LEFT);
                root.fetch("assignee", JoinType.LEFT);
            }
            List<jakarta.persistence.criteria.Predicate> predicates = new ArrayList<>();
            if (request.getPriority() != null) {
                predicates.add(cb.equal(root.get("priority"), request.getPriority()));
            }
            if (request.getStatus() != null) {
                predicates.add(cb.equal(root.get("status"), request.getStatus()));
            }
            if (request.getAssigneeId() != null) {
                predicates.add(cb.equal(root.get("assignee").get("memberId"), request.getAssigneeId()));
            }
            return cb.and(predicates.toArray(new jakarta.persistence.criteria.Predicate[0]));
        };
    }

    private Pageable toPageable(int page, int size, String sort, Map<String, String> whitelist) {
        if (page < 0 || size < 1 || size > 100) {
            throw new BusinessException("Invalid page or size.", HttpStatus.BAD_REQUEST);
        }
        String[] parts = sort == null ? new String[0] : sort.split(",");
        if (parts.length == 0 || parts[0].isBlank()) {
            throw new BusinessException("Sort field is required.", HttpStatus.BAD_REQUEST);
        }
        String property = whitelist.get(parts[0]);
        if (property == null) {
            throw new BusinessException("Unsupported sort field: " + parts[0], HttpStatus.BAD_REQUEST);
        }
        Sort.Direction direction = parts.length > 1 && "asc".equalsIgnoreCase(parts[1])
                ? Sort.Direction.ASC
                : Sort.Direction.DESC;
        return PageRequest.of(page, size, Sort.by(direction, property));
    }

    private void validateDateRange(OffsetDateTime from, OffsetDateTime to) {
        if (from != null && to != null && from.isAfter(to)) {
            throw new BusinessException("from must be before to.", HttpStatus.BAD_REQUEST);
        }
    }

    private AnomalyEvent findAnomalyEvent(Long eventId) {
        return anomalyEventRepository.findById(eventId)
                .orElseThrow(() -> new BusinessException("Anomaly event not found: " + eventId, HttpStatus.NOT_FOUND));
    }

    private MaintenanceTicket findMaintenanceTicket(Long ticketId) {
        return maintenanceTicketRepository.findById(ticketId)
                .orElseThrow(() -> new BusinessException("Maintenance ticket not found: " + ticketId, HttpStatus.NOT_FOUND));
    }

    private Member currentMember(Authentication authentication) {
        if (authentication == null || authentication.getName() == null) {
            throw new BusinessException("Authentication is required.", HttpStatus.UNAUTHORIZED);
        }
        return memberRepository.findByEmail(authentication.getName())
                .orElseThrow(() -> new BusinessException("Authenticated member not found: " + authentication.getName(), HttpStatus.UNAUTHORIZED));
    }

    private void appendTicketHistory(
            MaintenanceTicket ticket,
            MaintenanceStatus fromStatus,
            MaintenanceStatus toStatus,
            Member member,
            String note
    ) {
        ticketHistoryRepository.save(MaintenanceTicketHistory.builder()
                .maintenanceTicket(ticket)
                .fromStatus(fromStatus)
                .toStatus(toStatus)
                .changedBy(member)
                .note(note)
                .changedAt(LocalDateTime.now(PredictiveTimeUtils.SERVICE_ZONE))
                .build());
    }

    private String nextTicketNumber(LocalDateTime createdAt) {
        Long sequence = jdbcTemplate.queryForObject("SELECT nextval('maintenance_ticket_number_seq')", Long.class);
        return "MNT-%s-%04d".formatted(
                createdAt.format(DateTimeFormatter.BASIC_ISO_DATE),
                sequence != null ? sequence : 0L
        );
    }

    private LocalDateTime resolveDueAckAt(MaintenancePriority priority, LocalDateTime baseTime) {
        return switch (priority) {
            case P1 -> baseTime.plusMinutes(15);
            case P2 -> baseTime.plusMinutes(30);
            case P3 -> baseTime.plusHours(4);
        };
    }

    private LocalDateTime resolveDueStartAt(MaintenancePriority priority, LocalDateTime baseTime) {
        return switch (priority) {
            case P1 -> baseTime.plusHours(1);
            case P2 -> baseTime.plusHours(2);
            case P3 -> baseTime.plusDays(1);
        };
    }

    private AnomalyEventSummaryResponse toAnomalySummary(AnomalyEvent event) {
        Camera camera = event.getTargetCamera();
        return AnomalyEventSummaryResponse.builder()
                .id(event.getId())
                .targetType(event.getTargetType())
                .cameraId(camera != null ? camera.getCameraId() : null)
                .cameraName(camera != null ? camera.getCameraName() : null)
                .anomalyType(event.getAnomalyType())
                .severity(event.getSeverity())
                .status(event.getStatus())
                .detectionMethod(event.getDetectionMethod())
                .anomalyScore(event.getAnomalyScore())
                .projectedThresholdCrossingAt(toOffset(event.getProjectedThresholdCrossingAt()))
                .firstDetectedAt(toOffset(event.getFirstDetectedAt()))
                .lastDetectedAt(toOffset(event.getLastDetectedAt()))
                .dataSource(event.getDataSource())
                .build();
    }

    private AnomalyEventDetailResponse toAnomalyDetail(
            AnomalyEvent event,
            List<AnomalyEventEvidence> evidence,
            MaintenanceTicket ticket,
            ModelPredictionLog shadowModel
    ) {
        Camera camera = event.getTargetCamera();
        DetectorVersion detectorVersion = event.getDetectorVersion();
        AnomalyPolicy policy = event.getPolicy();
        return AnomalyEventDetailResponse.builder()
                .id(event.getId())
                .targetType(event.getTargetType())
                .cameraId(camera != null ? camera.getCameraId() : null)
                .cameraName(camera != null ? camera.getCameraName() : null)
                .anomalyType(event.getAnomalyType())
                .severity(event.getSeverity())
                .status(event.getStatus())
                .detectionMethod(event.getDetectionMethod())
                .detector(detectorVersion == null ? null : AnomalyEventDetailResponse.Detector.builder()
                        .name(detectorVersion.getDetectorName())
                        .version(detectorVersion.getVersion())
                        .build())
                .policyCode(policy != null ? policy.getPolicyCode() : null)
                .baseline(AnomalyEventDetailResponse.Baseline.builder()
                        .source(event.getBaselineSource())
                        .from(toOffset(event.getBaselineFrom()))
                        .to(toOffset(event.getBaselineTo()))
                        .sampleCount(event.getBaselineSampleCount())
                        .build())
                .trend(AnomalyEventDetailResponse.Trend.builder()
                        .slope(event.getTrendSlope())
                        .confidence(event.getTrendConfidence())
                        .predictionHorizonMinutes(event.getPredictionHorizonMinutes())
                        .projectedThresholdCrossingAt(toOffset(event.getProjectedThresholdCrossingAt()))
                        .build())
                .suspectedCauses(toSuspectedCauses(event.getSuspectedCausesJson()))
                .evidence(evidence.stream().map(this::toEvidenceResponse).toList())
                .ticket(ticket == null ? null : AnomalyEventDetailResponse.Ticket.builder()
                        .id(ticket.getId())
                        .ticketNumber(ticket.getTicketNumber())
                        .priority(ticket.getPriority())
                        .status(ticket.getStatus())
                        .build())
                .shadowModel(shadowModel == null ? null : AnomalyEventDetailResponse.ShadowModel.builder()
                        .detectorName(shadowModel.getDetectorVersion().getDetectorName())
                        .version(shadowModel.getDetectorVersion().getVersion())
                        .operatingMode(shadowModel.getDetectorVersion().getOperatingMode())
                        .anomalyScore(shadowModel.getAnomalyScore())
                        .warningThreshold(shadowModel.getWarningThreshold())
                        .criticalThreshold(shadowModel.getCriticalThreshold())
                        .predictedAnomaly(shadowModel.isPredictedAnomaly())
                        .predictedSeverity(shadowModel.getPredictedSeverity())
                        .evaluatedAt(toOffset(shadowModel.getEvaluatedAt()))
                        .topFeatures(shadowModel.getTopFeaturesJson())
                        .build())
                .build();
    }

    private AnomalyEventDetailResponse.Evidence toEvidenceResponse(AnomalyEventEvidence evidence) {
        return AnomalyEventDetailResponse.Evidence.builder()
                .metricName(evidence.getMetricName())
                .observedValue(evidence.getObservedValue())
                .baselineValue(evidence.getBaselineValue())
                .thresholdValue(evidence.getThresholdValue())
                .metricScore(evidence.getMetricScore())
                .unit(evidence.getUnit())
                .sampledAt(toOffset(evidence.getSampledAt()))
                .context(evidence.getContextJson())
                .build();
    }

    private MaintenanceTicketResponse toTicketResponse(MaintenanceTicket ticket) {
        Member assignee = ticket.getAssignee();
        LocalDateTime now = LocalDateTime.now(PredictiveTimeUtils.SERVICE_ZONE);
        return MaintenanceTicketResponse.builder()
                .id(ticket.getId())
                .ticketNumber(ticket.getTicketNumber())
                .anomalyEventId(ticket.getAnomalyEvent().getId())
                .cameraId(ticket.getAnomalyEvent().getTargetCamera().getCameraId())
                .priority(ticket.getPriority())
                .status(ticket.getStatus())
                .assignee(assignee == null ? null : MaintenanceTicketResponse.Assignee.builder()
                        .memberId(assignee.getMemberId())
                        .name(assignee.getName())
                        .build())
                .dueAckAt(toOffset(ticket.getDueAckAt()))
                .dueStartAt(toOffset(ticket.getDueStartAt()))
                .ackOverdue(ticket.getAcknowledgedAt() == null
                        && ticket.getDueAckAt() != null
                        && now.isAfter(ticket.getDueAckAt()))
                .startOverdue(ticket.getStartedAt() == null
                        && ticket.getDueStartAt() != null
                        && now.isAfter(ticket.getDueStartAt()))
                .createdAt(toOffset(ticket.getCreatedAt()))
                .build();
    }

    private MaintenanceTicketHistoryResponse toTicketHistoryResponse(MaintenanceTicketHistory history) {
        Member changedBy = history.getChangedBy();
        return MaintenanceTicketHistoryResponse.builder()
                .id(history.getId())
                .fromStatus(history.getFromStatus())
                .toStatus(history.getToStatus())
                .changedBy(changedBy == null ? null : MaintenanceTicketHistoryResponse.ChangedBy.builder()
                        .memberId(changedBy.getMemberId())
                        .name(changedBy.getName())
                        .build())
                .note(history.getNote())
                .changedAt(toOffset(history.getChangedAt()))
                .build();
    }

    private AnomalyPolicyResponse toPolicyResponse(AnomalyPolicy policy) {
        return AnomalyPolicyResponse.builder()
                .policyCode(policy.getPolicyCode())
                .anomalyType(policy.getAnomalyType())
                .detectionMethod(policy.getDetectionMethod())
                .warningThreshold(policy.getWarningThreshold())
                .criticalThreshold(policy.getCriticalThreshold())
                .warningConsecutiveWindows(policy.getWarningConsecutiveWindows())
                .criticalConsecutiveWindows(policy.getCriticalConsecutiveWindows())
                .minimumSampleCount(policy.getMinimumSampleCount())
                .predictionHorizonMinutes(policy.getPredictionHorizonMinutes())
                .config(policy.getConfigJson())
                .enabled(policy.isEnabled())
                .updatedAt(toOffset(policy.getUpdatedAt()))
                .build();
    }

    private List<SuspectedCause> toSuspectedCauses(List<Object> rawValues) {
        if (rawValues == null || rawValues.isEmpty()) {
            return List.of();
        }
        List<SuspectedCause> causes = new ArrayList<>();
        for (Object rawValue : rawValues) {
            if (rawValue == null) {
                continue;
            }
            try {
                causes.add(SuspectedCause.valueOf(String.valueOf(rawValue)));
            } catch (IllegalArgumentException ignored) {
                // Keep the response contract enum-safe even if old JSON contains unknown values.
            }
        }
        return causes;
    }

    private OffsetDateTime toOffset(LocalDateTime value) {
        return PredictiveTimeUtils.toSeoulOffset(value);
    }

    private LocalDateTime toLocalDateTime(OffsetDateTime value) {
        return PredictiveTimeUtils.toLocalDateTime(value);
    }
}
