package com.example.traffic.service;

import com.example.traffic.common.enums.UserRole;
import com.example.traffic.domain.Comment;
import com.example.traffic.domain.Member;
import com.example.traffic.domain.Post;
import com.example.traffic.dto.request.CommentRequest;
import com.example.traffic.dto.response.CommentResponse;
import com.example.traffic.etc.BusinessException;
import com.example.traffic.repository.CommentRepository;
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
public class CommentService {

    private final CommentRepository commentRepository;
    private final PostRepository postRepository;
    private final MemberRepository memberRepository;

    /**
     * 댓글 등록
     */
    @Transactional
    public CommentResponse createComment(Long postId, CommentRequest request, String email) {
        Post post = postRepository.findById(postId)
                .orElseThrow(() -> new BusinessException("존재하지 않는 게시글입니다.", HttpStatus.NOT_FOUND));

        Member member = memberRepository.findByEmail(email)
                .orElseThrow(() -> new BusinessException("존재하지 않는 회원입니다.", HttpStatus.NOT_FOUND));

        Comment comment = Comment.builder()
                .post(post)
                .author(member)
                .content(request.getContent())
                .build();

        commentRepository.save(comment);
        return new CommentResponse(comment);
    }

    /**
     * 특정 게시글의 댓글 목록 조회
     */
    public List<CommentResponse> getCommentsByPost(Long postId) {
        return commentRepository.findAllByPostPostIdOrderByCreatedAtAsc(postId).stream()
                .map(CommentResponse::new)
                .collect(Collectors.toList());
    }

    /**
     * 댓글 삭제 (작성자 본인 또는 관리자)
     */
    @Transactional
    public void deleteComment(Long commentId, String email) {
        Comment comment = commentRepository.findById(commentId)
                .orElseThrow(() -> new BusinessException("존재하지 않는 댓글입니다.", HttpStatus.NOT_FOUND));

        Member member = memberRepository.findByEmail(email)
                .orElseThrow(() -> new BusinessException("존재하지 않는 회원입니다.", HttpStatus.NOT_FOUND));

        // 권한 체크: 본인 또는 관리자
        if (!comment.getAuthor().getEmail().equals(email) && member.getRole() != UserRole.ADMIN) {
            throw new BusinessException("삭제 권한이 없습니다.", HttpStatus.FORBIDDEN);
        }

        commentRepository.delete(comment);
    }
}
