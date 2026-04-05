package com.erp.service;

import com.erp.exception.ResourceNotFoundException;
import com.erp.model.*;
import com.erp.repository.*;
import lombok.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class SubjectService {

    private final SubjectRepository  subjectRepo;
    private final FacultyRepository  facultyRepo;

    // ── DTO ───────────────────────────────────────────────────────────────
    @Getter @Setter
    public static class SubjectRequest {
        private String  name;
        private String  code;
        private Integer semester;
        private String  branch;
        private Integer credits;
        private Long    facultyId;   // optional — assign faculty
    }

    // ── Create ────────────────────────────────────────────────────────────
    @Transactional
    public Subject createSubject(SubjectRequest req) {
        if (subjectRepo.existsByCode(req.getCode()))
            throw new IllegalStateException("Subject code already exists: " + req.getCode());

        Faculty faculty = null;
        if (req.getFacultyId() != null)
            faculty = facultyRepo.findById(req.getFacultyId())
                .orElseThrow(() -> new ResourceNotFoundException("Faculty", "id", req.getFacultyId()));

        Subject subject = Subject.builder()
            .name(req.getName())
            .code(req.getCode().toUpperCase())
            .semester(req.getSemester())
            .branch(req.getBranch())
            .credits(req.getCredits())
            .faculty(faculty)
            .build();

        return subjectRepo.save(subject);
    }

    // ── Get all ───────────────────────────────────────────────────────────
    public List<Subject> getAll() {
        return subjectRepo.findAll();
    }

    // ── Get by ID ─────────────────────────────────────────────────────────
    public Subject getById(Long id) {
        return subjectRepo.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("Subject", "id", id));
    }

    // ── Get by branch + semester ──────────────────────────────────────────
    public List<Subject> getByBranchAndSemester(String branch, int semester) {
        return subjectRepo.findByBranchAndSemester(branch, semester);
    }

    // ── Get by faculty ────────────────────────────────────────────────────
    public List<Subject> getByFaculty(Long facultyId) {
        return subjectRepo.findByFacultyId(facultyId);
    }

    // ── Update ────────────────────────────────────────────────────────────
    @Transactional
    public Subject updateSubject(Long id, SubjectRequest req) {
        Subject subject = getById(id);

        if (req.getName()     != null) subject.setName(req.getName());
        if (req.getSemester() != null) subject.setSemester(req.getSemester());
        if (req.getBranch()   != null) subject.setBranch(req.getBranch());
        if (req.getCredits()  != null) subject.setCredits(req.getCredits());

        if (req.getFacultyId() != null) {
            Faculty faculty = facultyRepo.findById(req.getFacultyId())
                .orElseThrow(() -> new ResourceNotFoundException("Faculty", "id", req.getFacultyId()));
            subject.setFaculty(faculty);
        }

        return subjectRepo.save(subject);
    }

    // ── Delete ────────────────────────────────────────────────────────────
    @Transactional
    public void deleteSubject(Long id) {
        Subject subject = getById(id);
        subjectRepo.delete(subject);
    }
}
