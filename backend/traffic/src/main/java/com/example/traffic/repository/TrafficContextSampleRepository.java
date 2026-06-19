package com.example.traffic.repository;

import com.example.traffic.domain.TrafficContextSample;
import org.springframework.data.jpa.repository.JpaRepository;

public interface TrafficContextSampleRepository extends JpaRepository<TrafficContextSample, Long> {
}
