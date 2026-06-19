package com.example.traffic.repository;

import com.example.traffic.domain.AnomalyPolicy;
import com.example.traffic.common.enums.DetectionMethod;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface AnomalyPolicyRepository extends JpaRepository<AnomalyPolicy, Long> {

    List<AnomalyPolicy> findByEnabledOrderByPolicyCodeAsc(boolean enabled);

    List<AnomalyPolicy> findAllByOrderByPolicyCodeAsc();

    List<AnomalyPolicy> findByDetectionMethodAndEnabledOrderByPolicyCodeAsc(
            DetectionMethod detectionMethod,
            boolean enabled
    );

    Optional<AnomalyPolicy> findByPolicyCode(String policyCode);
}
