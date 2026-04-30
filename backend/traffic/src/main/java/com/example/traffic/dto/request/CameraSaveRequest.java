package com.example.traffic.dto.request;

import com.example.traffic.common.enums.Direction;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
public class CameraSaveRequest {
    @NotNull(message = "구역 ID는 필수입니다.")
    private Long zoneId;

    @NotBlank(message = "카메라 코드는 필수입니다.")
    @Size(max = 30)
    private String cameraCode;

    @NotBlank(message = "카메라 이름은 필수입니다.")
    @Size(max = 100)
    private String cameraName;

    @Size(max = 255)
    private String streamUrl;

    @NotNull(message = "방향 설정은 필수입니다.")
    private Direction directionType;
}