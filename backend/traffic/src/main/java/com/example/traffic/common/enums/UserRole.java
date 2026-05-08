package com.example.traffic.common.enums;

import com.example.traffic.etc.BusinessException;
import lombok.Getter;
import org.springframework.http.HttpStatus;

@Getter
public enum UserRole {
    USER("이용자"),
    ADMIN("관리자");

    private final String description;

    UserRole(String description) {
        this.description = description;
    }

    // 추가: 안전한 변환 메서드
    public static UserRole of(String value) {
        if (value == null || value.isBlank()) {
            return USER; // 기본값 설정
        }
        try {
            return UserRole.valueOf(value.toUpperCase());
        } catch (IllegalArgumentException e) {
            throw new BusinessException("존재하지 않는 권한입니다: " + value, HttpStatus.BAD_REQUEST);
        }
    }
}