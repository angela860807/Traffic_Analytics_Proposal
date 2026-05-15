package com.example.traffic.service;

import com.example.traffic.domain.TrafficAnalysisIndex;
import com.example.traffic.domain.Zone;
import com.example.traffic.repository.TrafficAnalysisIndexRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;

@Service
@Transactional(readOnly = true)
@RequiredArgsConstructor
public class TrafficAnalysisIndexService {

    private final TrafficAnalysisIndexRepository trafficAnalysisIndexRepository;

    @Transactional
    public TrafficAnalysisIndex updateCheckpoint(Zone zone,
                                                 Long lastSeq,
                                                 Long lastLogId,
                                                 LocalDateTime lastLogTime) {
        TrafficAnalysisIndex index = trafficAnalysisIndexRepository.findByZone(zone)
                .orElseGet(() -> TrafficAnalysisIndex.builder()
                        .zone(zone)
                        .build());

        index.update(lastSeq, lastLogId, lastLogTime);

        return trafficAnalysisIndexRepository.save(index);
    }
}
