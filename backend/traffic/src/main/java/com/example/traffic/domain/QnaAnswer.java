package com.example.traffic.domain;

import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Table(name = "qna_answers")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class QnaAnswer {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "answer_id")
    private Long answerId;

    // 질문 하나에 답변 하나 (UNIQUE 제약)
    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "question_id", nullable = false, unique = true)
    private QnaQuestion question;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "author_id", nullable = false)
    private Member author; // 답변자는 ADMIN[cite: 1]

    @Column(nullable = false, columnDefinition = "TEXT")
    private String content;

    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;

    @Builder
    public QnaAnswer(QnaQuestion question, Member author, String content) {
        this.question = question;
        this.author = author;
        this.content = content;
        this.createdAt = LocalDateTime.now();
    }
}
