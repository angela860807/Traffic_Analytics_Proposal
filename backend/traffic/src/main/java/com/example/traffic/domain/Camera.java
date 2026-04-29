package com.example.traffic.domain;

import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Table(name = "cameras")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Camera {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long cameraId;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "zone_id", nullable = false)
    private Zone zone;

    @Column(nullable = false, unique = true, length = 30)
    private String cameraCode;

    @Column(nullable = false, length = 100)
    private String cameraName;

    @Column(length = 255)
    private String streamUrl;

    @Column(nullable = false, length = 20)
    private String directionType;

    @Column(nullable = false)
    private boolean isActive;

    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    public void update(String cameraName, String cameraCode, String streamUrl, String directionType, boolean isActive) {
        this.cameraName = cameraName;
        this.cameraCode = cameraCode;
        this.streamUrl = streamUrl;
        this.directionType = directionType;
        this.isActive = isActive;
    }

    @Builder
    public Camera(Zone zone, String cameraCode, String cameraName, String streamUrl, String directionType) {
        this.zone = zone;
        this.cameraCode = cameraCode;
        this.cameraName = cameraName;
        this.streamUrl = streamUrl;
        this.directionType = directionType;
        this.isActive = true;
        this.createdAt = LocalDateTime.now();
    }
}
