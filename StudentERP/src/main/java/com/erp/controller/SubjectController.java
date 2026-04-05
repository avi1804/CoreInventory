package com.erp.controller;

import com.erp.dto.AuthDTOs.ApiResponse;
import com.erp.service.SubjectService;
import com.erp.service.SubjectService.SubjectRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/subjects")
@RequiredArgsConstructor
public class SubjectController {

    private final SubjectService subjectService;

    @PostMapping
    public ResponseEntity<ApiResponse> create(@RequestBody SubjectRequest req) {
        var subject = subjectService.createSubject(req);
        return ResponseEntity.status(HttpStatus.CREATED)
            .body(ApiResponse.ok("Subject created", subject));
    }

    @GetMapping
    public ResponseEntity<ApiResponse> getAll() {
        return ResponseEntity.ok(ApiResponse.ok("All subjects", subjectService.getAll()));
    }

    @GetMapping("/{id}")
    public ResponseEntity<ApiResponse> getById(@PathVariable Long id) {
        return ResponseEntity.ok(ApiResponse.ok("Subject", subjectService.getById(id)));
    }

    @GetMapping("/class")
    public ResponseEntity<ApiResponse> getByClass(
            @RequestParam String branch,
            @RequestParam int    semester) {
        var list = subjectService.getByBranchAndSemester(branch, semester);
        return ResponseEntity.ok(
            ApiResponse.ok(list.size() + " subjects for " + branch + " Sem " + semester, list));
    }

    @GetMapping("/faculty/{facultyId}")
    public ResponseEntity<ApiResponse> getByFaculty(@PathVariable Long facultyId) {
        return ResponseEntity.ok(ApiResponse.ok("Subjects by faculty", subjectService.getByFaculty(facultyId)));
    }

    @PutMapping("/{id}")
    public ResponseEntity<ApiResponse> update(
            @PathVariable Long id,
            @RequestBody SubjectRequest req) {
        return ResponseEntity.ok(ApiResponse.ok("Subject updated", subjectService.updateSubject(id, req)));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<ApiResponse> delete(@PathVariable Long id) {
        subjectService.deleteSubject(id);
        return ResponseEntity.ok(ApiResponse.ok("Subject deleted"));
    }
}