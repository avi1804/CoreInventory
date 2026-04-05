package com.erp.service;

import com.erp.exception.ResourceNotFoundException;
import com.erp.model.*;
import com.erp.repository.*;
import com.itextpdf.text.BaseColor;
import com.itextpdf.text.Document;
import com.itextpdf.text.Element;
import com.itextpdf.text.Font;
import com.itextpdf.text.PageSize;
import com.itextpdf.text.Paragraph;
import com.itextpdf.text.Phrase;
import com.itextpdf.text.Rectangle;
import com.itextpdf.text.pdf.PdfPCell;
import com.itextpdf.text.pdf.PdfPTable;
import com.itextpdf.text.pdf.PdfWriter;
import lombok.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.io.ByteArrayOutputStream;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.*;

@Service
@RequiredArgsConstructor
public class FeeService {

    private final FeeRepository     feeRepo;
    private final StudentRepository studentRepo;

    // ── DTOs ──────────────────────────────────────────────────────────────

    @Getter @Setter
    public static class FeeRequest {
        private Long       studentId;
        private BigDecimal amount;
        private String     dueDate;     // yyyy-MM-dd
        private String     feeType;     // TUITION, HOSTEL, EXAM, LIBRARY
    }

    @Getter @Builder
    public static class FeeSummary {
        private BigDecimal totalCollected;
        private BigDecimal totalPending;
        private long       paidCount;
        private long       pendingCount;
        private long       overdueCount;
    }

    // ── Create a fee record ───────────────────────────────────────────────
    @Transactional
    public Fee createFee(FeeRequest req) {
        Student student = studentRepo.findById(req.getStudentId())
            .orElseThrow(() -> new ResourceNotFoundException(
                "Student", "id", req.getStudentId()));

        Fee fee = Fee.builder()
            .student(student)
            .amount(req.getAmount())
            .dueDate(LocalDate.parse(req.getDueDate()))
            .feeType(req.getFeeType())
            .status(Fee.FeeStatus.PENDING)
            .build();

        return feeRepo.save(fee);
    }

    // ── Mark a fee as paid ────────────────────────────────────────────────
    @Transactional
    public Fee markPaid(Long feeId) {
        Fee fee = feeRepo.findById(feeId)
            .orElseThrow(() -> new ResourceNotFoundException("Fee", "id", feeId));

        fee.setStatus(Fee.FeeStatus.PAID);
        fee.setPaidDate(LocalDate.now());
        fee.setReceiptNumber("RCPT-" + System.currentTimeMillis());

        return feeRepo.save(fee);
    }

    // ── Update overdue status (call via @Scheduled nightly) ───────────────
    @Transactional
    public int markOverdueFees() {
        List<Fee> overdue = feeRepo.findOverdueFees();
        overdue.forEach(f -> f.setStatus(Fee.FeeStatus.OVERDUE));
        feeRepo.saveAll(overdue);
        return overdue.size();
    }

    // ── Get all fees for a student ────────────────────────────────────────
    public List<Fee> getStudentFees(Long studentId) {
        return feeRepo.findByStudentId(studentId);
    }

    // ── Dashboard summary ─────────────────────────────────────────────────
    public FeeSummary getSummary() {
        List<Fee> all = feeRepo.findAll();
        return FeeSummary.builder()
            .totalCollected(feeRepo.totalCollected())
            .totalPending(all.stream()
                .filter(f -> f.getStatus() != Fee.FeeStatus.PAID)
                .map(Fee::getAmount)
                .reduce(BigDecimal.ZERO, BigDecimal::add))
            .paidCount   (all.stream().filter(f -> f.getStatus() == Fee.FeeStatus.PAID   ).count())
            .pendingCount(all.stream().filter(f -> f.getStatus() == Fee.FeeStatus.PENDING).count())
            .overdueCount(all.stream().filter(f -> f.getStatus() == Fee.FeeStatus.OVERDUE).count())
            .build();
    }

    // ── Generate PDF receipt with iText ──────────────────────────────────
    public byte[] generateReceipt(Long feeId) throws Exception {
        Fee fee = feeRepo.findById(feeId)
            .orElseThrow(() -> new ResourceNotFoundException("Fee", "id", feeId));

        if (fee.getStatus() != Fee.FeeStatus.PAID) {
            throw new IllegalStateException("Receipt can only be generated for paid fees");
        }

        ByteArrayOutputStream out = new ByteArrayOutputStream();
        Document doc = new Document(PageSize.A4, 50, 50, 60, 60);
        PdfWriter.getInstance(doc, out);
        doc.open();

        // ── Fonts
        Font titleFont   = new Font(Font.FontFamily.HELVETICA, 18, Font.BOLD);
        Font headerFont  = new Font(Font.FontFamily.HELVETICA, 12, Font.BOLD);
        Font normalFont  = new Font(Font.FontFamily.HELVETICA, 11, Font.NORMAL);
        Font mutedFont   = new Font(Font.FontFamily.HELVETICA, 9,  Font.NORMAL, BaseColor.GRAY);

        // ── Header
        Paragraph title = new Paragraph("StudentERP – Fee Receipt", titleFont);
        title.setAlignment(Element.ALIGN_CENTER);
        doc.add(title);
        doc.add(new Paragraph(" "));

        // ── Receipt meta table
        PdfPTable metaTable = new PdfPTable(2);
        metaTable.setWidthPercentage(100);
        addReceiptRow(metaTable, "Receipt No",  fee.getReceiptNumber(), headerFont, normalFont);
        addReceiptRow(metaTable, "Date Paid",
            fee.getPaidDate().format(DateTimeFormatter.ofPattern("dd MMM yyyy")),
            headerFont, normalFont);
        doc.add(metaTable);
        doc.add(new Paragraph(" "));

        // ── Student details
        Student s = fee.getStudent();
        doc.add(new Paragraph("Student Details", headerFont));
        doc.add(new Paragraph("Name    : " + s.getName(),  normalFont));
        doc.add(new Paragraph("Roll No : " + s.getRollNo(), normalFont));
        doc.add(new Paragraph("Branch  : " + s.getBranch() + " | Sem: " + s.getSemester(), normalFont));
        doc.add(new Paragraph(" "));

        // ── Fee breakdown table
        PdfPTable feeTable = new PdfPTable(3);
        feeTable.setWidthPercentage(100);
        feeTable.setWidths(new float[]{3f, 2f, 2f});

        // header row
        addTableHeader(feeTable, "Description", "Due Date", "Amount (₹)");

        // data row
        addTableCell(feeTable, fee.getFeeType() != null ? fee.getFeeType() : "Tuition Fee", normalFont);
        addTableCell(feeTable, fee.getDueDate().format(DateTimeFormatter.ofPattern("dd MMM yyyy")), normalFont);
        addTableCell(feeTable, "₹ " + fee.getAmount().toPlainString(), normalFont);

        // total row
        PdfPCell totalLabel = new PdfPCell(new Phrase("Total Paid", headerFont));
        totalLabel.setColspan(2);
        totalLabel.setHorizontalAlignment(Element.ALIGN_RIGHT);
        totalLabel.setPadding(6);
        feeTable.addCell(totalLabel);

        PdfPCell totalVal = new PdfPCell(new Phrase("₹ " + fee.getAmount().toPlainString(), headerFont));
        totalVal.setHorizontalAlignment(Element.ALIGN_CENTER);
        totalVal.setPadding(6);
        feeTable.addCell(totalVal);

        doc.add(feeTable);
        doc.add(new Paragraph(" "));
        doc.add(new Paragraph("Thank you for your payment. This is a computer-generated receipt.", mutedFont));

        doc.close();
        return out.toByteArray();
    }

    // ── Helpers ───────────────────────────────────────────────────────────
    private void addReceiptRow(PdfPTable t, String k, String v, Font kf, Font vf) {
        PdfPCell kc = new PdfPCell(new Phrase(k, kf)); kc.setBorder(Rectangle.NO_BORDER); kc.setPadding(4); t.addCell(kc);
        PdfPCell vc = new PdfPCell(new Phrase(v, vf)); vc.setBorder(Rectangle.NO_BORDER); vc.setPadding(4); t.addCell(vc);
    }

    private void addTableHeader(PdfPTable t, String... headers) {
        Font f = new Font(Font.FontFamily.HELVETICA, 11, Font.BOLD, BaseColor.WHITE);
        for (String h : headers) {
            PdfPCell c = new PdfPCell(new Phrase(h, f));
            c.setBackgroundColor(new BaseColor(30, 80, 150));
            c.setPadding(7); c.setHorizontalAlignment(Element.ALIGN_CENTER);
            t.addCell(c);
        }
    }

    private void addTableCell(PdfPTable t, String text, Font f) {
        PdfPCell c = new PdfPCell(new Phrase(text, f));
        c.setPadding(6); c.setHorizontalAlignment(Element.ALIGN_CENTER);
        t.addCell(c);
    }
}
