package com.example.traffic.domain;

import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Table(name = "zones")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Zone {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long zoneId;

    @Column(nullable = false, unique = true, length = 30)
    private String zoneCode;

    @Column(nullable = false, length = 100)
    private String zoneName;

    @Column(nullable = false, length = 30)
    private String zoneType;

    @Column(nullable = false)
    private boolean isActive;

    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    public void update(String zoneName, String zoneCode, String zoneType, boolean isActive) {
        this.zoneName = zoneName;
        this.zoneCode = zoneCode;
        this.zoneType = zoneType;
        this.isActive = isActive;
    }

    @Builder
    public Zone(String zoneCode, String zoneName, String zoneType) {
        this.zoneCode = zoneCode;
        this.zoneName = zoneName;
        this.zoneType = zoneType;
        this.isActive = true;
        this.createdAt = LocalDateTime.now();
    }
}
