package com.erp.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import jakarta.persistence.*;
import jakarta.validation.constraints.NotBlank;
import lombok.*;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.LocalDate;
import java.time.LocalDateTime;

@Entity
@Table(name = "students")
@EntityListeners(AuditingEntityListener.class)
@Getter @Setter
@NoArgsConstructor @AllArgsConstructor
@Builder
public class Student {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotBlank
    @Column(name = "roll_no", nullable = false, unique = true)
    private String rollNo;

    @NotBlank
    private String branch;

    @Column(nullable = false)
    private Integer semester;

    private String phone;
    private String address;
    private LocalDate dateOfBirth;
    private String guardianName;
    private String guardianPhone;

    @Enumerated(EnumType.STRING)
    @Builder.Default
    private AdmissionStatus status = AdmissionStatus.ACTIVE;

    @OneToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "user_id", nullable = false, unique = true)
    @JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
    private User user;

    @CreatedDate
    @Column(updatable = false)
    private LocalDateTime admissionDate;

    public enum AdmissionStatus {
        ACTIVE, PENDING, GRADUATED, DROPPED
    }

    // Convenience helpers
    public String getName()  { return user != null ? user.getName()  : null; }
    public String getEmail() { return user != null ? user.getEmail() : null; }
}
