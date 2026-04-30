package com.example.traffic.service;

import com.example.traffic.domain.DetectionLog;
import com.example.traffic.repository.DetectionLogRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@Transactional(readOnly = true)
@RequiredArgsConstructor
public class DetectionLogService {

    private final DetectionLogRepository detectionLogRepository;

    // 1. 로그 등록 (AI 서버에서 탐지 결과를 보낼 때 사용)
    @Transactional
    public DetectionLog saveLog(DetectionLog log) {
        return detectionLogRepository.save(log);
    }

    // 2. 전체 로그 조회
    public List<DetectionLog> findAllLogs() {
        return detectionLogRepository.findAll();
    }

    // 3. 카메라별 로그 조회
    public List<DetectionLog> findLogsByCamera(Long cameraId) {
        return detectionLogRepository.findByCameraCameraId(cameraId);
    }

    // 4. 로그 삭제 (오탐 데이터 삭제 시 사용)
    @Transactional
    public void deleteLog(Long id) {
        if (!detectionLogRepository.existsById(id)) {
            throw new IllegalArgumentException("해당 로그가 존재하지 않습니다. id=" + id);
        }
        detectionLogRepository.deleteById(id);
    }
}
