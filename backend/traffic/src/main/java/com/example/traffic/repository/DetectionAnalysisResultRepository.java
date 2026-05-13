package com.example.traffic.repository;

import com.example.traffic.domain.DetectionAnalysisResult;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface DetectionAnalysisResultRepository extends JpaRepository<DetectionAnalysisResult, Long> {

    // 로그별 최신 분석 결과 조회
    Optional<DetectionAnalysisResult> findFirstByDetectionLog_LogIdOrderByAttemptNoDesc(Long logId);

    // 차량 번호 검색용 조회
    List<DetectionAnalysisResult> findByPlateNumberOrderByCreatedAtDesc(String plateNumber);
}
