package com.erp.controller;

import com.erp.dto.AuthDTOs.ApiResponse;
import com.erp.service.MarksService;
import com.erp.service.MarksService.MarksRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/marks")
@RequiredArgsConstructor
public class MarksController {

    private final MarksService marksService;

    @PostMapping("/enter")
    public ResponseEntity<ApiResponse> enterMarks(@RequestBody MarksRequest req) {
        return ResponseEntity.status(HttpStatus.CREATED)
            .body(ApiResponse.ok("Marks saved", marksService.enterMarks(req)));
    }

    @PostMapping("/enter-bulk")
    public ResponseEntity<ApiResponse> enterBulkMarks(@RequestBody List<MarksRequest> requests) {
        var result = marksService.enterBulkMarks(requests);
        return ResponseEntity.ok(ApiResponse.ok(result.size() + " marks records saved", result));
    }

    @GetMapping("/result")
    public ResponseEntity<ApiResponse> getResultCard(
            @RequestParam Long   studentId,
            @RequestParam String examType) {
        return ResponseEntity.ok(ApiResponse.ok("Result card", marksService.getResultCard(studentId, examType)));
    }

    @GetMapping("/subject")
    public ResponseEntity<ApiResponse> getSubjectMarks(
            @RequestParam Long   subjectId,
            @RequestParam String examType) {
        return ResponseEntity.ok(ApiResponse.ok("Subject marks", marksService.getSubjectMarks(subjectId, examType)));
    }
}