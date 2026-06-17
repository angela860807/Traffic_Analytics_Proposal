package com.example.traffic.util;

import java.time.LocalDateTime;
import java.time.OffsetDateTime;
import java.time.ZoneId;
import java.time.ZoneOffset;

public final class PredictiveTimeUtils {

    public static final ZoneId SERVICE_ZONE = ZoneId.of("Asia/Seoul");

    private PredictiveTimeUtils() {
    }

    public static OffsetDateTime toSeoulOffset(LocalDateTime value) {
        if (value == null) {
            return null;
        }
        ZoneOffset offset = SERVICE_ZONE.getRules().getOffset(value);
        return value.atOffset(offset);
    }

    public static LocalDateTime toLocalDateTime(OffsetDateTime value) {
        if (value == null) {
            return null;
        }
        return value.atZoneSameInstant(SERVICE_ZONE).toLocalDateTime();
    }
}
