package com.example.traffic.controller;

import com.example.traffic.dto.request.PostRequest;
import com.example.traffic.dto.response.CommonResponse;
import com.example.traffic.dto.response.PostResponse;
import com.example.traffic.service.PostService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/posts")
@RequiredArgsConstructor
public class PostController {

    private final PostService postService;

    /**
     * 게시글 등록
     * NoticeController 스타일: 생성된 ID(Long) 반환
     */
    @PostMapping
    public ResponseEntity<CommonResponse<Long>> createPost(
            @Valid @RequestBody PostRequest request,
            @AuthenticationPrincipal UserDetails userDetails) {

        // PostResponse에서 ID만 추출하거나 Service 리턴타입 변경 고려
        Long postId = postService.createPost(request, userDetails.getUsername()).getPostId();
        return ResponseEntity.ok(CommonResponse.success(postId, "게시글이 등록되었습니다."));
    }

    /**
     * 게시글 목록 조회
     * NoticeController 스타일: getPostList로 명명[cite: 19]
     */
    @GetMapping
    public ResponseEntity<CommonResponse<List<PostResponse>>> getPostList() {
        return ResponseEntity.ok(CommonResponse.success(postService.getAllPosts(), "게시글 목록 조회 성공"));
    }

    /**
     * 게시글 상세 조회
     * NoticeController 스타일: getPostDetail로 명명[cite: 19]
     */
    @GetMapping("/{id}")
    public ResponseEntity<CommonResponse<PostResponse>> getPostDetail(@PathVariable Long id) {
        return ResponseEntity.ok(CommonResponse.success(postService.getPostById(id), "게시글 상세 조회 성공"));
    }

    /**
     * 게시글 수정
     */
    @PutMapping("/{id}")
    public ResponseEntity<CommonResponse<Void>> updatePost(
            @PathVariable Long id,
            @Valid @RequestBody PostRequest request,
            @AuthenticationPrincipal UserDetails userDetails) {
        postService.updatePost(id, request, userDetails.getUsername());
        return ResponseEntity.ok(CommonResponse.success(null, "게시글이 수정되었습니다."));
    }

    /**
     * 게시글 삭제
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<CommonResponse<Void>> deletePost(
            @PathVariable Long id,
            @AuthenticationPrincipal UserDetails userDetails) {
        postService.deletePost(id, userDetails.getUsername());
        return ResponseEntity.ok(CommonResponse.success(null, "게시글이 삭제되었습니다."));
    }
}