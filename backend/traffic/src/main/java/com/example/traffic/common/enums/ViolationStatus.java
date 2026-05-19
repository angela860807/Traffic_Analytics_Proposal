package com.example.traffic.common.enums;

import lombok.Getter;

@Getter
public enum ViolationStatus {
    UNPROCESSED("미처리"),
    NOTIFIED("고지완료"),
    CLOSED("종결");

    private final String description;

    ViolationStatus(String description) {
        this.description = description;
    }
}
