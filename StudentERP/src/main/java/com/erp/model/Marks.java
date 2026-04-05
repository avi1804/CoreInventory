package com.erp.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "marks",
       uniqueConstraints = @UniqueConstraint(
           columnNames = {"student_id", "subject_id", "exam_type"}))
@Getter @Setter @NoArgsConstructor @AllArgsConstructor @Builder
public class Marks {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "student_id", nullable = false)
    @JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
    private Student student;

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "subject_id", nullable = false)
    @JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
    private Subject subject;

    @Enumerated(EnumType.STRING)
    @Column(name = "exam_type", nullable = false)
    private ExamType examType;

    @Column(nullable = false)
    private Double marksObtained;

    @Column(nullable = false)
    private Double totalMarks;

    public enum ExamType {
        MID_SEM, END_SEM, INTERNAL, PRACTICAL
    }

    public String getGrade() {
        double percent = (marksObtained / totalMarks) * 100;
        if (percent >= 90) return "A+";
        if (percent >= 80) return "A";
        if (percent >= 70) return "B";
        if (percent >= 60) return "C";
        if (percent >= 50) return "D";
        return "F";
    }
}
