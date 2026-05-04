package com.example.traffic.common.enums;

import com.example.traffic.etc.BusinessException;
import lombok.Getter;
import org.springframework.http.HttpStatus;

@Getter
public enum DetectionType {
    VEHICLE("차량"),
    PLATE("번호판");

    private final String description;

    DetectionType(String description) {
        this.description = description;
    }

    public static DetectionType of(String value) {
        if (value == null || value.isBlank()) return VEHICLE;
        try {
            return DetectionType.valueOf(value.toUpperCase());
        } catch (IllegalArgumentException e) {
            // AI 탐지 결과와 직결되므로 502 처리
            throw new BusinessException("잘못된 탐지 타입입니다: " + value, HttpStatus.BAD_GATEWAY);
        }
    }
}