package com.example.traffic.dto.request;

import com.example.traffic.common.enums.ZoneType;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
public class ZoneSaveRequest {

    @NotBlank(message = "구역 코드는 필수입니다.")
    @Size(max = 30, message = "구역 코드는 30자를 초과할 수 없습니다.")
    private String zoneCode;

    @NotBlank(message = "구역 명칭은 필수입니다.")
    @Size(max = 100, message = "구역 명칭은 100자를 초과할 수 없습니다.")
    private String zoneName;

    @NotNull(message = "구역 타입은 필수입니다.")
    private ZoneType zoneType;
}
