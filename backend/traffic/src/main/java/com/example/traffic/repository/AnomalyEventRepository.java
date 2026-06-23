package com.example.traffic.repository;

import com.example.traffic.domain.AnomalyEvent;
import com.example.traffic.common.enums.AnomalyEventStatus;
import com.example.traffic.common.enums.AnomalyType;
import com.example.traffic.common.enums.DataSourceType;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;

import java.util.Collection;
import java.util.Optional;

public interface AnomalyEventRepository extends JpaRepository<AnomalyEvent, Long>, JpaSpecificationExecutor<AnomalyEvent> {

    Optional<AnomalyEvent> findFirstByTargetCamera_CameraIdAndAnomalyTypeAndDataSourceAndStatusInOrderByLastDetectedAtDesc(
            Long cameraId,
            AnomalyType anomalyType,
            DataSourceType dataSource,
            Collection<AnomalyEventStatus> statuses
    );
}
