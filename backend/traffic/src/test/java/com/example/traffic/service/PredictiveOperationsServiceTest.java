package com.example.traffic.service;

import com.example.traffic.common.enums.MaintenancePriority;
import com.example.traffic.common.enums.MaintenanceStatus;
import com.example.traffic.common.enums.UserRole;
import com.example.traffic.domain.MaintenanceTicket;
import com.example.traffic.domain.MaintenanceTicketHistory;
import com.example.traffic.domain.Member;
import com.example.traffic.dto.request.predictive.MaintenanceTicketAssignRequest;
import com.example.traffic.etc.BusinessException;
import com.example.traffic.repository.*;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.core.Authentication;
import org.springframework.test.util.ReflectionTestUtils;

import java.time.LocalDateTime;
import java.util.Collection;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class PredictiveOperationsServiceTest {

    @Mock
    private AnomalyEventRepository anomalyEventRepository;
    @Mock
    private AnomalyEventEvidenceRepository evidenceRepository;
    @Mock
    private MaintenanceTicketRepository maintenanceTicketRepository;
    @Mock
    private MaintenanceTicketHistoryRepository ticketHistoryRepository;
    @Mock
    private ModelPredictionLogRepository modelPredictionLogRepository;
    @Mock
    private AnomalyPolicyRepository anomalyPolicyRepository;
    @Mock
    private MemberRepository memberRepository;
    @Mock
    private MaintenanceTicketStateTransitionService ticketStateTransitionService;
    @Mock
    private org.springframework.jdbc.core.JdbcTemplate jdbcTemplate;
    @Mock
    private Authentication authentication;

    @InjectMocks
    private PredictiveOperationsService service;

    @Test
    @SuppressWarnings("unchecked")
    void getAssigneesOnlyQueriesAssignableRoles() {
        Member admin = member(2L, "admin@email.com", "관리자", UserRole.ADMIN);
        when(memberRepository.findByRoleInOrderByRoleAscNameAsc(anyCollection()))
                .thenReturn(List.of(admin));

        var responses = service.getAssignees(List.of(UserRole.USER, UserRole.ADMIN));

        ArgumentCaptor<Collection<UserRole>> rolesCaptor = ArgumentCaptor.forClass(Collection.class);
        verify(memberRepository).findByRoleInOrderByRoleAscNameAsc(rolesCaptor.capture());
        assertThat(rolesCaptor.getValue()).containsExactly(UserRole.ADMIN);
        assertThat(responses).hasSize(1);
        assertThat(responses.get(0).getMemberId()).isEqualTo(2L);
        assertThat(responses.get(0).getRole()).isEqualTo(UserRole.ADMIN);
    }

    @Test
    void assignMaintenanceTicketRejectsUserRoleAssignee() {
        Member operator = member(3L, "ops@email.com", "운영자", UserRole.OPERATOR);
        Member user = member(1L, "user@email.com", "이용자", UserRole.USER);
        MaintenanceTicket ticket = MaintenanceTicket.builder()
                .ticketNumber("MNT-20260622-0001")
                .priority(MaintenancePriority.P1)
                .status(MaintenanceStatus.OPEN)
                .build();

        when(authentication.getName()).thenReturn(operator.getEmail());
        when(memberRepository.findByEmail(operator.getEmail())).thenReturn(Optional.of(operator));
        when(maintenanceTicketRepository.findById(501L)).thenReturn(Optional.of(ticket));
        when(memberRepository.findById(1L)).thenReturn(Optional.of(user));

        MaintenanceTicketAssignRequest request = new MaintenanceTicketAssignRequest();
        ReflectionTestUtils.setField(request, "assigneeId", 1L);
        ReflectionTestUtils.setField(request, "note", "USER 배정 차단 검증");

        assertThatThrownBy(() -> service.assignMaintenanceTicket(501L, request, authentication))
                .isInstanceOf(BusinessException.class)
                .hasMessageContaining("Assignee role is not assignable");

        verify(ticketHistoryRepository, never()).save(any());
    }

    @Test
    void getMaintenanceTicketHistoriesMapsAppendOnlyRows() {
        MaintenanceTicket ticket = MaintenanceTicket.builder()
                .ticketNumber("MNT-20260622-0002")
                .priority(MaintenancePriority.P1)
                .status(MaintenanceStatus.ASSIGNED)
                .build();
        Member admin = member(2L, "admin@email.com", "관리자", UserRole.ADMIN);
        MaintenanceTicketHistory history = MaintenanceTicketHistory.builder()
                .maintenanceTicket(ticket)
                .fromStatus(MaintenanceStatus.OPEN)
                .toStatus(MaintenanceStatus.ASSIGNED)
                .changedBy(admin)
                .note("담당자 배정")
                .changedAt(LocalDateTime.of(2026, 6, 22, 10, 30))
                .build();
        ReflectionTestUtils.setField(history, "id", 9L);

        when(maintenanceTicketRepository.findById(501L)).thenReturn(Optional.of(ticket));
        when(ticketHistoryRepository.findByMaintenanceTicket_IdOrderByChangedAtAscIdAsc(501L))
                .thenReturn(List.of(history));

        var responses = service.getMaintenanceTicketHistories(501L);

        assertThat(responses).hasSize(1);
        assertThat(responses.get(0).getId()).isEqualTo(9L);
        assertThat(responses.get(0).getFromStatus()).isEqualTo(MaintenanceStatus.OPEN);
        assertThat(responses.get(0).getToStatus()).isEqualTo(MaintenanceStatus.ASSIGNED);
        assertThat(responses.get(0).getChangedBy().getMemberId()).isEqualTo(2L);
        assertThat(responses.get(0).getNote()).isEqualTo("담당자 배정");
    }

    private Member member(Long id, String email, String name, UserRole role) {
        Member member = Member.builder()
                .email(email)
                .password("encoded")
                .name(name)
                .phone("010%08d".formatted(id))
                .role(role)
                .build();
        ReflectionTestUtils.setField(member, "memberId", id);
        return member;
    }
}
