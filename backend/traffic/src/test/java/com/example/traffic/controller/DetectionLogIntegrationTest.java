package com.example.traffic.controller;

import com.example.traffic.common.enums.Direction;
import com.example.traffic.common.enums.ZoneType;
import com.example.traffic.domain.Camera;
import com.example.traffic.domain.Zone;
import com.example.traffic.repository.CameraRepository;
import com.example.traffic.repository.DetectionLogRepository;
import com.example.traffic.repository.VehicleFlowEventRepository;
import com.example.traffic.repository.VehicleRepository;
import com.example.traffic.repository.ZoneRepository;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.time.LocalDateTime;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest(properties = "app.api.internal-key=traffic-ai-internal-key-2026")
@AutoConfigureMockMvc
public class DetectionLogIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ZoneRepository zoneRepository;

    @Autowired
    private CameraRepository cameraRepository;

    @Autowired
    private DetectionLogRepository detectionLogRepository;

    @Autowired
    private VehicleRepository vehicleRepository;

    @Autowired
    private VehicleFlowEventRepository vehicleFlowEventRepository;

    @Test
    void fastApiDetectionRequest_savesDetectionLogVehicleAndFlowEvent() throws Exception {
        Zone zone = zoneRepository.save(Zone.builder()
                .zoneCode("TEST_ZONE_001")
                .zoneName("Test Zone")
                .zoneType(ZoneType.ENTRY)
                .build());

        cameraRepository.save(Camera.builder()
                .zone(zone)
                .cameraCode("TEST_CAM_001")
                .cameraName("Test Camera")
                .streamUrl("http://localhost/test-stream")
                .directionType(Direction.IN)
                .build());

        String plateNumber = "12가3456";
        String detectedAt = LocalDateTime.now().withNano(0).toString();

        String requestBody = """
                {
                  "cameraCode": "TEST_CAM_001",
                  "plateNumber": "%s",
                  "detectionType": "PLATE",
                  "confidenceScore": 0.95,
                  "imagePath": "/images/raw/test.jpg",
                  "imageUrl": "http://localhost/images/raw/test.jpg",
                  "detectedAt": "%s"
                }
                """.formatted(plateNumber, detectedAt);

        mockMvc.perform(post("/api/v1/detection-logs")
                        .header("X-Internal-Api-Key", "traffic-ai-internal-key-2026")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(requestBody))
                .andExpect(status().isOk());

        assertThat(detectionLogRepository.findByPlateNumberOrderByDetectedAtDesc(plateNumber))
                .isNotEmpty();

        assertThat(vehicleRepository.findByPlateNumber(plateNumber))
                .isPresent();

        assertThat(vehicleFlowEventRepository.findAll())
                .anyMatch(event -> event.getVehicle().getPlateNumber().equals(plateNumber)
                        && event.getSourceDetectionLog() != null);
    }
}
