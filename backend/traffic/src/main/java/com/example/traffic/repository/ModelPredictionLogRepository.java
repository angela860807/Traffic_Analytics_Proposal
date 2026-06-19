package com.example.traffic.repository;

import com.example.traffic.domain.ModelPredictionLog;
import com.example.traffic.common.enums.DataSourceType;
import org.springframework.data.jpa.repository.JpaRepository;

import java.time.LocalDateTime;
import java.util.Optional;

public interface ModelPredictionLogRepository extends JpaRepository<ModelPredictionLog, Long> {

    boolean existsByCamera_CameraIdAndDetectorVersion_IdAndEvaluatedAt(
            Long cameraId,
            Long detectorVersionId,
            LocalDateTime evaluatedAt
    );

    Optional<ModelPredictionLog> findFirstByCamera_CameraIdAndDataSourceOrderByEvaluatedAtDesc(
            Long cameraId,
            DataSourceType dataSource
    );
}
