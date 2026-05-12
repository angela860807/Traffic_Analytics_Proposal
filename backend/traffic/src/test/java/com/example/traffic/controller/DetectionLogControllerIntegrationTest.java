package com.example.traffic.controller;

import com.example.traffic.common.enums.DetectionLogStatus;
import com.example.traffic.repository.DetectionLogRepository;
import com.example.traffic.repository.VehicleFlowEventRepository;
import com.example.traffic.repository.VehicleRepository;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.jdbc.Sql;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.transaction.annotation.Transactional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
@Transactional
@Sql(
        statements = {
                "ALTER TABLE detection_logs ALTER COLUMN plate_number DROP NOT NULL",
                "ALTER TABLE detection_logs DROP CONSTRAINT IF EXISTS detection_logs_status_check",
                "ALTER TABLE detection_logs ADD CONSTRAINT detection_logs_status_check CHECK (status IN ('RECEIVED', 'OCR_FAILED', 'FLOW_EVENT_CREATED', 'DUPLICATE_SKIPPED'))"
        },
        executionPhase = Sql.ExecutionPhase.BEFORE_TEST_METHOD
)
class DetectionLogControllerIntegrationTest {

    private static final String INTERNAL_API_KEY = "traffic-ai-internal-key-2026";

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private DetectionLogRepository detectionLogRepository;

    @Autowired
    private VehicleRepository vehicleRepository;

    @Autowired
    private VehicleFlowEventRepository vehicleFlowEventRepository;

    @Test
    void processDetectionSavesLogVehicleAndFlowEvent() throws Exception {
        String plateNumber = "12가3456";
        long logCountBefore = detectionLogRepository.count();
        long flowEventCountBefore = vehicleFlowEventRepository.count();

        mockMvc.perform(post("/api/v1/detection-logs")
                        .header("X-Internal-Api-Key", INTERNAL_API_KEY)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {
                                  "cameraCode": "CAM_001",
                                  "plateNumber": "12가3456",
                                  "confidenceScore": 0.9321,
                                  "imagePath": "storage/detections/2026/05/12/CAM_001_103000_frame.jpg",
                                  "imageUrl": "/static/detections/2026/05/12/CAM_001_103000_frame.jpg",
                                  "detectedAt": "2026-05-12T10:30:00",
                                  "detectionType": "PLATE"
                                }
                                """))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data").isNumber());

        assertThat(detectionLogRepository.count()).isEqualTo(logCountBefore + 1);
        assertThat(vehicleRepository.findByPlateNumber(plateNumber)).isPresent();
        assertThat(vehicleFlowEventRepository.count()).isEqualTo(flowEventCountBefore + 1);
        assertThat(detectionLogRepository.findByPlateNumberOrderByDetectedAtDesc(plateNumber))
                .first()
                .extracting("status")
                .isEqualTo(DetectionLogStatus.FLOW_EVENT_CREATED);
    }

    @Test
    void processDetectionRequiresInternalApiKey() throws Exception {
        mockMvc.perform(post("/api/v1/detection-logs")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {
                                  "cameraCode": "CAM_001",
                                  "plateNumber": "99가9999",
                                  "confidenceScore": 0.8,
                                  "imagePath": "storage/detections/test.jpg",
                                  "detectedAt": "2026-05-12T10:30:00",
                                  "detectionType": "PLATE"
                                }
                                """))
                .andExpect(status().isUnauthorized());
    }

    @Test
    void processDetectionSavesOcrFailedLogWithoutVehicleOrFlowEvent() throws Exception {
        long logCountBefore = detectionLogRepository.count();
        long vehicleCountBefore = vehicleRepository.count();
        long flowEventCountBefore = vehicleFlowEventRepository.count();

        mockMvc.perform(post("/api/v1/detection-logs")
                        .header("X-Internal-Api-Key", INTERNAL_API_KEY)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {
                                  "cameraCode": "CAM_001",
                                  "plateNumber": null,
                                  "confidenceScore": 0.0,
                                  "imagePath": "storage/detections/2026/05/12/CAM_001_103500_frame.jpg",
                                  "imageUrl": "/static/detections/2026/05/12/CAM_001_103500_frame.jpg",
                                  "detectedAt": "2026-05-12T10:35:00",
                                  "detectionType": "VEHICLE",
                                  "status": "OCR_FAILED"
                                }
                                """))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true));

        assertThat(detectionLogRepository.count()).isEqualTo(logCountBefore + 1);
        assertThat(vehicleRepository.count()).isEqualTo(vehicleCountBefore);
        assertThat(vehicleFlowEventRepository.count()).isEqualTo(flowEventCountBefore);
        assertThat(detectionLogRepository.findTop100ByOrderByDetectedAtDesc())
                .first()
                .extracting("status")
                .isEqualTo(DetectionLogStatus.OCR_FAILED);
    }

    @Test
    void processDetectionSavesFastApiDuplicateLogWithoutFlowEvent() throws Exception {
        String plateNumber = "34나5678";
        long logCountBefore = detectionLogRepository.count();
        long flowEventCountBefore = vehicleFlowEventRepository.count();

        mockMvc.perform(post("/api/v1/detection-logs")
                        .header("X-Internal-Api-Key", INTERNAL_API_KEY)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {
                                  "cameraCode": "CAM_001",
                                  "plateNumber": "34나5678",
                                  "confidenceScore": 0.91,
                                  "imagePath": "storage/detections/2026/05/12/CAM_001_103600_frame.jpg",
                                  "imageUrl": "/static/detections/2026/05/12/CAM_001_103600_frame.jpg",
                                  "detectedAt": "2026-05-12T10:36:00",
                                  "detectionType": "PLATE",
                                  "status": "DUPLICATE_SKIPPED"
                                }
                                """))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true));

        assertThat(detectionLogRepository.count()).isEqualTo(logCountBefore + 1);
        assertThat(vehicleRepository.findByPlateNumber(plateNumber)).isPresent();
        assertThat(vehicleFlowEventRepository.count()).isEqualTo(flowEventCountBefore);
        assertThat(detectionLogRepository.findByPlateNumberOrderByDetectedAtDesc(plateNumber))
                .first()
                .extracting("status")
                .isEqualTo(DetectionLogStatus.DUPLICATE_SKIPPED);
    }
}
