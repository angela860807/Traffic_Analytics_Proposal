package com.example.traffic.common.enums;

import lombok.Getter;

@Getter
public enum QnaStatus {
    OPEN("답변대기"),
    ANSWERED("답변완료"),
    CLOSED("종료");

    private final String description;

    QnaStatus(String description) {
        this.description = description;
    }
}
