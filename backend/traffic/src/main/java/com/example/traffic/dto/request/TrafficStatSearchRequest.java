package com.example.traffic.dto.request;

import jakarta.validation.constraints.NotNull;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDate;

@Getter
@NoArgsConstructor
public class TrafficStatSearchRequest {
    @NotNull(message = "조회 날짜는 필수입니다.")
    private LocalDate statDate; //

    private Long zoneId; // 특정 구역만 보고 싶을 때
}
