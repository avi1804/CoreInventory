package com.erp.service;

import com.erp.exception.ResourceNotFoundException;
import com.erp.model.*;
import com.erp.repository.*;
import lombok.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.util.*;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class AttendanceService {

    private final AttendanceRepository attendanceRepo;
    private final StudentRepository    studentRepo;
    private final SubjectRepository    subjectRepo;

    // ── DTO ───────────────────────────────────────────────────────────────
    @Getter @Setter
    public static class AttendanceRequest {
        private Long   studentId;
        private Long   subjectId;
        private String date;    // yyyy-MM-dd
        private String status;  // PRESENT | ABSENT | LATE
    }

    @Getter @Builder
    public static class AttendanceReport {
        private Long   studentId;
        private String studentName;
        private String rollNo;
        private Long   subjectId;
        private String subjectName;
        private long   totalClasses;
        private long   present;
        private long   absent;
        private double percentage;
        private String remark;  // GOOD | WARNING | CRITICAL
    }

    // ── Mark attendance for a single student ─────────────────────────────
    @Transactional
    public Attendance markAttendance(AttendanceRequest req) {
        LocalDate date = LocalDate.parse(req.getDate());

        Student student = studentRepo.findById(req.getStudentId())
            .orElseThrow(() -> new ResourceNotFoundException("Student", "id", req.getStudentId()));

        Subject subject = subjectRepo.findById(req.getSubjectId())
            .orElseThrow(() -> new ResourceNotFoundException("Subject", "id", req.getSubjectId()));

        // Upsert: update existing record or create new
        Attendance attendance = attendanceRepo
            .findByStudentIdAndSubjectIdAndDate(req.getStudentId(), req.getSubjectId(), date)
            .orElseGet(() -> Attendance.builder()
                .student(student)
                .subject(subject)
                .date(date)
                .build());

        attendance.setStatus(Attendance.AttendanceStatus.valueOf(req.getStatus().toUpperCase()));
        return attendanceRepo.save(attendance);
    }

    // ── Bulk mark (an entire class at once) ───────────────────────────────
    @Transactional
    public List<Attendance> markBulkAttendance(List<AttendanceRequest> requests) {
        return requests.stream()
            .map(this::markAttendance)
            .collect(Collectors.toList());
    }

    // ── Get all records for one student ──────────────────────────────────
    public List<Attendance> getStudentAttendance(Long studentId) {
        return attendanceRepo.findByStudentId(studentId);
    }

    // ── Attendance report per student per subject ─────────────────────────
    public AttendanceReport getAttendanceReport(Long studentId, Long subjectId) {
        Student student = studentRepo.findById(studentId)
            .orElseThrow(() -> new ResourceNotFoundException("Student", "id", studentId));

        Subject subject = subjectRepo.findById(subjectId)
            .orElseThrow(() -> new ResourceNotFoundException("Subject", "id", subjectId));

        Object[] counts = attendanceRepo.getAttendanceCounts(studentId, subjectId);
        long total   = counts[0] != null ? ((Number) counts[0]).longValue() : 0L;
        long present = counts[1] != null ? ((Number) counts[1]).longValue() : 0L;
        long absent  = total - present;
        double pct   = total == 0 ? 0.0 : (present * 100.0 / total);

        String remark;
        if      (pct >= 80) remark = "GOOD";
        else if (pct >= 65) remark = "WARNING";
        else                remark = "CRITICAL";

        return AttendanceReport.builder()
            .studentId(studentId)
            .studentName(student.getName())
            .rollNo(student.getRollNo())
            .subjectId(subjectId)
            .subjectName(subject.getName())
            .totalClasses(total)
            .present(present)
            .absent(absent)
            .percentage(Math.round(pct * 10.0) / 10.0)
            .remark(remark)
            .build();
    }

    // ── Full report for a student across all subjects ─────────────────────
    public List<AttendanceReport> getFullStudentReport(Long studentId) {
        List<Attendance> records = attendanceRepo.findByStudentId(studentId);
        return records.stream()
            .map(a -> a.getSubject().getId())
            .distinct()
            .map(subjectId -> getAttendanceReport(studentId, subjectId))
            .collect(Collectors.toList());
    }

    // ── Get class attendance for a specific date & subject ────────────────
    public List<Attendance> getClassAttendance(Long subjectId, LocalDate date) {
        return attendanceRepo.findBySubjectIdAndDate(subjectId, date);
    }

    // ── Students with attendance below threshold ───────────────────────────
    public List<AttendanceReport> getLowAttendanceStudents(
            String branch, int semester, Long subjectId, double threshold) {
        return studentRepo.findByBranchAndSemester(branch, semester).stream()
            .map(s -> getAttendanceReport(s.getId(), subjectId))
            .filter(r -> r.getPercentage() < threshold)
            .sorted(Comparator.comparingDouble(AttendanceReport::getPercentage))
            .collect(Collectors.toList());
    }
}
