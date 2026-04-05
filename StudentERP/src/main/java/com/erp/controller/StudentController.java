package com.erp.controller;

import com.erp.dto.AuthDTOs.ApiResponse;
import com.erp.service.StudentService;
import com.erp.service.StudentService.StudentRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.http.*;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/students")
@RequiredArgsConstructor
public class StudentController {

    private final StudentService studentService;

    // ── POST /api/students  (Admin only)
    @PostMapping
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<ApiResponse> createStudent(@RequestBody StudentRequest req) {
        var student = studentService.createStudent(req);
        return ResponseEntity.status(HttpStatus.CREATED)
            .body(ApiResponse.ok("Student enrolled successfully", student));
    }

    // ── GET /api/students
    @GetMapping
    @PreAuthorize("hasAnyRole('ADMIN', 'FACULTY')")
    public ResponseEntity<ApiResponse> getAllStudents() {
        return ResponseEntity.ok(
            ApiResponse.ok("All students", studentService.getAllStudents()));
    }

    // ── GET /api/students/{id}
    @GetMapping("/{id}")
    public ResponseEntity<ApiResponse> getStudent(@PathVariable Long id) {
        return ResponseEntity.ok(
            ApiResponse.ok("Student details", studentService.getById(id)));
    }

    // ── GET /api/students/roll/{rollNo}
    @GetMapping("/roll/{rollNo}")
    public ResponseEntity<ApiResponse> getByRollNo(@PathVariable String rollNo) {
        return ResponseEntity.ok(
            ApiResponse.ok("Student found", studentService.getByRollNo(rollNo)));
    }

    // ── GET /api/students/search?q=anika
    @GetMapping("/search")
    @PreAuthorize("hasAnyRole('ADMIN', 'FACULTY')")
    public ResponseEntity<ApiResponse> search(@RequestParam String q) {
        var results = studentService.search(q);
        return ResponseEntity.ok(
            ApiResponse.ok(results.size() + " results for: " + q, results));
    }

    // ── GET /api/students/class?branch=CSE&semester=3
    @GetMapping("/class")
    @PreAuthorize("hasAnyRole('ADMIN', 'FACULTY')")
    public ResponseEntity<ApiResponse> getClass(
            @RequestParam String branch,
            @RequestParam int    semester) {
        var students = studentService.getByBranchAndSemester(branch, semester);
        return ResponseEntity.ok(
            ApiResponse.ok(students.size() + " students in " + branch + " Sem " + semester,
                students));
    }

    // ── PUT /api/students/{id}  (Admin only)
    @PutMapping("/{id}")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<ApiResponse> updateStudent(
            @PathVariable Long id,
            @RequestBody StudentRequest req) {
        var updated = studentService.updateStudent(id, req);
        return ResponseEntity.ok(ApiResponse.ok("Student updated", updated));
    }

    // ── PATCH /api/students/{id}/status?status=GRADUATED  (Admin only)
    @PatchMapping("/{id}/status")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<ApiResponse> updateStatus(
            @PathVariable Long id,
            @RequestParam String status) {
        var updated = studentService.updateStatus(id, status);
        return ResponseEntity.ok(ApiResponse.ok("Status updated to " + status, updated));
    }

    // ── DELETE /api/students/{id}  (Admin only — soft delete)
    @DeleteMapping("/{id}")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<ApiResponse> deleteStudent(@PathVariable Long id) {
        studentService.deactivateStudent(id);
        return ResponseEntity.ok(ApiResponse.ok("Student deactivated"));
    }
}
