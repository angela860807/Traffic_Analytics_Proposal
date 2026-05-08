package com.example.traffic.dto.response;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public class CommonResponse<T> {
    private boolean success; // 성공 여부 (true/false)
    private T data;          // 실제 응답 데이터 (List, Object 등)
    private String message;  // 응답 메시지

    // 성공 응답 정적 팩토리 메서드
    public static <T> CommonResponse<T> success(T data) {
        return new CommonResponse<>(true, data, "요청이 성공적으로 처리되었습니다.");
    }

    // 메시지를 커스텀하고 싶을 때 사용하는 메서드
    public static <T> CommonResponse<T> success(T data, String message) {
        return new CommonResponse<>(true, data, message);
    }
}