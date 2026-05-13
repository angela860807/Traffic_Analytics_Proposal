package com.example.traffic.dto.response;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;

@Getter
@Builder
@AllArgsConstructor
public class TokenResponse {
    private String grantType;      // 보통 "Bearer" 사용
    private String accessToken;    // API 요청용
    private String refreshToken;   // 토큰 재발급용
    private Long accessTokenExpiresIn; // 만료 시간
}
