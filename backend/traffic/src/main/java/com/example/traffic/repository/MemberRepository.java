package com.example.traffic.repository;

import com.example.traffic.domain.Member;
import com.example.traffic.common.enums.UserRole;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Collection;
import java.util.List;
import java.util.Optional;

public interface MemberRepository extends JpaRepository<Member, Long> {

    Optional<Member> findByEmail(String email);

    List<Member> findByRoleInOrderByRoleAscNameAsc(Collection<UserRole> roles);

    boolean existsByEmail(String email);
    boolean existsByPhone(String phone);

}
