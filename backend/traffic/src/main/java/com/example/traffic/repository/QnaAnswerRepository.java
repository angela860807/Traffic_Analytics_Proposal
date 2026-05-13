package com.example.traffic.repository;

import com.example.traffic.domain.QnaAnswer;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface QnaAnswerRepository extends JpaRepository<QnaAnswer, Long> {
    // 특정 질문에 달린 답변 조회 (1:1 관계)
    Optional<QnaAnswer> findByQuestionQuestionId(Long questionId);

    // 답변 존재 여부 확인 (중복 등록 방지용)
    boolean existsByQuestionQuestionId(Long questionId);
}