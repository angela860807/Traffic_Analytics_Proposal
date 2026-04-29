package com.example.traffic.service;

import com.example.traffic.domain.Zone;
import com.example.traffic.repository.ZoneRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@Transactional(readOnly = true)
@RequiredArgsConstructor
public class ZoneService {

    private final ZoneRepository zoneRepository;

    public List<Zone> findAllZones() {
        return zoneRepository.findAll();
    }
}
