package com.example.traffic.repository;

import com.example.traffic.domain.ModelPredictionLog;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ModelPredictionLogRepository extends JpaRepository<ModelPredictionLog, Long> {
}
