package com.example.traffic.service;

import com.example.traffic.common.enums.UserRole;
import com.example.traffic.domain.Member;
import com.example.traffic.dto.request.LoginRequest;
import com.example.traffic.dto.request.SignupRequest;
import com.example.traffic.dto.response.MemberResponse;
import com.example.traffic.dto.response.TokenResponse;
import com.example.traffic.etc.BusinessException;
import com.example.traffic.security.JwtTokenProvider;
import com.example.traffic.repository.MemberRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.config.annotation.authentication.builders.AuthenticationManagerBuilder;
import org.springframework.security.core.Authentication;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class MemberService {

    private final MemberRepository memberRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtTokenProvider jwtTokenProvider;
    private final AuthenticationManagerBuilder authenticationManagerBuilder;

    /**
     * [회원가입] 이메일/전화번호 중복 체크 및 BCrypt 암호화 저장
     */
    @Transactional
    public MemberResponse signup(SignupRequest request) {
        // 1. 중복 체크 로직
        if (memberRepository.existsByEmail(request.getEmail())) {
            throw new BusinessException("이미 사용 중인 이메일입니다.", HttpStatus.CONFLICT);
        }
        if (memberRepository.existsByPhone(request.getPhone())) {
            throw new BusinessException("이미 등록된 전화번호입니다.", HttpStatus.CONFLICT);
        }

        // 2. 비밀번호 암호화 후 엔티티 생성 및 저장
        Member member = Member.builder()
                .email(request.getEmail())
                .password(passwordEncoder.encode(request.getPassword()))
                .name(request.getName())
                .phone(request.getPhone())
                .role(UserRole.USER)
                .build();

        return MemberResponse.from(memberRepository.save(member));
    }

    /**
     * [로그인] 인증 및 JWT 토큰 발급
     */
    @Transactional
    public TokenResponse login(LoginRequest request) {
        // 1. 이메일/비밀번호 기반으로 AuthenticationToken 생성
        UsernamePasswordAuthenticationToken authenticationToken =
                new UsernamePasswordAuthenticationToken(request.getEmail(), request.getPassword());

        // 2. 실제 검증 (비밀번호 체크 포함)
        // 이 과정에서 CustomUserDetailsService가 호출됩니다.
        Authentication authentication = authenticationManagerBuilder.getObject().authenticate(authenticationToken);

        // 3. 인증 성공 시 JWT 토큰 발급[cite: 8]
        TokenResponse tokenResponse = jwtTokenProvider.createToken(authentication);

        // 4. 최근 접속 시각 갱신
        Member member = memberRepository.findByEmail(request.getEmail())
                .orElseThrow(() -> new BusinessException("사용자를 찾을 수 없습니다.", HttpStatus.NOT_FOUND));
        member.updateLastLogin();

        return tokenResponse;
    }

    /**
     * [회원 정보 조회] ID로 회원 상세 정보 가져오기
     */
    public MemberResponse getMemberById(Long memberId) {
        Member member = memberRepository.findById(memberId)
                .orElseThrow(() -> new BusinessException("존재하지 않는 회원입니다.", HttpStatus.NOT_FOUND));
        return MemberResponse.from(member);
    }
}