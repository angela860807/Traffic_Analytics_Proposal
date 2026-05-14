package com.example.traffic.etc;

import com.example.traffic.dto.response.ErrorResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.util.stream.Collectors;

@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {

    /**
     * [수정 가이드 3번] @Valid 검증 실패 처리 [cite: 14]
     * 컨트롤러 진입 전 DTO 유효성 검사 실패 시 발생합니다.
     */
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponse> handleValidationException(MethodArgumentNotValidException e) {
        String errorMessage = e.getBindingResult().getFieldErrors().stream()
                .map(error -> String.format("[%s: %s]", error.getField(), error.getDefaultMessage()))
                .collect(Collectors.joining(", "));

        log.error("Validation Error (400): {}", errorMessage);
        return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                .body(new ErrorResponse("INVALID_INPUT", errorMessage));
    }

    /**
     * [핵심 수정] BusinessException 통합 처리
     * README에 명시된 대로 모든 비즈니스 로직 오류 및 AI 서버 연동 오류(502)를 처리합니다.
     * IllegalStateException이나 IllegalArgumentException은 서비스 레이어에서
     * BusinessException으로 래핑해서 던지는 것을 원칙으로 합니다.
     */
    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<ErrorResponse> handleBusinessException(BusinessException e) {
        // AI 서버 응답 오류(502 Bad Gateway) 로그 특화 [cite: 8]
        if (e.getHttpStatus() == HttpStatus.BAD_GATEWAY) {
            log.error("AI Server Integration Error (502): {}", e.getMessage());
        } else {
            log.error("Business Logic Error: {}", e.getMessage());
        }

        return ResponseEntity.status(e.getHttpStatus())
                .body(new ErrorResponse("BUSINESS_ERROR", e.getMessage()));
    }

    /**
     * [수정 가이드 2번] JSON 형식 및 데이터 바인딩 오류 처리 [cite: 14]
     */
    @ExceptionHandler(HttpMessageNotReadableException.class)
    public ResponseEntity<ErrorResponse> handleJsonException(HttpMessageNotReadableException e) {
        log.error("JSON Parsing Error: {}", e.getMessage());
        return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                .body(new ErrorResponse("INVALID_JSON", "요청 데이터 형식이 올바르지 않거나 필수 값이 누락되었습니다."));
    }

    @ExceptionHandler(BadCredentialsException.class)
    public ResponseEntity<ErrorResponse> handleBadCredentialsException(BadCredentialsException e) {
        log.warn("Authentication failed: {}", e.getMessage());
        return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                .body(new ErrorResponse("AUTHENTICATION_FAILED", "이메일 또는 비밀번호가 올바르지 않습니다."));
    }

    /**
     * [보안/안전] 정의되지 않은 모든 예외 처리 [cite: 14]
     * 500 에러가 외부로 노출되지 않도록 서버 내부 오류로 치환합니다.
     */
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleAllException(Exception e) {
        log.error("Unexpected System Error (500): ", e);
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(new ErrorResponse("SERVER_ERROR", "서버 내부 오류가 발생했습니다."));
    }
}
