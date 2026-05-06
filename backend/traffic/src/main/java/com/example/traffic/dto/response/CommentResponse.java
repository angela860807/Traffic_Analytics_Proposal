package com.example.traffic.dto.response;

import com.example.traffic.domain.Comment;
import lombok.Getter;

import java.time.LocalDateTime;

@Getter
public class CommentResponse {
    private final Long commentId;
    private final String content;
    private final String authorName;
    private final LocalDateTime createdAt;
    private final LocalDateTime updatedAt;

    public CommentResponse(Comment comment) {
        this.commentId = comment.getCommentId();
        this.content = comment.getContent();
        this.authorName = comment.getAuthor().getName();
        this.createdAt = comment.getCreatedAt();
        this.updatedAt = comment.getUpdatedAt();
    }
}
