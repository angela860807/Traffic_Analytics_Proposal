package com.example.traffic.service;

import com.example.traffic.domain.Member;
import com.example.traffic.domain.Notice;
import com.example.traffic.dto.request.NoticeSaveRequest;
import com.example.traffic.dto.response.NoticeResponse;
import com.example.traffic.etc.BusinessException;
import com.example.traffic.repository.MemberRepository;
import com.example.traffic.repository.NoticeRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class NoticeService {

    private final NoticeRepository noticeRepository;
    private final MemberRepository memberRepository;

    // 공지 작성 (ADMIN 권한 체크는 Controller/Security에서 1차 수행)
    @Transactional
    public Long saveNotice(NoticeSaveRequest request, String email) {
        Member author = memberRepository.findByEmail(email)
                .orElseThrow(() -> new BusinessException("사용자를 찾을 수 없습니다.", HttpStatus.NOT_FOUND));

        Notice notice = Notice.builder()
                .author(author)
                .title(request.getTitle())
                .content(request.getContent())
                .isPinned(request.isPinned())
                .build();

        return noticeRepository.save(notice).getNoticeId();
    }

    // 전체 목록 조회
    public List<NoticeResponse> getNoticeList() {
        return noticeRepository.findAllByOrderByIsPinnedDescCreatedAtDesc().stream()
                .map(NoticeResponse::new)
                .collect(Collectors.toList());
    }

    // 상세 조회 (조회수 증가 포함)
    @Transactional
    public NoticeResponse getNoticeDetail(Long id) {
        Notice notice = noticeRepository.findById(id)
                .orElseThrow(() -> new BusinessException("공지사항을 찾을 수 없습니다.", HttpStatus.NOT_FOUND));

        notice.incrementViewCount();
        return new NoticeResponse(notice);
    }

    // 수정
    @Transactional
    public void updateNotice(Long id, NoticeSaveRequest request) {
        Notice notice = noticeRepository.findById(id)
                .orElseThrow(() -> new BusinessException("공지사항을 찾을 수 없습니다.", HttpStatus.NOT_FOUND));

        notice.update(request.getTitle(), request.getContent(), request.isPinned());
    }

    // 삭제
    @Transactional
    public void deleteNotice(Long id) {
        if (!noticeRepository.existsById(id)) {
            throw new BusinessException("존재하지 않는 공지사항입니다.", HttpStatus.NOT_FOUND);
        }
        noticeRepository.deleteById(id);
    }
}
