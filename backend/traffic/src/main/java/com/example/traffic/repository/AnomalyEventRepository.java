package com.example.traffic.repository;

import com.example.traffic.domain.AnomalyEvent;
import org.springframework.data.jpa.repository.JpaRepository;

public interface AnomalyEventRepository extends JpaRepository<AnomalyEvent, Long> {
}
