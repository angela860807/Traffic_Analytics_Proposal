package com.example.traffic.controller;

import com.example.traffic.dto.request.CommentRequest;
import com.example.traffic.dto.response.CommonResponse;
import com.example.traffic.dto.response.CommentResponse;
import com.example.traffic.service.CommentService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/comments") // 경로를 단순화하여 관리
@RequiredArgsConstructor
public class CommentController {

    private final CommentService commentService;

    /**
     * 댓글 등록
     * NoticeController와 동일하게 생성된 댓글의 ID(Long)를 반환하도록 맞춤
     */
    @PostMapping("/post/{postId}")
    public ResponseEntity<CommonResponse<Long>> createComment(
            @PathVariable Long postId,
            @Valid @RequestBody CommentRequest request,
            @AuthenticationPrincipal UserDetails userDetails) {

        // 서비스에서 CommentResponse 대신 ID를 반환하도록 살짝 수정하거나,
        // 여기서 response.getCommentId()를 추출하여 반환합니다.
        Long commentId = commentService.createComment(postId, request, userDetails.getUsername()).getCommentId();
        return ResponseEntity.ok(CommonResponse.success(commentId, "댓글이 등록되었습니다."));
    }

    /**
     * 특정 게시글의 댓글 목록 조회
     */
    @GetMapping("/post/{postId}")
    public ResponseEntity<CommonResponse<List<CommentResponse>>> getCommentList(@PathVariable Long postId) {
        return ResponseEntity.ok(CommonResponse.success(commentService.getCommentsByPost(postId), "댓글 목록 조회 성공"));
    }

    /**
     * 댓글 삭제
     * NoticeController의 삭제 방식(Void 반환)을 따름
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<CommonResponse<Void>> deleteComment(
            @PathVariable Long id,
            @AuthenticationPrincipal UserDetails userDetails) {

        commentService.deleteComment(id, userDetails.getUsername());
        return ResponseEntity.ok(CommonResponse.success(null, "댓글이 삭제되었습니다."));
    }
}