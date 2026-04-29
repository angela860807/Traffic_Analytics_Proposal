package com.example.traffic.domain;

import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "detection_logs")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class DetectionLog {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long logId;

    private Camera camera;

    private Vehicle vehicle;

    private String plateNumber;

    private String detectionType;


}
