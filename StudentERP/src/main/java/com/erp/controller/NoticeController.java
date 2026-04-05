package com.erp.controller;

import com.erp.dto.AuthDTOs.ApiResponse;
import com.erp.service.NoticeService;
import com.erp.service.NoticeService.NoticeRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.http.*;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/notices")
@RequiredArgsConstructor
public class NoticeController {

    private final NoticeService noticeService;

    // ── GET /api/notices  – public read
    @GetMapping
    public ResponseEntity<ApiResponse> getAllNotices() {
        return ResponseEntity.ok(
            ApiResponse.ok("Active notices", noticeService.getAllActive()));
    }

    // ── GET /api/notices?category=EXAM
    @GetMapping("/category/{category}")
    public ResponseEntity<ApiResponse> getByCategory(@PathVariable String category) {
        return ResponseEntity.ok(
            ApiResponse.ok(category + " notices", noticeService.getByCategory(category)));
    }

    // ── POST /api/notices  (Faculty / Admin)
    @PostMapping
    @PreAuthorize("hasAnyRole('FACULTY', 'ADMIN')")
    public ResponseEntity<ApiResponse> createNotice(@RequestBody NoticeRequest req) {
        var notice = noticeService.createNotice(req);
        return ResponseEntity.status(HttpStatus.CREATED)
            .body(ApiResponse.ok("Notice posted", notice));
    }

    // ── DELETE /api/notices/{id}  (Admin only)
    @DeleteMapping("/{id}")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<ApiResponse> archiveNotice(@PathVariable Long id) {
        noticeService.archiveNotice(id);
        return ResponseEntity.ok(ApiResponse.ok("Notice archived"));
    }
}
