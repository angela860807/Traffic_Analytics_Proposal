package com.example.traffic.repository;

import com.example.traffic.domain.Post;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface PostRepository extends JpaRepository<Post, Long> {
    // 최신글 순으로 정렬해서 가져오는 쿼리 메서드 추가
    List<Post> findAllByOrderByCreatedAtDesc();
}
