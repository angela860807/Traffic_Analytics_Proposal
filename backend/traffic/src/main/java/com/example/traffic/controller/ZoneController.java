package com.example.traffic.controller;

import com.example.traffic.domain.Zone;
import com.example.traffic.service.ZoneService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/zones")
@RequiredArgsConstructor
public class ZoneController {

    private final ZoneService zoneService;

    @GetMapping
    public List<Zone> getAllZones() {
        return zoneService.findAllZones();
    }
}
