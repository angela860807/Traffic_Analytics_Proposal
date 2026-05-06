package com.example.traffic.dto.response;

import com.example.traffic.domain.Post;
import lombok.Getter;

import java.time.LocalDateTime;
import java.util.List;

@Getter
public class PostResponse {
    private final Long postId;
    private final String title;
    private final String content;
    private final String authorName;
    private final int viewCount;
    private final LocalDateTime createdAt;
    private final LocalDateTime updatedAt;
    private final List<CommentResponse> comments; // ⬅️ 1. 필드 추가

    // ⬅️ 2. 이 생성자를 기존 것 대신 넣거나 새로 만드세요.
    public PostResponse(Post post, List<CommentResponse> comments) {
        this.postId = post.getPostId();
        this.title = post.getTitle();
        this.content = post.getContent();
        this.authorName = post.getAuthor().getName();
        this.viewCount = post.getViewCount();
        this.createdAt = post.getCreatedAt();
        this.updatedAt = post.getUpdatedAt();
        this.comments = comments; // ⬅️ 전달받은 리스트 저장
    }

    // (선택) 기존 에러 방지용 기본 생성자
    public PostResponse(Post post) {
        this(post, null);
    }
}