package com.example.traffic.service;

import com.example.traffic.common.enums.QnaStatus;
import com.example.traffic.domain.Member;
import com.example.traffic.domain.QnaAnswer;
import com.example.traffic.domain.QnaQuestion;
import com.example.traffic.dto.request.QnaAnswerRequest;
import com.example.traffic.dto.request.QnaQuestionRequest;
import com.example.traffic.dto.response.QnaAnswerResponse;
import com.example.traffic.dto.response.QnaQuestionResponse;
import com.example.traffic.etc.BusinessException;
import com.example.traffic.repository.MemberRepository;
import com.example.traffic.repository.QnaAnswerRepository;
import com.example.traffic.repository.QnaQuestionRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class QnaService {

    private final QnaQuestionRepository questionRepository;
    private final QnaAnswerRepository answerRepository;
    private final MemberRepository memberRepository;

    /**
     * 질문 등록 (Notice 스타일: ID 반환)
     */
    @Transactional
    public Long createQuestion(QnaQuestionRequest request, String email) {
        Member author = memberRepository.findByEmail(email)
                .orElseThrow(() -> new BusinessException("사용자를 찾을 수 없습니다.", HttpStatus.NOT_FOUND));

        QnaQuestion question = QnaQuestion.builder()
                .author(author)
                .title(request.getTitle())
                .content(request.getContent())
                .status(QnaStatus.OPEN) // 생성 시점에 명시적으로 '답변대기' 상태 부여
                .build();

        return questionRepository.save(question).getQuestionId();
    }

    /**
     * 질문 목록 조회
     */
    public List<QnaQuestionResponse> getQuestionList() {
        return questionRepository.findAllByOrderByCreatedAtDesc().stream()
                .map(QnaQuestionResponse::new)
                .collect(Collectors.toList());
    }

    /**
     * 질문 상세 조회 (답변 포함)
     */
    public QnaQuestionResponse getQuestionDetail(Long id) {
        QnaQuestion question = questionRepository.findById(id)
                .orElseThrow(() -> new BusinessException("질문을 찾을 수 없습니다.", HttpStatus.NOT_FOUND));

        QnaQuestionResponse response = new QnaQuestionResponse(question);

        // 1:1 관계인 답변이 존재하면 함께 세팅[cite: 1, 11]
        answerRepository.findByQuestionQuestionId(id).ifPresent(answer ->
                response.setAnswer(new QnaAnswerResponse(answer))
        );

        return response;
    }

    /**
     * 답변 등록 (ADMIN 전용)
     */
    @Transactional
    public Long createAnswer(Long questionId, QnaAnswerRequest request, String email) {
        QnaQuestion question = questionRepository.findById(questionId)
                .orElseThrow(() -> new BusinessException("질문을 찾을 수 없습니다.", HttpStatus.NOT_FOUND));

        // 이미 답변이 존재하는지 체크 (1:1 제약 조건)[cite: 1]
        if (answerRepository.existsByQuestionQuestionId(questionId)) {
            throw new BusinessException("이미 답변이 등록된 질문입니다.", HttpStatus.BAD_REQUEST);
        }

        Member admin = memberRepository.findByEmail(email)
                .orElseThrow(() -> new BusinessException("사용자를 찾을 수 없습니다.", HttpStatus.NOT_FOUND));

        QnaAnswer answer = QnaAnswer.builder()
                .question(question)
                .author(admin)
                .content(request.getContent())
                .build();

        // 질문 상태를 ANSWERED로 자동 변경
        question.completeAnswer();

        return answerRepository.save(answer).getAnswerId();
    }

    /**
     * 질문 삭제 (Notice 스타일: Void 반환)[cite: 17]
     */
    @Transactional
    public void deleteQuestion(Long id, String email) {
        QnaQuestion question = questionRepository.findById(id)
                .orElseThrow(() -> new BusinessException("질문을 찾을 수 없습니다.", HttpStatus.NOT_FOUND));

        // 1. 본인 글 권한 체크
        if (!question.getAuthor().getEmail().equals(email)) {
            throw new BusinessException("삭제 권한이 없습니다.", HttpStatus.FORBIDDEN);
        }

        // 2. [추가] 답변 완료 상태 체크 (QnaStatus 활용)
        // 이미 답변이 완료된 질문은 삭제할 수 없게 하거나, 별도의 정책을 적용합니다.
        if (question.getStatus() == QnaStatus.ANSWERED) {
            throw new BusinessException("이미 답변이 완료된 질문은 삭제할 수 없습니다.", HttpStatus.BAD_REQUEST);
        }

        questionRepository.delete(question);
    }
}
