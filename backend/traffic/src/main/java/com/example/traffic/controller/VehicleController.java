package com.example.traffic.controller;

import com.example.traffic.domain.Vehicle;
import com.example.traffic.service.VehicleService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/vehicles")
@RequiredArgsConstructor
public class VehicleController {

    private final VehicleService vehicleService;

    public Vehicle register(@RequestParam String plateNumber) {
        return vehicleService.getOrCreateVehicle(plateNumber);
    }

    @GetMapping
    public List<Vehicle> list() {
        return vehicleService.findAll();
    }
}
