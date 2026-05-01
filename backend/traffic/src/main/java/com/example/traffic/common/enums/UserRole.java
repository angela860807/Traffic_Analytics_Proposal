package com.example.traffic.common.enums;

import lombok.Getter;

@Getter
public enum UserRole {
    USER("일반사용자"),
    ADMIN("관리자");

    private final String description;

    UserRole(String description) {
        this.description = description;
    }
}