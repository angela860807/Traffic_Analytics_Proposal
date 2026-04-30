package com.example.traffic.dto.request;

import com.example.traffic.common.enums.Direction;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
public class CameraUpdateRequest {
    @NotBlank(message = "카메라 이름은 필수입니다.")
    @Size(max = 100)
    private String cameraName;

    @Size(max = 255)
    private String streamUrl;

    @NotNull(message = "방향 설정은 필수입니다.")
    private Direction directionType;

    @NotNull(message = "활성화 상태는 필수입니다.")
    private Boolean isActive; // 수정 시에만 직접 조절[cite: 1]
}