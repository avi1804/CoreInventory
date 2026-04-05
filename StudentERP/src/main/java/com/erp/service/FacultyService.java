package com.erp.service;

import com.erp.exception.ResourceNotFoundException;
import com.erp.model.*;
import com.erp.repository.*;
import lombok.*;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class FacultyService {

    private final FacultyRepository facultyRepo;
    private final UserRepository    userRepo;
    private final PasswordEncoder   encoder;

    // ── DTO ───────────────────────────────────────────────────────────────
    @Getter @Setter
    public static class FacultyRequest {
        private String name;
        private String email;
        private String password;
        private String department;
        private String designation;
        private String qualification;
        private String phone;
    }

    // ── Create faculty (also creates User record) ─────────────────────────
    @Transactional
    public Faculty createFaculty(FacultyRequest req) {

        if (userRepo.existsByEmail(req.getEmail()))
            throw new IllegalStateException("Email already registered: " + req.getEmail());

        User user = User.builder()
            .name(req.getName())
            .email(req.getEmail())
            .password(encoder.encode(req.getPassword()))
            .role(User.Role.FACULTY)
            .build();
        userRepo.save(user);

        Faculty faculty = Faculty.builder()
            .department(req.getDepartment())
            .designation(req.getDesignation())
            .qualification(req.getQualification())
            .phone(req.getPhone())
            .user(user)
            .active(true)
            .build();

        return facultyRepo.save(faculty);
    }

    // ── Get all active faculty ────────────────────────────────────────────
    public List<Faculty> getAllFaculty() {
        return facultyRepo.findByActiveTrue();
    }

    // ── Get by ID ─────────────────────────────────────────────────────────
    public Faculty getById(Long id) {
        return facultyRepo.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("Faculty", "id", id));
    }

    // ── Get by department ─────────────────────────────────────────────────
    public List<Faculty> getByDepartment(String department) {
        return facultyRepo.findByDepartmentAndActiveTrue(department);
    }

    // ── Search ────────────────────────────────────────────────────────────
    public List<Faculty> search(String query) {
        return facultyRepo.search(query);
    }

    // ── Update faculty profile ────────────────────────────────────────────
    @Transactional
    public Faculty updateFaculty(Long id, FacultyRequest req) {
        Faculty faculty = getById(id);

        if (req.getDepartment()   != null) faculty.setDepartment(req.getDepartment());
        if (req.getDesignation()  != null) faculty.setDesignation(req.getDesignation());
        if (req.getQualification()!= null) faculty.setQualification(req.getQualification());
        if (req.getPhone()        != null) faculty.setPhone(req.getPhone());

        // Update name on User record too
        if (req.getName() != null) {
            faculty.getUser().setName(req.getName());
            userRepo.save(faculty.getUser());
        }

        // Update password if provided
        if (req.getPassword() != null && !req.getPassword().isBlank()) {
            faculty.getUser().setPassword(encoder.encode(req.getPassword()));
            userRepo.save(faculty.getUser());
        }

        return facultyRepo.save(faculty);
    }

    // ── Soft-delete: deactivate faculty ───────────────────────────────────
    @Transactional
    public void deleteFaculty(Long id) {
        Faculty faculty = getById(id);
        faculty.setActive(false);
        faculty.getUser().setActive(false);
        userRepo.save(faculty.getUser());
        facultyRepo.save(faculty);
    }
}
