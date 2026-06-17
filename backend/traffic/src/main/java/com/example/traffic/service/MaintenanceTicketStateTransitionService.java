package com.example.traffic.service;

import com.example.traffic.common.enums.MaintenanceStatus;
import com.example.traffic.common.enums.UserRole;
import com.example.traffic.etc.BusinessException;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;

import java.util.Set;

@Service
public class MaintenanceTicketStateTransitionService {

    public void validateTransition(MaintenanceStatus fromStatus, MaintenanceStatus toStatus, UserRole role, String note) {
        if (!canTransition(fromStatus, toStatus)) {
            throw new BusinessException("Invalid maintenance ticket status transition.", HttpStatus.CONFLICT);
        }
        if (!hasPermission(fromStatus, toStatus, role)) {
            throw new BusinessException("Permission denied for maintenance ticket status transition.", HttpStatus.FORBIDDEN);
        }
        if (MaintenanceStatus.RESOLVED.equals(toStatus) && (note == null || note.isBlank())) {
            throw new BusinessException("Resolution note is required.", HttpStatus.BAD_REQUEST);
        }
    }

    public boolean canTransition(MaintenanceStatus fromStatus, MaintenanceStatus toStatus) {
        if (fromStatus == null || toStatus == null) {
            return false;
        }
        return switch (fromStatus) {
            case OPEN -> MaintenanceStatus.ASSIGNED.equals(toStatus);
            case ASSIGNED -> MaintenanceStatus.IN_PROGRESS.equals(toStatus);
            case IN_PROGRESS -> MaintenanceStatus.RESOLVED.equals(toStatus);
            case RESOLVED -> MaintenanceStatus.CLOSED.equals(toStatus);
            case CLOSED -> false;
        };
    }

    public boolean hasPermission(MaintenanceStatus fromStatus, MaintenanceStatus toStatus, UserRole role) {
        if (role == null || fromStatus == null || toStatus == null) {
            return false;
        }
        if (!canTransition(fromStatus, toStatus)) {
            return false;
        }

        Set<UserRole> allowedRoles = switch (toStatus) {
            case ASSIGNED, CLOSED -> Set.of(UserRole.OPERATOR, UserRole.ADMIN);
            case IN_PROGRESS, RESOLVED -> Set.of(UserRole.OPERATOR, UserRole.MAINTAINER, UserRole.ADMIN);
            case OPEN -> Set.of();
        };
        return allowedRoles.contains(role);
    }
}
