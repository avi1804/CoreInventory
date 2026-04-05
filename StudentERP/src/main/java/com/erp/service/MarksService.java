package com.erp.service;

import com.erp.exception.ResourceNotFoundException;
import com.erp.model.*;
import com.erp.repository.*;
import lombok.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.*;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class MarksService {

    private final MarksRepository   marksRepo;
    private final StudentRepository studentRepo;
    private final SubjectRepository subjectRepo;

    // ── DTOs ──────────────────────────────────────────────────────────────
    @Getter @Setter
    public static class MarksRequest {
        private Long   studentId;
        private Long   subjectId;
        private String examType;       // MID_SEM | END_SEM | INTERNAL | PRACTICAL
        private Double marksObtained;
        private Double totalMarks;
    }

    @Getter @Builder
    public static class SubjectResult {
        private Long   subjectId;
        private String subjectName;
        private String subjectCode;
        private Integer credits;
        private String examType;
        private Double marksObtained;
        private Double totalMarks;
        private Double percentage;
        private String grade;
    }

    @Getter @Builder
    public static class ResultCard {
        private Long          studentId;
        private String        studentName;
        private String        rollNo;
        private String        branch;
        private Integer       semester;
        private String        examType;
        private List<SubjectResult> subjects;
        private Double        totalMarks;
        private Double        totalObtained;
        private Double        percentage;
        private String        overallGrade;
        private String        result;   // PASS | FAIL
    }

    // ── Enter / update marks ──────────────────────────────────────────────
    @Transactional
    public Marks enterMarks(MarksRequest req) {
        Marks.ExamType examType = Marks.ExamType.valueOf(req.getExamType().toUpperCase());

        Student student = studentRepo.findById(req.getStudentId())
            .orElseThrow(() -> new ResourceNotFoundException("Student", "id", req.getStudentId()));

        Subject subject = subjectRepo.findById(req.getSubjectId())
            .orElseThrow(() -> new ResourceNotFoundException("Subject", "id", req.getSubjectId()));

        Marks marks = marksRepo
            .findByStudentIdAndSubjectIdAndExamType(req.getStudentId(), req.getSubjectId(), examType)
            .orElseGet(() -> Marks.builder()
                .student(student)
                .subject(subject)
                .examType(examType)
                .build());

        marks.setMarksObtained(req.getMarksObtained());
        marks.setTotalMarks(req.getTotalMarks());
        return marksRepo.save(marks);
    }

    // ── Bulk marks entry ──────────────────────────────────────────────────
    @Transactional
    public List<Marks> enterBulkMarks(List<MarksRequest> requests) {
        return requests.stream()
            .map(this::enterMarks)
            .collect(Collectors.toList());
    }

    // ── Generate full result card for a student ───────────────────────────
    public ResultCard getResultCard(Long studentId, String examType) {
        Student student = studentRepo.findById(studentId)
            .orElseThrow(() -> new ResourceNotFoundException("Student", "id", studentId));

        Marks.ExamType type = Marks.ExamType.valueOf(examType.toUpperCase());
        List<Marks> marksList = marksRepo.findByStudentIdAndExamType(studentId, type);

        List<SubjectResult> subjects = marksList.stream().map(m -> {
            double pct = (m.getMarksObtained() / m.getTotalMarks()) * 100;
            return SubjectResult.builder()
                .subjectId(m.getSubject().getId())
                .subjectName(m.getSubject().getName())
                .subjectCode(m.getSubject().getCode())
                .credits(m.getSubject().getCredits())
                .examType(examType)
                .marksObtained(m.getMarksObtained())
                .totalMarks(m.getTotalMarks())
                .percentage(Math.round(pct * 10.0) / 10.0)
                .grade(m.getGrade())
                .build();
        }).collect(Collectors.toList());

        double totalObtained = subjects.stream().mapToDouble(SubjectResult::getMarksObtained).sum();
        double total         = subjects.stream().mapToDouble(SubjectResult::getTotalMarks).sum();
        double overallPct    = total == 0 ? 0 : (totalObtained / total) * 100;
        boolean hasFail      = subjects.stream().anyMatch(s -> "F".equals(s.getGrade()));

        return ResultCard.builder()
            .studentId(studentId)
            .studentName(student.getName())
            .rollNo(student.getRollNo())
            .branch(student.getBranch())
            .semester(student.getSemester())
            .examType(examType)
            .subjects(subjects)
            .totalObtained(totalObtained)
            .totalMarks(total)
            .percentage(Math.round(overallPct * 10.0) / 10.0)
            .overallGrade(computeOverallGrade(overallPct))
            .result(hasFail ? "FAIL" : "PASS")
            .build();
    }

    // ── Class-wide marks for a subject + exam type ────────────────────────
    public List<Marks> getSubjectMarks(Long subjectId, String examType) {
        return marksRepo.findBySubjectIdAndExamType(
            subjectId, Marks.ExamType.valueOf(examType.toUpperCase()));
    }

    // ── Grade boundaries ──────────────────────────────────────────────────
    private String computeOverallGrade(double pct) {
        if (pct >= 90) return "A+";
        if (pct >= 80) return "A";
        if (pct >= 70) return "B";
        if (pct >= 60) return "C";
        if (pct >= 50) return "D";
        return "F";
    }
}
