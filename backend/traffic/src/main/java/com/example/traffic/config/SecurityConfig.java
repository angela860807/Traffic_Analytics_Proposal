package com.example.traffic.config;

import com.example.traffic.security.CustomUserDetailsService;
import com.example.traffic.security.JwtAuthenticationFilter;
import com.example.traffic.security.JwtTokenProvider;

import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

@Configuration
@EnableWebSecurity
@RequiredArgsConstructor
public class SecurityConfig {

    private final JwtTokenProvider jwtTokenProvider;
    private final CustomUserDetailsService customUserDetailsService;

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
                .csrf(AbstractHttpConfigurer::disable)
                .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
                .authorizeHttpRequests(auth -> auth
                        .requestMatchers("/api/auth/**").permitAll()
                        .requestMatchers("/v3/api-docs/**", "/swagger-ui/**", "/swagger-ui.html").permitAll()

                        // [추가] AI 서버 탐지 로그 전송 API: JWT 인증 제외
                        // 대신 Controller에서 X-Internal-Api-Key로 보안 처리함
                        .requestMatchers(HttpMethod.POST, "/api/v1/detection-logs").permitAll()

                        // 공지사항 권한
                        .requestMatchers(HttpMethod.GET, "/api/notices/**").permitAll()
                        .requestMatchers("/api/notices/**").hasRole("ADMIN")

                        // 게시글 권한
                        .requestMatchers(HttpMethod.GET, "/api/posts/**").permitAll() // 목록/상세 조회는 누구나 가능

                        // QnA 권한 중앙 제어
                        .requestMatchers(HttpMethod.GET, "/api/qna/**").permitAll() // 목록/상세 조가는 누구나 가능
                        .requestMatchers(HttpMethod.POST, "/api/qna/questions/*/answers").hasRole("ADMIN") // 답변 작성은 관리자만
                        .requestMatchers("/api/qna/**").authenticated() // 그 외(질문 등록/삭제 등)는 인증된 사용자만

                        .anyRequest().authenticated()
                )
                .addFilterBefore(new JwtAuthenticationFilter(jwtTokenProvider, customUserDetailsService),
                        UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }
}