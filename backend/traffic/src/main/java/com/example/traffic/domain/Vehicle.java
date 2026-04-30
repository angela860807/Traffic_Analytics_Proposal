package com.example.traffic.domain;

import com.example.traffic.common.enums.VehicleStatus;
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

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private VehicleStatus vehicleStatus;

    private LocalDateTime firstDetectedAt;

    private LocalDateTime lastDetectedAt;

    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

     // 추가: 차량 정보 수정을 위한 메서드
     public void updateStatus(VehicleStatus vehicleStatus) {
         this.vehicleStatus = vehicleStatus;
         this.lastDetectedAt = LocalDateTime.now();
     }

    // 기존: 마지막 탐지 시간만 갱신하는 메서드
    public void updateLastDetectedAt() {
        this.lastDetectedAt = LocalDateTime.now();
    }

    @Builder
    public Vehicle(String plateNumber, VehicleStatus vehicleStatus) {
        this.plateNumber = plateNumber;
        // Enum 기준으로 기본값 설정
        this.vehicleStatus = (vehicleStatus != null) ? vehicleStatus : VehicleStatus.ACTIVE;
        this.firstDetectedAt = LocalDateTime.now();
        this.lastDetectedAt = LocalDateTime.now();
        this.createdAt = LocalDateTime.now();
    }
}