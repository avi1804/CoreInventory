package com.erp.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import jakarta.persistence.*;
import jakarta.validation.constraints.NotBlank;
import lombok.*;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.LocalDateTime;

@Entity
@Table(name = "notices")
@EntityListeners(AuditingEntityListener.class)
@Getter @Setter @NoArgsConstructor @AllArgsConstructor @Builder
public class Notice {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotBlank
    private String title;

    @Column(columnDefinition = "TEXT")
    private String content;

    @Enumerated(EnumType.STRING)
    @Builder.Default
    private NoticeCategory category = NoticeCategory.GENERAL;

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "posted_by")
    @JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
    private User postedBy;

    @CreatedDate
    @Column(updatable = false)
    private LocalDateTime postedAt;

    @Builder.Default
    private boolean active = true;

    public enum NoticeCategory {
        GENERAL, EXAM, FEE, EVENT, HOLIDAY, URGENT
    }
}
