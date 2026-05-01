package com.example.traffic.common.enums;

import lombok.Getter;

@Getter
public enum UserStatus {
    ACTIVE("활성"),
    INACTIVE("비활성"),
    BANNED("정지");

    private final String description;

    UserStatus(String description) {
        this.description = description;
    }
}
