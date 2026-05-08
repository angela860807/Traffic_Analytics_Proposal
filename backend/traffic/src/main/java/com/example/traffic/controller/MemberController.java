package com.example.traffic.controller;

import com.example.traffic.dto.request.LoginRequest;
import com.example.traffic.dto.request.SignupRequest;
import com.example.traffic.dto.response.CommonResponse;
import com.example.traffic.dto.response.MemberResponse;
import com.example.traffic.dto.response.TokenResponse;
import com.example.traffic.service.MemberService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class MemberController {

    private final MemberService memberService;

    /**
     * 회원가입 API
     */
    @PostMapping("/signup")
    public ResponseEntity<CommonResponse<MemberResponse>> signup(@Valid @RequestBody SignupRequest request) {
        MemberResponse response = memberService.signup(request);
        return ResponseEntity.ok(CommonResponse.success(response, "회원가입이 완료되었습니다."));
    }

    /**
     * 로그인 API
     */
    @PostMapping("/login")
    public ResponseEntity<CommonResponse<TokenResponse>> login(@Valid @RequestBody LoginRequest request) {
        TokenResponse response = memberService.login(request);
        return ResponseEntity.ok(CommonResponse.success(response, "로그인에 성공하였습니다."));
    }
    /**
     * 로그아웃 API
     * JWT 방식은 클라이언트가 토큰을 삭제하는 것이 기본이지만,
     * 서버에서도 성공 응답을 내려주어 프론트엔드가 토큰을 지울 수 있게 합니다.
     */
    @PostMapping("/logout")
    public ResponseEntity<CommonResponse<String>> logout() {
        // 향후 Redis를 사용한다면 여기서 토큰을 블랙리스트에 등록하는 로직을 추가할 수 있습니다.
        return ResponseEntity.ok(CommonResponse.success(null, "로그아웃 되었습니다."));
    }

    /**
     * 내 정보 조회 API (인증 테스트용)
     * 이 API는 SecurityConfig 설정에 따라 Header에 유효한 토큰이 있어야만 접근 가능합니다.
     */
    @GetMapping("/me/{id}")
    public ResponseEntity<CommonResponse<MemberResponse>> getMyInfo(@PathVariable Long id) {
        MemberResponse response = memberService.getMemberById(id);
        return ResponseEntity.ok(CommonResponse.success(response, "조회 성공"));
    }
}
