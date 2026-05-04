package com.example.traffic.common.enums;

import com.example.traffic.etc.BusinessException;
import lombok.Getter;
import org.springframework.http.HttpStatus;

@Getter
public enum UserStatus {
    ACTIVE("활성"),
    INACTIVE("비활성"),
    BANNED("정지");

    private final String description;

    UserStatus(String description) {
        this.description = description;
    }

    // 추가: 안전한 변환 메서드
    public static UserStatus of(String value) {
        if (value == null || value.isBlank()) {
            return ACTIVE; // 기본값
        }
        try {
            return UserStatus.valueOf(value.toUpperCase());
        } catch (IllegalArgumentException e) {
            throw new BusinessException("잘못된 유저 상태 값입니다: " + value, HttpStatus.BAD_REQUEST);
        }
    }
}