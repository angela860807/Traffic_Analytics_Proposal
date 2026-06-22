package com.example.traffic.dto.response.predictive;

import com.example.traffic.common.enums.UserRole;
import lombok.Builder;
import lombok.Getter;

@Getter
@Builder
public class PredictiveAssigneeResponse {
    private final Long memberId;
    private final String name;
    private final String email;
    private final UserRole role;
}
