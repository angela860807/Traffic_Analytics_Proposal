package com.example.traffic.repository;

import com.example.traffic.domain.AnomalyEventEvidence;
import org.springframework.data.jpa.repository.JpaRepository;

public interface AnomalyEventEvidenceRepository extends JpaRepository<AnomalyEventEvidence, Long> {
}
