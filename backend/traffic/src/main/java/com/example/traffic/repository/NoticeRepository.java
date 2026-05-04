package com.example.traffic.repository;

import com.example.traffic.domain.Notice;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface NoticeRepository extends JpaRepository<Notice, Long> {
    // 상단 고정글 우선 + 생성일 내림차순 조회 (설계서 인덱스 활용)
    List<Notice> findAllByOrderByIsPinnedDescCreatedAtDesc();
}
