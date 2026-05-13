package com.example.traffic.dto.response;

import com.example.traffic.domain.Notice;
import lombok.Getter;

import java.time.LocalDateTime;

@Getter
public class NoticeResponse {
    private Long noticeId;
    private String title;
    private String content;
    private String authorName;
    private boolean isPinned;
    private int viewCount;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    public NoticeResponse(Notice notice) {
        this.noticeId = notice.getNoticeId();
        this.title = notice.getTitle();
        this.content = notice.getContent();
        this.authorName = notice.getAuthor().getName();
        this.isPinned = notice.isPinned();
        this.viewCount = notice.getViewCount();
        this.createdAt = notice.getCreatedAt();
        this.updatedAt = notice.getUpdatedAt();
    }
}
