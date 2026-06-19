package com.example.traffic.domain;

import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(
        name = "camera_links",
        uniqueConstraints = @UniqueConstraint(
                name = "uq_camera_links_upstream_downstream_direction",
                columnNames = {"upstream_camera_id", "downstream_camera_id", "direction"}
        )
)
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class CameraLink {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "upstream_camera_id", nullable = false)
    private Camera upstreamCamera;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "downstream_camera_id", nullable = false)
    private Camera downstreamCamera;

    @Column(nullable = false, length = 50)
    private String direction;

    @Column(name = "expected_travel_time_seconds", nullable = false)
    private Integer expectedTravelTimeSeconds;

    @Column(name = "expected_flow_ratio", precision = 7, scale = 6)
    private BigDecimal expectedFlowRatio;

    @Column(name = "tolerance_ratio", precision = 7, scale = 6)
    private BigDecimal toleranceRatio;

    @Column(nullable = false)
    private boolean enabled;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;

    @Builder
    public CameraLink(Camera upstreamCamera, Camera downstreamCamera, String direction,
                      Integer expectedTravelTimeSeconds, BigDecimal expectedFlowRatio,
                      BigDecimal toleranceRatio, Boolean enabled) {
        this.upstreamCamera = upstreamCamera;
        this.downstreamCamera = downstreamCamera;
        this.direction = direction;
        this.expectedTravelTimeSeconds = expectedTravelTimeSeconds;
        this.expectedFlowRatio = expectedFlowRatio;
        this.toleranceRatio = toleranceRatio;
        this.enabled = enabled == null || enabled;
        this.createdAt = LocalDateTime.now();
        this.updatedAt = this.createdAt;
    }
}
