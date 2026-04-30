package com.example.traffic.service;

import com.example.traffic.domain.Vehicle;
import com.example.traffic.repository.VehicleRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@Transactional(readOnly = true)
@RequiredArgsConstructor
public class VehicleService {

    private final VehicleRepository vehicleRepository;

    public Vehicle getOrCreateVehicle(String plateNumber) {
        return vehicleRepository.findByPlateNumber(plateNumber)
                .orElseGet(() -> vehicleRepository.save(
                        Vehicle.builder().plateNumber(plateNumber).build()
                ));
    }

    @Transactional(readOnly = true)
    public List<Vehicle> findAll() {
        return vehicleRepository.findAll();
    }
}
