package com.erp.controller;

import com.erp.dto.AuthDTOs.ApiResponse;
import com.erp.service.FacultyService;
import com.erp.service.FacultyService.FacultyRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/faculty")
@RequiredArgsConstructor
public class FacultyController {

    private final FacultyService facultyService;

    // POST /api/faculty
    @PostMapping
    public ResponseEntity<ApiResponse> createFaculty(@RequestBody FacultyRequest req) {
        var faculty = facultyService.createFaculty(req);
        return ResponseEntity.status(HttpStatus.CREATED)
            .body(ApiResponse.ok("Faculty added successfully", faculty));
    }

    // GET /api/faculty
    @GetMapping
    public ResponseEntity<ApiResponse> getAllFaculty() {
        return ResponseEntity.ok(
            ApiResponse.ok("All faculty", facultyService.getAllFaculty()));
    }

    // GET /api/faculty/{id}
    @GetMapping("/{id}")
    public ResponseEntity<ApiResponse> getFaculty(@PathVariable Long id) {
        return ResponseEntity.ok(
            ApiResponse.ok("Faculty details", facultyService.getById(id)));
    }

    // GET /api/faculty/department/{dept}
    @GetMapping("/department/{dept}")
    public ResponseEntity<ApiResponse> getByDepartment(@PathVariable String dept) {
        var list = facultyService.getByDepartment(dept);
        return ResponseEntity.ok(
            ApiResponse.ok(list.size() + " faculty in " + dept, list));
    }

    // GET /api/faculty/search?q=...
    @GetMapping("/search")
    public ResponseEntity<ApiResponse> search(@RequestParam String q) {
        var results = facultyService.search(q);
        return ResponseEntity.ok(
            ApiResponse.ok(results.size() + " results for: " + q, results));
    }

    // PUT /api/faculty/{id}
    @PutMapping("/{id}")
    public ResponseEntity<ApiResponse> updateFaculty(
            @PathVariable Long id,
            @RequestBody FacultyRequest req) {
        var updated = facultyService.updateFaculty(id, req);
        return ResponseEntity.ok(ApiResponse.ok("Faculty updated", updated));
    }

    // DELETE /api/faculty/{id}
    @DeleteMapping("/{id}")
    public ResponseEntity<ApiResponse> deleteFaculty(@PathVariable Long id) {
        facultyService.deleteFaculty(id);
        return ResponseEntity.ok(ApiResponse.ok("Faculty removed successfully"));
    }
}