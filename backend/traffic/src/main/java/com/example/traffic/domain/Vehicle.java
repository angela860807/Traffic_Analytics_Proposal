package com.example.traffic.domain;

import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Table(name = "vehicles")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Vehicle {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long vehicleId;

    @Column(nullable = false, unique = true, length = 20)
    private String plateNumber; // 차량 번호판

    @Column(nullable = false, length = 20)
    private String vehicleStatus; // 차량 상태 (정상, 도난, 수배 등)

    private LocalDateTime firstDetectedAt;

    private LocalDateTime lastDetectedAt;

    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    // 추가: 차량 정보 수정을 위한 메서드
    public void update(String vehicleStatus) {
        this.vehicleStatus = vehicleStatus;
        this.lastDetectedAt = LocalDateTime.now();
    }

    // 기존: 마지막 탐지 시간만 갱신하는 메서드
    public void updateLastDetectedAt() {
        this.lastDetectedAt = LocalDateTime.now();
    }

    @Builder
    public Vehicle(String plateNumber, String vehicleStatus) {
        this.plateNumber = plateNumber;
        this.vehicleStatus = (vehicleStatus != null) ? vehicleStatus : "ACTIVE";
        this.firstDetectedAt = LocalDateTime.now();
        this.lastDetectedAt = LocalDateTime.now();
        this.createdAt = LocalDateTime.now();
    }
}