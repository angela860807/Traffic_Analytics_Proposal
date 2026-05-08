package com.example.traffic.common.enums;

import com.example.traffic.etc.BusinessException;
import lombok.Getter;
import org.springframework.http.HttpStatus;

@Getter
public enum VehicleStatus {
    ACTIVE("정상"),
    STOLEN("도난"),
    WANTED("수배");

    private final String description;

    VehicleStatus(String description) {
        this.description = description;
    }

    public static VehicleStatus of(String value) {
        if (value == null || value.isBlank()) return ACTIVE;
        try {
            return VehicleStatus.valueOf(value.toUpperCase());
        } catch (IllegalArgumentException e) {
            throw new BusinessException("잘못된 차량 상태 값입니다: " + value, HttpStatus.BAD_REQUEST);
        }
    }
}