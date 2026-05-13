package com.example.traffic.domain;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Table(name = "notices")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Notice {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long noticeId;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "author_id", nullable = false)
    private Member author;

    @Column(nullable = false, length = 200)
    private String title;

    @Column(nullable = false, columnDefinition = "TEXT")
    private String content;

    @Column(nullable = false)
    private boolean isPinned = false; // DEFAULT FALSE

    @Column(nullable = false)
    private int viewCount = 0; // DEFAULT 0

    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;

    @Builder
    public Notice(Member author, String title, String content, boolean isPinned) {
        this.author = author;
        this.title = title;
        this.content = content;
        this.isPinned = isPinned;
        this.viewCount = 0;
        this.createdAt = LocalDateTime.now(); // 기존 도메인들과 동일한 방식
    }

    // 수정 시 updatedAt 갱신
    public void update(String title, String content, boolean isPinned) {
        this.title = title;
        this.content = content;
        this.isPinned = isPinned;
        this.updatedAt = LocalDateTime.now();
    }

    // 조회수 증가
    public void incrementViewCount() {
        this.viewCount++;
    }
}