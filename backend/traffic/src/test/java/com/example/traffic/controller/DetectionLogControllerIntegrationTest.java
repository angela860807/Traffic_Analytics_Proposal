package com.example.traffic.controller;

import com.example.traffic.common.enums.DetectionLogStatus;
import com.example.traffic.common.enums.DetectionType;
import com.example.traffic.domain.DetectionAnalysisResult;
import com.example.traffic.domain.DetectionLog;
import com.example.traffic.repository.DetectionAnalysisResultRepository;
import com.example.traffic.repository.DetectionLogRepository;
import com.example.traffic.repository.SpeedViolationRepository;
import com.example.traffic.repository.TrafficAnalysisIndexRepository;
import com.example.traffic.repository.VehicleFlowEventRepository;
import com.example.traffic.repository.VehicleRepository;
import com.jayway.jsonpath.JsonPath;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;
import org.springframework.transaction.annotation.Transactional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.hamcrest.Matchers.nullValue;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
@Transactional
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

    @Autowired
    private TrafficAnalysisIndexRepository trafficAnalysisIndexRepository;

    @Autowired
    private SpeedViolationRepository speedViolationRepository;

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
                .andExpect(jsonPath("$.data.logId").isNumber())
                .andExpect(jsonPath("$.data.flowEventId").isNumber())
                .andExpect(jsonPath("$.data.status").value("FLOW_EVENT_CREATED"))
                .andExpect(jsonPath("$.data.plateNumber").value(plateNumber));

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
        assertThat(trafficAnalysisIndexRepository.findByZoneZoneId(savedLog.getCamera().getZone().getZoneId()))
                .isPresent()
                .get()
                .satisfies(index -> {
                    assertThat(index.getLastLogId()).isEqualTo(savedLog.getLogId());
                    assertThat(index.getLastLogTime()).isEqualTo(savedLog.getDetectedAt());
                });
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
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.status").value("OCR_FAILED"))
                .andExpect(jsonPath("$.data.flowEventId").value(nullValue()));

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
        assertThat(savedResult.getDetectionType()).isEqualTo(DetectionType.VEHICLE);
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
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.status").value("DUPLICATE_SKIPPED"))
                .andExpect(jsonPath("$.data.flowEventId").value(nullValue()));

        DetectionAnalysisResult savedResult = detectionAnalysisResultRepository
                .findByPlateNumberOrderByCreatedAtDesc(plateNumber)
                .get(0);

        assertThat(detectionLogRepository.count()).isEqualTo(logCountBefore + 1);
        assertThat(detectionAnalysisResultRepository.count()).isEqualTo(resultCountBefore + 1);
        assertThat(vehicleFlowEventRepository.count()).isEqualTo(flowEventCountBefore);
        assertThat(savedResult.getStatus()).isEqualTo(DetectionLogStatus.DUPLICATE_SKIPPED);
    }

    @Test
    void createSpeedViolationSavesViolationForFlowEvent() throws Exception {
        String uniqueSuffix = String.valueOf(System.currentTimeMillis());
        String plateNumber = "SPD" + uniqueSuffix;
        long violationCountBefore = speedViolationRepository.count();

        MvcResult detectionResult = mockMvc.perform(post("/api/v1/detection-logs")
                        .header("X-Internal-Api-Key", INTERNAL_API_KEY)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {
                                  "cameraCode": "CAM_001",
                                  "plateNumber": "%s",
                                  "confidenceScore": 0.95,
                                  "imagePath": "storage/detections/2026/05/19/CAM_001_speed_frame.jpg",
                                  "imageUrl": "/static/detections/2026/05/19/CAM_001_speed_frame.jpg",
                                  "detectedAt": "2026-05-19T15:20:00",
                                  "detectionType": "PLATE"
                                }
                                """.formatted(plateNumber)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.status").value("FLOW_EVENT_CREATED"))
                .andExpect(jsonPath("$.data.flowEventId").isNumber())
                .andReturn();

        Integer flowEventId = JsonPath.read(detectionResult.getResponse().getContentAsString(), "$.data.flowEventId");

        mockMvc.perform(post("/api/speed-violations")
                        .header("X-Internal-Api-Key", INTERNAL_API_KEY)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {
                                  "flowEventId": %d,
                                  "plateNumber": "%s",
                                  "cameraCode": "CAM_001",
                                  "measuredSpeed": 72.35,
                                  "speedLimit": 50.0,
                                  "violationImagePath": "storage/detections/2026/05/19/CAM_001_152000_violation.jpg",
                                  "violationImageUrl": "/static/detections/2026/05/19/CAM_001_152000_violation.jpg",
                                  "violatedAt": "2026-05-19T15:20:00"
                                }
                                """.formatted(flowEventId, plateNumber)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.flowEventId").value(flowEventId))
                .andExpect(jsonPath("$.data.plateNumber").value(plateNumber))
                .andExpect(jsonPath("$.data.measuredSpeed").value(72.35))
                .andExpect(jsonPath("$.data.speedLimit").value(50.0))
                .andExpect(jsonPath("$.data.violationStatus").value("UNPROCESSED"));

        assertThat(speedViolationRepository.count()).isEqualTo(violationCountBefore + 1);
    }
}
