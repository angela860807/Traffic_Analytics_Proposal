package com.example.traffic.domain;

import com.example.traffic.common.enums.QnaStatus;
import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Table(name = "qna_questions")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class QnaQuestion {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "question_id")
    private Long questionId;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "author_id", nullable = false)
    private Member author;

    @Column(nullable = false, length = 200)
    private String title;

    @Column(nullable = false, columnDefinition = "TEXT")
    private String content;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private QnaStatus status = QnaStatus.OPEN; // 기본값 OPEN

    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;

    @Builder
    public QnaQuestion(Member author, String title, String content, QnaStatus status) {
        this.author = author;
        this.title = title;
        this.content = content;
        this.status = (status != null) ? status : QnaStatus.OPEN;
        this.createdAt = LocalDateTime.now();
    }

    // 답변 등록 시 상태 변경 로직
    public void completeAnswer() {
        this.status = QnaStatus.ANSWERED;
        this.updatedAt = LocalDateTime.now();
    }
}
