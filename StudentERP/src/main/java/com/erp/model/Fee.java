package com.erp.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import jakarta.persistence.*;
import lombok.*;

import java.math.BigDecimal;
import java.time.LocalDate;

@Entity
@Table(name = "fees")
@Getter @Setter @NoArgsConstructor @AllArgsConstructor @Builder
public class Fee {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "student_id", nullable = false)
    @JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
    private Student student;

    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal amount;

    @Column(nullable = false)
    private LocalDate dueDate;

    private LocalDate paidDate;
    private String receiptNumber;
    private String feeType;

    @Enumerated(EnumType.STRING)
    @Builder.Default
    private FeeStatus status = FeeStatus.PENDING;

    public enum FeeStatus {
        PENDING, PAID, OVERDUE, WAIVED
    }
}
