package com.example.traffic.controller;

import com.example.traffic.common.enums.UserRole;
import com.example.traffic.dto.request.predictive.*;
import com.example.traffic.dto.response.predictive.*;
import com.example.traffic.service.PredictiveOperationsService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/v1/predictive")
public class PredictiveOperationsController {

    private final PredictiveOperationsService predictiveOperationsService;

    @GetMapping("/anomaly-events")
    public PageResponse<AnomalyEventSummaryResponse> getAnomalyEvents(
            @Valid @ModelAttribute AnomalyEventSearchRequest request) {
        return predictiveOperationsService.getAnomalyEvents(request);
    }

    @GetMapping("/anomaly-events/{eventId}")
    public AnomalyEventDetailResponse getAnomalyEvent(@PathVariable Long eventId) {
        return predictiveOperationsService.getAnomalyEvent(eventId);
    }

    @PostMapping("/anomaly-events/{eventId}/acknowledge")
    public AnomalyEventDetailResponse acknowledgeAnomalyEvent(
            @PathVariable Long eventId,
            @Valid @RequestBody AnomalyAcknowledgeRequest request,
            Authentication authentication) {
        return predictiveOperationsService.acknowledgeAnomalyEvent(eventId, request, authentication);
    }

    @PostMapping("/anomaly-events/{eventId}/resolve")
    public AnomalyEventDetailResponse resolveAnomalyEvent(
            @PathVariable Long eventId,
            @Valid @RequestBody AnomalyResolveRequest request,
            Authentication authentication) {
        return predictiveOperationsService.resolveAnomalyEvent(eventId, request, authentication);
    }

    @PostMapping("/anomaly-events/{eventId}/dismiss")
    public AnomalyEventDetailResponse dismissAnomalyEvent(
            @PathVariable Long eventId,
            @Valid @RequestBody AnomalyDismissRequest request,
            Authentication authentication) {
        return predictiveOperationsService.dismissAnomalyEvent(eventId, request, authentication);
    }

    @GetMapping("/maintenance-tickets")
    public PageResponse<MaintenanceTicketResponse> getMaintenanceTickets(
            @Valid @ModelAttribute MaintenanceTicketSearchRequest request) {
        return predictiveOperationsService.getMaintenanceTickets(request);
    }

    @GetMapping("/assignees")
    public List<PredictiveAssigneeResponse> getAssignees(
            @RequestParam(required = false) String roles) {
        List<UserRole> parsedRoles = roles == null || roles.isBlank()
                ? List.of()
                : java.util.Arrays.stream(roles.split(","))
                .map(String::trim)
                .filter(role -> !role.isBlank())
                .map(UserRole::of)
                .toList();
        return predictiveOperationsService.getAssignees(parsedRoles);
    }

    @GetMapping("/maintenance-tickets/{ticketId}/histories")
    public List<MaintenanceTicketHistoryResponse> getMaintenanceTicketHistories(
            @PathVariable Long ticketId) {
        return predictiveOperationsService.getMaintenanceTicketHistories(ticketId);
    }

    @PostMapping("/maintenance-tickets")
    public MaintenanceTicketResponse createMaintenanceTicket(
            @Valid @RequestBody MaintenanceTicketCreateRequest request,
            Authentication authentication) {
        return predictiveOperationsService.createMaintenanceTicket(request, authentication);
    }

    @PostMapping("/maintenance-tickets/{ticketId}/assign")
    public MaintenanceTicketResponse assignMaintenanceTicket(
            @PathVariable Long ticketId,
            @Valid @RequestBody MaintenanceTicketAssignRequest request,
            Authentication authentication) {
        return predictiveOperationsService.assignMaintenanceTicket(ticketId, request, authentication);
    }

    @PostMapping("/maintenance-tickets/{ticketId}/status")
    public MaintenanceTicketResponse changeMaintenanceTicketStatus(
            @PathVariable Long ticketId,
            @Valid @RequestBody MaintenanceTicketStatusRequest request,
            Authentication authentication) {
        return predictiveOperationsService.changeMaintenanceTicketStatus(ticketId, request, authentication);
    }

    @PatchMapping("/policies/{policyCode}")
    public AnomalyPolicyResponse updatePolicy(
            @PathVariable String policyCode,
            @Valid @RequestBody AnomalyPolicyUpdateRequest request,
            Authentication authentication) {
        return predictiveOperationsService.updatePolicy(policyCode, request, authentication);
    }
}
