package com.example.traffic.repository;

import com.example.traffic.domain.AnomalyEventEvidence;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface AnomalyEventEvidenceRepository extends JpaRepository<AnomalyEventEvidence, Long> {

    List<AnomalyEventEvidence> findByAnomalyEvent_IdOrderBySampledAtDescIdDesc(Long anomalyEventId);
}
