package com.example.traffic.dto.response;

import com.example.traffic.common.enums.QnaStatus;
import com.example.traffic.domain.QnaQuestion;
import lombok.Getter;

import java.time.LocalDateTime;

@Getter
public class QnaQuestionResponse {
    private final Long questionId;
    private final String title;
    private final String content;
    private final String authorName;
    private final QnaStatus status;
    private final LocalDateTime createdAt;

    // 질문 상세 조회 시 함께 보여줄 답변 데이터 (없으면 null)
    private QnaAnswerResponse answer;

    public QnaQuestionResponse(QnaQuestion question) {
        this.questionId = question.getQuestionId();
        this.title = question.getTitle();
        this.content = question.getContent();
        this.authorName = question.getAuthor().getName();
        this.status = question.getStatus();
        this.createdAt = question.getCreatedAt();
    }

    // 답변 정보를 세팅하기 위한 메서드
    public void setAnswer(QnaAnswerResponse answer) {
        this.answer = answer;
    }
}