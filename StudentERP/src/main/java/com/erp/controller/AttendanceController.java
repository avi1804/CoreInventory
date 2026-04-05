package com.erp.controller;

import com.erp.dto.AuthDTOs.ApiResponse;
import com.erp.service.AttendanceService;
import com.erp.service.AttendanceService.*;
import lombok.RequiredArgsConstructor;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.List;

@RestController
@RequestMapping("/api/attendance")
@RequiredArgsConstructor
public class AttendanceController {

    private final AttendanceService attendanceService;

    @PostMapping("/mark")
    public ResponseEntity<ApiResponse> markAttendance(@RequestBody AttendanceRequest req) {
        return ResponseEntity.ok(ApiResponse.ok("Attendance marked", attendanceService.markAttendance(req)));
    }

    @PostMapping("/mark-bulk")
    public ResponseEntity<ApiResponse> markBulk(@RequestBody List<AttendanceRequest> requests) {
        var result = attendanceService.markBulkAttendance(requests);
        return ResponseEntity.ok(ApiResponse.ok(result.size() + " records saved", result));
    }

    @GetMapping("/student/{studentId}")
    public ResponseEntity<ApiResponse> getStudentAttendance(@PathVariable Long studentId) {
        return ResponseEntity.ok(ApiResponse.ok("Student attendance", attendanceService.getStudentAttendance(studentId)));
    }

    @GetMapping("/report")
    public ResponseEntity<ApiResponse> getReport(
            @RequestParam Long studentId,
            @RequestParam Long subjectId) {
        return ResponseEntity.ok(ApiResponse.ok("Attendance report", attendanceService.getAttendanceReport(studentId, subjectId)));
    }

    @GetMapping("/full-report/{studentId}")
    public ResponseEntity<ApiResponse> getFullReport(@PathVariable Long studentId) {
        return ResponseEntity.ok(ApiResponse.ok("Full attendance report", attendanceService.getFullStudentReport(studentId)));
    }

    @GetMapping("/class")
    public ResponseEntity<ApiResponse> getClassAttendance(
            @RequestParam Long subjectId,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate date) {
        return ResponseEntity.ok(ApiResponse.ok("Class attendance on " + date, attendanceService.getClassAttendance(subjectId, date)));
    }

    @GetMapping("/low")
    public ResponseEntity<ApiResponse> getLowAttendance(
            @RequestParam String branch,
            @RequestParam int    semester,
            @RequestParam Long   subjectId,
            @RequestParam(defaultValue = "75") double threshold) {
        var result = attendanceService.getLowAttendanceStudents(branch, semester, subjectId, threshold);
        return ResponseEntity.ok(ApiResponse.ok(result.size() + " students below " + threshold + "%", result));
    }
}