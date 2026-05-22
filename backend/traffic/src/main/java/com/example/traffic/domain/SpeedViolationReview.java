package com.example.traffic.domain;

import com.example.traffic.common.enums.ViolationStatus;
import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Table(
        name = "speed_violation_reviews",
        indexes = {
                @Index(name = "idx_speed_violation_reviews_violation", columnList = "violation_id"),
                @Index(name = "idx_speed_violation_reviews_reviewed_at", columnList = "reviewed_at")
        }
)
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class SpeedViolationReview {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "review_id")
    private Long reviewId;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "violation_id", nullable = false)
    private SpeedViolation speedViolation;

    @Enumerated(EnumType.STRING)
    @Column(name = "from_status", nullable = false, length = 20)
    private ViolationStatus fromStatus;

    @Enumerated(EnumType.STRING)
    @Column(name = "to_status", nullable = false, length = 20)
    private ViolationStatus toStatus;

    @Column(length = 120)
    private String reason;

    @Column(length = 500)
    private String memo;

    @Column(name = "reviewed_by", length = 80)
    private String reviewedBy;

    @Column(name = "reviewed_at", nullable = false)
    private LocalDateTime reviewedAt;

    @Builder
    public SpeedViolationReview(SpeedViolation speedViolation,
                                ViolationStatus fromStatus,
                                ViolationStatus toStatus,
                                String reason,
                                String memo,
                                String reviewedBy,
                                LocalDateTime reviewedAt) {
        this.speedViolation = speedViolation;
        this.fromStatus = fromStatus;
        this.toStatus = toStatus;
        this.reason = normalize(reason);
        this.memo = normalize(memo);
        this.reviewedBy = normalize(reviewedBy);
        this.reviewedAt = reviewedAt != null ? reviewedAt : LocalDateTime.now();
    }

    private String normalize(String value) {
        if (value == null || value.isBlank()) {
            return null;
        }
        return value.trim();
    }
}
