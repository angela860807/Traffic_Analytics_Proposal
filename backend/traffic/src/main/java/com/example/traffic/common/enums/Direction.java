package com.example.traffic.common.enums;

import com.example.traffic.etc.BusinessException;
import lombok.Getter;
import org.springframework.http.HttpStatus;

@Getter
public enum Direction {
    IN("진입"),
    OUT("진출"),
    BOTH("양방향");

    private final String description;

    Direction(String description) {
        this.description = description;
    }

    public static Direction of(String value) {
        if (value == null || value.isBlank()) return BOTH;
        try {
            return Direction.valueOf(value.toUpperCase());
        } catch (IllegalArgumentException e) {
            // [2-2 반영] 일반 예외가 아닌 502 성격의 BusinessException으로 명확하게 던짐
            throw new BusinessException("잘못된 방향 값입니다: " + value, HttpStatus.BAD_GATEWAY);
        }
    }
}