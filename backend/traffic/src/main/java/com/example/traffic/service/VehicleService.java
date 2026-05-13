package com.example.traffic.service;

import com.example.traffic.common.enums.VehicleStatus;
import com.example.traffic.domain.Vehicle;
import com.example.traffic.dto.request.VehicleStatusRequest;
import com.example.traffic.dto.response.VehicleResponse;
import com.example.traffic.repository.VehicleRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@Transactional(readOnly = true)
@RequiredArgsConstructor
public class VehicleService {

    private final VehicleRepository vehicleRepository;

    /**
     * [차량 조회 또는 자동 등록]
     * 탐지 로그 생성 시 번호판이 없으면 새로 생성, 있으면 기존 객체 반환[cite: 20, 22]
     */
    @Transactional
    public Vehicle getOrCreateVehicle(String plateNumber) {
        return vehicleRepository.findByPlateNumber(plateNumber)
                .orElseGet(() -> vehicleRepository.save(
                        Vehicle.builder()
                                .plateNumber(plateNumber)
                                .vehicleStatus(VehicleStatus.ACTIVE)
                                .build()
                ));
    }

    /**
     * [차량 상태 업데이트] 도난/수배 차량 등 상태 변경[cite: 11, 14]
     */
    @Transactional
    public void updateVehicleStatus(Long vehicleId, VehicleStatusRequest request) {
        Vehicle vehicle = vehicleRepository.findById(vehicleId)
                .orElseThrow(() -> new IllegalArgumentException("해당 차량이 없습니다."));
        vehicle.updateStatus(request.getVehicleStatus());
    }

    /**
     * [차량 단건 조회] 상세 정보 및 탐지 시각 확인[cite: 18]
     */
    public VehicleResponse getVehicle(Long vehicleId) {
        return vehicleRepository.findById(vehicleId)
                .map(VehicleResponse::from)
                .orElseThrow(() -> new IllegalArgumentException("해당 차량이 없습니다."));
    }
}