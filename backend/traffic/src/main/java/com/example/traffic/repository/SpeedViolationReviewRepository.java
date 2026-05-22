package com.example.traffic.repository;

import com.example.traffic.domain.SpeedViolation;
import com.example.traffic.domain.SpeedViolationReview;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface SpeedViolationReviewRepository extends JpaRepository<SpeedViolationReview, Long> {

    Optional<SpeedViolationReview> findFirstBySpeedViolationOrderByReviewedAtDescReviewIdDesc(
            SpeedViolation speedViolation
    );
}
