package com.example.traffic.domain;

import com.example.traffic.common.enums.UserRole;
import com.example.traffic.common.enums.UserStatus;
import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.ColumnDefault;
import org.hibernate.annotations.DynamicInsert;

import java.time.LocalDateTime;

@Entity
@Table(name = "members")
@Getter
@DynamicInsert // 필드 값이 null인 경우 DDL의 DEFAULT 값을 사용하도록 설정
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Member {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "member_id")
    private Long memberId;

    @Column(nullable = false, unique = true, length = 100)
    private String email;

    @Column(nullable = false, length = 255) // BCrypt 암호화 길이에 맞춤
    private String password;

    @Column(nullable = false, length = 50)
    private String name;

    @Column(nullable = false, unique = true, length = 20)
    private String phone;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    @ColumnDefault("'USER'") // DB 레벨의 기본값 명시
    private UserRole role;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    @ColumnDefault("'ACTIVE'") // DB 레벨의 기본값 명시
    private UserStatus status;

    @Column(name = "last_login_at")
    private LocalDateTime lastLoginAt;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Builder
    public Member(String email, String password, String name, String phone, UserRole role, UserStatus status) {
        this.email = email;
        this.password = password;
        this.name = name;
        this.phone = phone;
        this.role = (role != null) ? role : UserRole.USER;
        this.status = (status != null) ? status : UserStatus.ACTIVE;
    }

    /**
     * 저장 전 자동 날짜 할당
     */
    @PrePersist
    public void prePersist() {
        this.createdAt = LocalDateTime.now();
    }

    public void updateLastLogin() {
        this.lastLoginAt = LocalDateTime.now();
    }
}