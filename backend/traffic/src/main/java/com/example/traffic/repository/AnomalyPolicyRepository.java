package com.example.traffic.repository;

import com.example.traffic.domain.AnomalyPolicy;
import org.springframework.data.jpa.repository.JpaRepository;

public interface AnomalyPolicyRepository extends JpaRepository<AnomalyPolicy, Long> {
}
