package com.example.traffic.repository;

import com.example.traffic.domain.CameraHealthSample;
import com.example.traffic.common.enums.DataSourceType;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface CameraHealthSampleRepository extends JpaRepository<CameraHealthSample, Long> {

    @Query("""
            SELECT sample
            FROM CameraHealthSample sample
            WHERE sample.camera.cameraId = :cameraId
              AND sample.dataSource = :dataSource
              AND sample.isLateSample = false
            ORDER BY sample.sampledAt DESC
            """)
    List<CameraHealthSample> findRecentEligibleSamples(
            @Param("cameraId") Long cameraId,
            @Param("dataSource") DataSourceType dataSource,
            Pageable pageable
    );
}
