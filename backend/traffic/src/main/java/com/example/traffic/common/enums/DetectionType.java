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
            // AI가 잘못된 값을 보낸 것이므로 400 에러가 더 적절합니다.
            throw new BusinessException("잘못된 탐지 타입입니다: " + value, HttpStatus.BAD_REQUEST);
        }
    }
}