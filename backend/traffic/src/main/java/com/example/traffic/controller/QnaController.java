package com.example.traffic.controller;

import com.example.traffic.dto.request.QnaAnswerRequest;
import com.example.traffic.dto.request.QnaQuestionRequest;
import com.example.traffic.dto.response.CommonResponse;
import com.example.traffic.dto.response.QnaQuestionResponse;
import com.example.traffic.service.QnaService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/qna")
@RequiredArgsConstructor
public class QnaController {

    private final QnaService qnaService;

    // 질문 등록
    @PostMapping("/questions")
    public ResponseEntity<CommonResponse<Long>> createQuestion(
            @RequestBody QnaQuestionRequest request,
            @AuthenticationPrincipal UserDetails userDetails) {
        Long id = qnaService.createQuestion(request, userDetails.getUsername());
        return ResponseEntity.ok(CommonResponse.success(id, "질문이 등록되었습니다."));
    }

    // 질문 목록 조회
    @GetMapping("/questions")
    public ResponseEntity<CommonResponse<List<QnaQuestionResponse>>> getQuestionList() {
        return ResponseEntity.ok(CommonResponse.success(qnaService.getQuestionList(), "목록 조회 성공"));
    }

    // 질문 상세 조회 (답변 포함)
    @GetMapping("/questions/{id}")
    public ResponseEntity<CommonResponse<QnaQuestionResponse>> getQuestion(@PathVariable Long id) {
        return ResponseEntity.ok(CommonResponse.success(qnaService.getQuestionDetail(id), "상세 조회 성공"));
    }

    // 답변 등록 (ADMIN 권한은 Security에서 체크)
    @PostMapping("/questions/{id}/answers")
    public ResponseEntity<CommonResponse<Long>> createAnswer(
            @PathVariable Long id,
            @RequestBody QnaAnswerRequest request,
            @AuthenticationPrincipal UserDetails userDetails) {
        Long answerId = qnaService.createAnswer(id, request, userDetails.getUsername());
        return ResponseEntity.ok(CommonResponse.success(answerId, "답변이 등록되었습니다."));
    }

    // 질문 삭제
    @DeleteMapping("/questions/{id}")
    public ResponseEntity<CommonResponse<Void>> deleteQuestion(
            @PathVariable Long id,
            @AuthenticationPrincipal UserDetails userDetails) {
        qnaService.deleteQuestion(id, userDetails.getUsername());
        return ResponseEntity.ok(CommonResponse.success(null, "질문이 삭제되었습니다."));
    }
}