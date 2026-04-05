package com.erp.controller;

import com.erp.dto.AuthDTOs.ApiResponse;
import com.erp.service.FeeService;
import com.erp.service.FeeService.FeeRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.http.*;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/fees")
@RequiredArgsConstructor
public class FeeController {

    private final FeeService feeService;

    // ── POST /api/fees  (Admin only)
    @PostMapping
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<ApiResponse> createFee(@RequestBody FeeRequest req) {
        var fee = feeService.createFee(req);
        return ResponseEntity.status(HttpStatus.CREATED)
            .body(ApiResponse.ok("Fee record created", fee));
    }

    // ── PUT /api/fees/{id}/pay  (Admin only)
    @PutMapping("/{id}/pay")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<ApiResponse> markPaid(@PathVariable Long id) {
        var fee = feeService.markPaid(id);
        return ResponseEntity.ok(ApiResponse.ok("Fee marked as paid. Receipt: "
            + fee.getReceiptNumber(), fee));
    }

    // ── GET /api/fees/student/{studentId}
    @GetMapping("/student/{studentId}")
    @PreAuthorize("hasAnyRole('ADMIN') or @authService.isSelf(#studentId)")
    public ResponseEntity<ApiResponse> getStudentFees(@PathVariable Long studentId) {
        return ResponseEntity.ok(
            ApiResponse.ok("Fees for student " + studentId,
                feeService.getStudentFees(studentId)));
    }

    // ── GET /api/fees/summary  (Admin only)
    @GetMapping("/summary")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<ApiResponse> getSummary() {
        return ResponseEntity.ok(ApiResponse.ok("Fee summary", feeService.getSummary()));
    }

    // ── POST /api/fees/mark-overdue  (Admin only, or trigger via scheduler)
    @PostMapping("/mark-overdue")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<ApiResponse> markOverdue() {
        int count = feeService.markOverdueFees();
        return ResponseEntity.ok(ApiResponse.ok(count + " fees marked overdue"));
    }

    // ── GET /api/fees/{id}/receipt  — returns PDF bytes
    @GetMapping("/{id}/receipt")
    public ResponseEntity<byte[]> downloadReceipt(@PathVariable Long id) throws Exception {
        byte[] pdf = feeService.generateReceipt(id);

        return ResponseEntity.ok()
            .header(HttpHeaders.CONTENT_DISPOSITION,
                    "attachment; filename=\"receipt-" + id + ".pdf\"")
            .contentType(MediaType.APPLICATION_PDF)
            .contentLength(pdf.length)
            .body(pdf);
    }
}
