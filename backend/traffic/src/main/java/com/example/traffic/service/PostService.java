package com.example.traffic.service;

import com.example.traffic.common.enums.UserRole;
import com.example.traffic.domain.Member;
import com.example.traffic.domain.Post;
import com.example.traffic.dto.request.PostRequest;
import com.example.traffic.dto.response.CommentResponse;
import com.example.traffic.dto.response.PostResponse;
import com.example.traffic.etc.BusinessException;
import com.example.traffic.repository.MemberRepository;
import com.example.traffic.repository.PostRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class PostService {

    private final PostRepository postRepository;
    private final MemberRepository memberRepository;
    private final CommentService commentService;

    /**
     * 게시글 등록
     */
    @Transactional
    public PostResponse createPost(PostRequest request, String email) {
        // 1. 작성자(Member) 조회
        Member member = memberRepository.findByEmail(email)
                .orElseThrow(() -> new BusinessException("존재하지 않는 회원입니다.", HttpStatus.NOT_FOUND));

        // 2. Post 엔티티 생성 및 저장
        Post post = Post.builder()
                .author(member)
                .title(request.getTitle())
                .content(request.getContent())
                .build();

        postRepository.save(post);

        return new PostResponse(post, null);
    }

    /**
     * 게시글 전체 조회 (최신순)
     */
    public List<PostResponse> getAllPosts() {
        return postRepository.findAllByOrderByCreatedAtDesc().stream()
                .map(post -> new PostResponse(post, null))
                .collect(Collectors.toList());
    }

    /**
     * 게시글 상세 조회 (조회수 증가 포함)
     */
    @Transactional
    public PostResponse getPostById(Long postId) {
        Post post = postRepository.findById(postId)
                .orElseThrow(() -> new BusinessException("존재하지 않는 게시글입니다.", HttpStatus.NOT_FOUND));

        post.incrementViewCount();

        // ✅ 해당 게시글의 댓글 목록을 가져옴
        List<CommentResponse> comments = commentService.getCommentsByPost(postId);

        // ✅ 게시글 정보와 댓글 정보를 함께 DTO로 변환
        return new PostResponse(post, comments);
    }

    /**
     * 게시글 삭제 (작성자 본인 또는 관리자)
     */
    @Transactional
    public void deletePost(Long postId, String email) {
        Post post = postRepository.findById(postId)
                .orElseThrow(() -> new BusinessException("존재하지 않는 게시글입니다.", HttpStatus.NOT_FOUND));

        Member member = memberRepository.findByEmail(email)
                .orElseThrow(() -> new BusinessException("존재하지 않는 회원입니다.", HttpStatus.NOT_FOUND));

        // 권한 체크: 본인도 아니고 관리자도 아니라면 403 예외 발생[cite: 20]
        if (!post.getAuthor().getEmail().equals(email) && member.getRole() != UserRole.ADMIN) {
            throw new BusinessException("삭제 권한이 없습니다.", HttpStatus.FORBIDDEN);
        }

        postRepository.delete(post);
    }

    /**
     * 게시글 수정 (작성자 본인만 - 보통 수정은 관리자라도 타인의 글은 건드리지 않음)
     */
    @Transactional
    public void updatePost(Long postId, PostRequest request, String email) {
        Post post = postRepository.findById(postId)
                .orElseThrow(() -> new BusinessException("존재하지 않는 게시글입니다.", HttpStatus.NOT_FOUND));

        // 수정 권한 체크[cite: 20]
        if (!post.getAuthor().getEmail().equals(email)) {
            throw new BusinessException("수정 권한이 없습니다.", HttpStatus.FORBIDDEN);
        }

        post.update(request.getTitle(), request.getContent());
    }
}
