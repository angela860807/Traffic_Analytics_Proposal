package com.example.traffic.service;

import com.example.traffic.common.enums.DetectionMethod;
import com.example.traffic.common.enums.DetectorOperatingMode;
import com.example.traffic.domain.DetectorVersion;
import com.example.traffic.dto.response.predictive.DetectionEvaluationResponse;
import com.example.traffic.etc.BusinessException;
import com.example.traffic.repository.DetectorVersionRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class PredictiveAnomalyCandidateGuardService {

    private final DetectorVersionRepository detectorVersionRepository;

    public List<DetectionEvaluationResponse.Candidate> getActiveCandidatesForEventProcessing(
            DetectionEvaluationResponse response) {
        if (response == null || response.getCandidates() == null || response.getCandidates().isEmpty()) {
            return List.of();
        }

        DetectorVersion detectorVersion = findDetectorVersion(response.getDetector());
        if (!detectorVersion.isActive() || !DetectorOperatingMode.ACTIVE.equals(detectorVersion.getOperatingMode())) {
            return List.of();
        }
        if (DetectionMethod.LSTM_AUTOENCODER.equals(detectorVersion.getDetectionMethod())) {
            return List.of();
        }

        return response.getCandidates();
    }

    public void validateActiveDetectorForEventProcessing(DetectorVersion detectorVersion) {
        if (detectorVersion == null) {
            throw new BusinessException("Detector version is missing.", HttpStatus.BAD_REQUEST);
        }
        if (!detectorVersion.isActive() || !DetectorOperatingMode.ACTIVE.equals(detectorVersion.getOperatingMode())) {
            throw new BusinessException("Only ACTIVE detector results can create anomaly events.", HttpStatus.CONFLICT);
        }
        if (DetectionMethod.LSTM_AUTOENCODER.equals(detectorVersion.getDetectionMethod())) {
            throw new BusinessException("LSTM_AUTOENCODER results must not create anomaly events.", HttpStatus.CONFLICT);
        }
    }

    private DetectorVersion findDetectorVersion(DetectionEvaluationResponse.Detector detector) {
        if (detector == null || detector.getName() == null || detector.getVersion() == null) {
            throw new BusinessException("Detector information is missing.", HttpStatus.BAD_REQUEST);
        }
        return detectorVersionRepository.findByDetectorNameAndVersion(detector.getName(), detector.getVersion())
                .orElseThrow(() -> new BusinessException(
                        "Detector version not found: " + detector.getName() + " " + detector.getVersion(),
                        HttpStatus.NOT_FOUND));
    }
}
