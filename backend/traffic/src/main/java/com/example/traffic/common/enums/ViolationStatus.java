package com.example.traffic.common.enums;

import lombok.Getter;

@Getter
public enum ViolationStatus {
    UNPROCESSED("Pending review"),
    NOTIFIED("Speed violation confirmed"),
    REJECTED("Rejected as non-violation"),
    CLOSED("Closed");

    private final String description;

    ViolationStatus(String description) {
        this.description = description;
    }
}
