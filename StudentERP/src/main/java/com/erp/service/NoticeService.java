package com.erp.service;

import com.erp.exception.ResourceNotFoundException;
import com.erp.model.*;
import com.erp.repository.*;
import lombok.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class NoticeService {

    private final NoticeRepository noticeRepo;
    private final UserRepository   userRepo;

    @Getter @Setter
    public static class NoticeRequest {
        private String title;
        private String content;
        private String category;  // GENERAL | EXAM | FEE | EVENT | HOLIDAY | URGENT
        private Long   postedById;
    }

    // ── Create notice ─────────────────────────────────────────────────────
    @Transactional
    public Notice createNotice(NoticeRequest req) {
        User poster = userRepo.findById(req.getPostedById())
            .orElseThrow(() -> new ResourceNotFoundException("User", "id", req.getPostedById()));

        Notice.NoticeCategory category;
        try {
            category = Notice.NoticeCategory.valueOf(req.getCategory().toUpperCase());
        } catch (Exception e) {
            category = Notice.NoticeCategory.GENERAL;
        }

        Notice notice = Notice.builder()
            .title(req.getTitle())
            .content(req.getContent())
            .category(category)
            .postedBy(poster)
            .active(true)
            .build();

        return noticeRepo.save(notice);
    }

    // ── Get all active notices ────────────────────────────────────────────
    public List<Notice> getAllActive() {
        return noticeRepo.findByActiveTrueOrderByPostedAtDesc();
    }

    // ── Filter by category ────────────────────────────────────────────────
    public List<Notice> getByCategory(String category) {
        Notice.NoticeCategory cat = Notice.NoticeCategory.valueOf(category.toUpperCase());
        return noticeRepo.findByCategoryAndActiveTrueOrderByPostedAtDesc(cat);
    }

    // ── Archive (soft delete) ─────────────────────────────────────────────
    @Transactional
    public void archiveNotice(Long id) {
        Notice notice = noticeRepo.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("Notice", "id", id));
        notice.setActive(false);
        noticeRepo.save(notice);
    }
}
