package com.example.traffic.etc;

import com.example.traffic.dto.response.ErrorResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {

    // 0. 피드백 2-2, 2-3, 2-8: 커스텀 비즈니스 예외 처리 (추가됨)
    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<ErrorResponse> handleBusinessException(BusinessException e) {
        log.error("Business Exception: {}", e.getMessage());
        return ResponseEntity.status(e.getHttpStatus()) // 502 Bad Gateway 등이 그대로 적용됨
                .body(new ErrorResponse("BUSINESS_ERROR", e.getMessage()));
    }

    // 1. 피드백 2-2, 2-8: Enum 변환 실패 및 잘못된 인자 전달 처리
    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<ErrorResponse> handleIllegalArgumentException(IllegalArgumentException e) {
        log.error("Invalid Argument: {}", e.getMessage());
        return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                .body(new ErrorResponse("INVALID_INPUT", e.getMessage()));
    }

    // 2. 피드백 2-8: 데이터 충돌 및 잘못된 상태 요청 처리
    @ExceptionHandler(IllegalStateException.class)
    public ResponseEntity<ErrorResponse> handleIllegalStateException(IllegalStateException e) {
        log.error("Illegal State: {}", e.getMessage());
        return ResponseEntity.status(HttpStatus.CONFLICT)
                .body(new ErrorResponse("CONFLICT", e.getMessage()));
    }

    // 3. 피드백 2-8: JSON 형식 오류 처리
    @ExceptionHandler(HttpMessageNotReadableException.class)
    public ResponseEntity<ErrorResponse> handleJsonException(HttpMessageNotReadableException e) {
        log.error("JSON Parsing Error: {}", e.getMessage());
        return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                .body(new ErrorResponse("INVALID_JSON", "요청 데이터 형식이 올바르지 않습니다."));
    }

    // 4. 모든 예외에 대한 최후의 보루
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleAllException(Exception e) {
        log.error("Internal Server Error: ", e);
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(new ErrorResponse("SERVER_ERROR", "서버 내부 오류가 발생했습니다."));
    }
}