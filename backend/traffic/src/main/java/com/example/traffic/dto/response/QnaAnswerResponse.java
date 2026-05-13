package com.example.traffic.dto.response;

import com.example.traffic.domain.QnaAnswer;
import lombok.Getter;

import java.time.LocalDateTime;

@Getter
public class QnaAnswerResponse {
    private final Long answerId;
    private final String content;
    private final String authorName; // 답변 작성자(관리자) 이름
    private final LocalDateTime createdAt;

    public QnaAnswerResponse(QnaAnswer answer) {
        this.answerId = answer.getAnswerId();
        this.content = answer.getContent();
        this.authorName = answer.getAuthor().getName();
        this.createdAt = answer.getCreatedAt();
    }
}
