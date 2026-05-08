package com.example.traffic.common.enums;

import com.example.traffic.etc.BusinessException;
import lombok.Getter;
import org.springframework.http.HttpStatus;

@Getter
public enum QnaStatus {
    OPEN("답변대기"),
    ANSWERED("답변완료"),
    CLOSED("종료");

    private final String description;

    QnaStatus(String description) {
        this.description = description;
    }

    // 추가: 안전한 변환 메서드[cite: 11]
    public static QnaStatus of(String value) {
        if (value == null || value.isBlank()) {
            return OPEN;
        }
        try {
            return QnaStatus.valueOf(value.toUpperCase());
        } catch (IllegalArgumentException e) {
            throw new BusinessException("잘못된 QnA 상태 값입니다: " + value, HttpStatus.BAD_REQUEST);
        }
    }
}