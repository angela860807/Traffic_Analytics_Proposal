package com.example.traffic.common.enums;

import com.example.traffic.etc.BusinessException;
import lombok.Getter;
import org.springframework.http.HttpStatus;

@Getter
public enum ZoneType {
    ENTRY("진입구역"),
    EXIT("진출구역"),
    INTERNAL("내부구역");

    private final String description;

    ZoneType(String description) {
        this.description = description;
    }

    public static ZoneType of(String value) {
        if (value == null || value.isBlank()) return INTERNAL;
        try {
            return ZoneType.valueOf(value.toUpperCase());
        } catch (IllegalArgumentException e) {
            throw new BusinessException("잘못된 구역 타입입니다: " + value, HttpStatus.BAD_REQUEST);
        }
    }
}