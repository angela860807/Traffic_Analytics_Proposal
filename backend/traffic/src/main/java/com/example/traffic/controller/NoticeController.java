package com.example.traffic.controller;

import com.example.traffic.dto.request.NoticeSaveRequest;
import com.example.traffic.dto.response.CommonResponse;
import com.example.traffic.dto.response.NoticeResponse;
import com.example.traffic.service.NoticeService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/notices")
@RequiredArgsConstructor
public class NoticeController {

    private final NoticeService noticeService;

    // 공지사항 등록 (ADMIN)
    @PostMapping
    public ResponseEntity<CommonResponse<Long>> createNotice(@RequestBody NoticeSaveRequest request,
                                                             @AuthenticationPrincipal UserDetails userDetails) {
        Long noticeId = noticeService.saveNotice(request, userDetails.getUsername());
        return ResponseEntity.ok(CommonResponse.success(noticeId, "공지사항이 등록되었습니다."));
    }

    // 공지사항 목록 조회 (전체)
    @GetMapping
    public ResponseEntity<CommonResponse<List<NoticeResponse>>> getNoticeList() {
        return ResponseEntity.ok(CommonResponse.success(noticeService.getNoticeList(), "목록 조회 성공"));
    }

    // 공지사항 상세 조회 (전체)
    @GetMapping("/{id}")
    public ResponseEntity<CommonResponse<NoticeResponse>> getNotice(@PathVariable Long id) {
        return ResponseEntity.ok(CommonResponse.success(noticeService.getNoticeDetail(id), "상세 조회 성공"));
    }

    // 공지사항 수정 (ADMIN)
    @PutMapping("/{id}")
    public ResponseEntity<CommonResponse<Void>> updateNotice(@PathVariable Long id, @RequestBody NoticeSaveRequest request) {
        noticeService.updateNotice(id, request);
        return ResponseEntity.ok(CommonResponse.success(null, "공지사항이 수정되었습니다."));
    }

    // 공지사항 삭제 (ADMIN)
    @DeleteMapping("/{id}")
    public ResponseEntity<CommonResponse<Void>> deleteNotice(@PathVariable Long id) {
        noticeService.deleteNotice(id);
        return ResponseEntity.ok(CommonResponse.success(null, "공지사항이 삭제되었습니다."));
    }
}
