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
    private String plateNumber;

    @Column(nullable = false, length = 20)
    private String vehicleStatus;

    private LocalDateTime firstDetectedAt;

    private LocalDateTime lastDetectedAt;

    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Builder
    public Vehicle(String plateNumber, String vehicleStatus) {
        this.plateNumber = plateNumber;
        this.vehicleStatus = (vehicleStatus != null) ? vehicleStatus : "ACTIVE";
        this.firstDetectedAt = LocalDateTime.now();
        this.lastDetectedAt = LocalDateTime.now();
        this.createdAt = LocalDateTime.now();
    }

    public void updateLastDetectedAt() {
        this.lastDetectedAt = LocalDateTime.now();
    }
}
