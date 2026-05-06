package com.example.traffic.repository;

import com.example.traffic.domain.Comment;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface CommentRepository extends JpaRepository<Comment, Long> {

    List<Comment> findAllByPostPostIdOrderByCreatedAtAsc(Long postId);
}
