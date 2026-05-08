package com.example.traffic.dto.response;

import com.example.traffic.common.enums.UserRole;
import com.example.traffic.domain.Member;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;

import java.time.LocalDateTime;

@Getter
@Builder
@AllArgsConstructor
public class MemberResponse {
    private Long memberId;
    private String email;
    private String name;
    private String phone;
    private UserRole role;
    private LocalDateTime lastLoginAt;

    // Entity를 Response DTO로 변환하는 정적 팩토리 메서드
    public static MemberResponse from(Member member) {
        return MemberResponse.builder()
                .memberId(member.getMemberId())
                .email(member.getEmail())
                .name(member.getName())
                .phone(member.getPhone())
                .role(member.getRole())
                .lastLoginAt(member.getLastLoginAt())
                .build();
    }
}