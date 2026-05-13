package com.example.traffic.controller;

import com.example.traffic.common.enums.DetectionLogStatus;
import com.example.traffic.domain.DetectionAnalysisResult;
import com.example.traffic.domain.DetectionLog;
import com.example.traffic.repository.DetectionAnalysisResultRepository;
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
                "ALTER TABLE detection_logs ALTER COLUMN detection_type DROP NOT NULL"
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
    private DetectionAnalysisResultRepository detectionAnalysisResultRepository;

    @Autowired
    private VehicleRepository vehicleRepository;

    @Autowired
    private VehicleFlowEventRepository vehicleFlowEventRepository;

    @Test
    void processDetectionSavesLogAnalysisResultVehicleAndFlowEvent() throws Exception {
        String uniqueSuffix = String.valueOf(System.currentTimeMillis());
        String plateNumber = "TEST" + uniqueSuffix;
        String imageUrl = "/static/detections/2026/05/12/CAM_001_" + uniqueSuffix + "_frame.jpg";
        String plateCropImagePath = "storage/detections/2026/05/12/CAM_001_" + uniqueSuffix + "_plate_crop.jpg";
        String plateCropImageUrl = "/static/detections/2026/05/12/CAM_001_" + uniqueSuffix + "_plate_crop.jpg";
        String ocrImagePath = "storage/detections/2026/05/12/CAM_001_" + uniqueSuffix + "_ocr.jpg";
        String ocrImageUrl = "/static/detections/2026/05/12/CAM_001_" + uniqueSuffix + "_ocr.jpg";
        long logCountBefore = detectionLogRepository.count();
        long resultCountBefore = detectionAnalysisResultRepository.count();
        long flowEventCountBefore = vehicleFlowEventRepository.count();

        mockMvc.perform(post("/api/v1/detection-logs")
                        .header("X-Internal-Api-Key", INTERNAL_API_KEY)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {
                                  "cameraCode": "CAM_001",
                                  "plateNumber": "%s",
                                  "confidenceScore": 0.9321,
                                  "imagePath": "storage/detections/2026/05/12/CAM_001_103000_frame.jpg",
                                  "imageUrl": "%s",
                                  "plateCropImagePath": "%s",
                                  "plateCropImageUrl": "%s",
                                  "ocrImagePath": "%s",
                                  "ocrImageUrl": "%s",
                                  "detectedAt": "2026-05-12T10:30:00",
                                  "detectionType": "PLATE"
                                }
                                """.formatted(plateNumber, imageUrl, plateCropImagePath, plateCropImageUrl,
                                ocrImagePath, ocrImageUrl)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data").isNumber());

        assertThat(detectionLogRepository.count()).isEqualTo(logCountBefore + 1);
        assertThat(detectionAnalysisResultRepository.count()).isEqualTo(resultCountBefore + 1);
        assertThat(vehicleRepository.findByPlateNumber(plateNumber)).isPresent();
        assertThat(vehicleFlowEventRepository.count()).isEqualTo(flowEventCountBefore + 1);

        DetectionAnalysisResult savedResult = detectionAnalysisResultRepository
                .findByPlateNumberOrderByCreatedAtDesc(plateNumber)
                .get(0);
        DetectionLog savedLog = savedResult.getDetectionLog();

        assertThat(savedLog.getImageUrl()).isEqualTo(imageUrl);
        assertThat(savedResult.getStatus()).isEqualTo(DetectionLogStatus.FLOW_EVENT_CREATED);
        assertThat(savedResult.getPlateCropImagePath()).isEqualTo(plateCropImagePath);
        assertThat(savedResult.getPlateCropImageUrl()).isEqualTo(plateCropImageUrl);
        assertThat(savedResult.getOcrImagePath()).isEqualTo(ocrImagePath);
        assertThat(savedResult.getOcrImageUrl()).isEqualTo(ocrImageUrl);
    }

    @Test
    void processDetectionRequiresInternalApiKey() throws Exception {
        mockMvc.perform(post("/api/v1/detection-logs")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {
                                  "cameraCode": "CAM_001",
                                  "plateNumber": "NO_KEY_TEST",
                                  "confidenceScore": 0.8,
                                  "imagePath": "storage/detections/test.jpg",
                                  "detectedAt": "2026-05-12T10:30:00",
                                  "detectionType": "PLATE"
                                }
                                """))
                .andExpect(status().isUnauthorized());
    }

    @Test
    void processDetectionSavesOcrFailedAnalysisResultWithoutVehicleOrFlowEvent() throws Exception {
        String imageUrl = "/static/detections/2026/05/12/CAM_001_ocr_failed_"
                + System.currentTimeMillis() + "_frame.jpg";
        long logCountBefore = detectionLogRepository.count();
        long resultCountBefore = detectionAnalysisResultRepository.count();
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
                                  "imageUrl": "%s",
                                  "detectedAt": "2026-05-12T10:35:00",
                                  "detectionType": "VEHICLE",
                                  "status": "OCR_FAILED"
                                }
                                """.formatted(imageUrl)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true));

        DetectionLog savedLog = detectionLogRepository.findTop100ByOrderByDetectedAtDesc().stream()
                .filter(log -> imageUrl.equals(log.getImageUrl()))
                .findFirst()
                .orElseThrow();
        DetectionAnalysisResult savedResult = detectionAnalysisResultRepository
                .findFirstByDetectionLog_LogIdOrderByAttemptNoDesc(savedLog.getLogId())
                .orElseThrow();

        assertThat(detectionLogRepository.count()).isEqualTo(logCountBefore + 1);
        assertThat(detectionAnalysisResultRepository.count()).isEqualTo(resultCountBefore + 1);
        assertThat(vehicleRepository.count()).isEqualTo(vehicleCountBefore);
        assertThat(vehicleFlowEventRepository.count()).isEqualTo(flowEventCountBefore);
        assertThat(savedResult.getStatus()).isEqualTo(DetectionLogStatus.OCR_FAILED);
    }

    @Test
    void processDetectionSavesDuplicateAnalysisResultWithoutFlowEvent() throws Exception {
        String plateNumber = "DUP" + System.currentTimeMillis();
        long logCountBefore = detectionLogRepository.count();
        long resultCountBefore = detectionAnalysisResultRepository.count();
        long flowEventCountBefore = vehicleFlowEventRepository.count();

        mockMvc.perform(post("/api/v1/detection-logs")
                        .header("X-Internal-Api-Key", INTERNAL_API_KEY)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {
                                  "cameraCode": "CAM_001",
                                  "plateNumber": "%s",
                                  "confidenceScore": 0.91,
                                  "imagePath": "storage/detections/2026/05/12/CAM_001_103600_frame.jpg",
                                  "imageUrl": "/static/detections/2026/05/12/CAM_001_103600_frame.jpg",
                                  "detectedAt": "2026-05-12T10:36:00",
                                  "detectionType": "PLATE",
                                  "status": "DUPLICATE_SKIPPED"
                                }
                                """.formatted(plateNumber)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true));

        DetectionAnalysisResult savedResult = detectionAnalysisResultRepository
                .findByPlateNumberOrderByCreatedAtDesc(plateNumber)
                .get(0);

        assertThat(detectionLogRepository.count()).isEqualTo(logCountBefore + 1);
        assertThat(detectionAnalysisResultRepository.count()).isEqualTo(resultCountBefore + 1);
        assertThat(vehicleFlowEventRepository.count()).isEqualTo(flowEventCountBefore);
        assertThat(savedResult.getStatus()).isEqualTo(DetectionLogStatus.DUPLICATE_SKIPPED);
    }
}
