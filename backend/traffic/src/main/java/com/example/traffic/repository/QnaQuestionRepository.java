package com.example.traffic.repository;

import com.example.traffic.common.enums.QnaStatus;
import com.example.traffic.domain.QnaQuestion;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface QnaQuestionRepository extends JpaRepository<QnaQuestion, Long> {
    // 상태별 최신순 조회 (인덱스: idx_qna_q_status 활용)[cite: 1]
    List<QnaQuestion> findAllByStatusOrderByCreatedAtDesc(QnaStatus status);

    // 전체 최신순 조회[cite: 9]
    List<QnaQuestion> findAllByOrderByCreatedAtDesc();
}