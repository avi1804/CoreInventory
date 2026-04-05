package com.erp.service;

import com.erp.dto.AuthDTOs.RegisterRequest;
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
public class StudentService {

    private final StudentRepository studentRepo;
    private final UserRepository    userRepo;
    private final PasswordEncoder   encoder;

    // ── DTO ───────────────────────────────────────────────────────────────
    @Getter @Setter
    public static class StudentRequest {
        private String  name;
        private String  email;
        private String  password;
        private String  rollNo;
        private String  branch;
        private Integer semester;
        private String  phone;
        private String  address;
        private String  guardianName;
        private String  guardianPhone;
    }

    // ── Create student (also creates User record) ─────────────────────────
    @Transactional
    public Student createStudent(StudentRequest req) {

        if (userRepo.existsByEmail(req.getEmail()))
            throw new IllegalStateException("Email already registered: " + req.getEmail());

        if (studentRepo.existsByRollNo(req.getRollNo()))
            throw new IllegalStateException("Roll number already exists: " + req.getRollNo());

        User user = User.builder()
            .name(req.getName())
            .email(req.getEmail())
            .password(encoder.encode(req.getPassword()))
            .role(User.Role.STUDENT)
            .build();
        userRepo.save(user);

        Student student = Student.builder()
            .rollNo(req.getRollNo())
            .branch(req.getBranch())
            .semester(req.getSemester())
            .phone(req.getPhone())
            .address(req.getAddress())
            .guardianName(req.getGuardianName())
            .guardianPhone(req.getGuardianPhone())
            .user(user)
            .status(Student.AdmissionStatus.ACTIVE)
            .build();

        return studentRepo.save(student);
    }

    // ── Get all students (exclude soft-deleted / DROPPED) ────────────────
    public List<Student> getAllStudents() {
        return studentRepo.findByStatusNot(Student.AdmissionStatus.DROPPED);
    }

    // ── Get by ID ─────────────────────────────────────────────────────────
    public Student getById(Long id) {
        return studentRepo.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("Student", "id", id));
    }

    // ── Get by roll number ────────────────────────────────────────────────
    public Student getByRollNo(String rollNo) {
        return studentRepo.findByRollNo(rollNo)
            .orElseThrow(() -> new ResourceNotFoundException("Student", "rollNo", rollNo));
    }

    // ── Search students ───────────────────────────────────────────────────
    public List<Student> search(String query) {
        return studentRepo.search(query);
    }

    // ── Get students by branch + semester (exclude DROPPED) ──────────────
    public List<Student> getByBranchAndSemester(String branch, int semester) {
        return studentRepo.findByBranchAndSemesterAndStatusNot(
            branch, semester, Student.AdmissionStatus.DROPPED);
    }

    // ── Update student profile ────────────────────────────────────────────
    @Transactional
    public Student updateStudent(Long id, StudentRequest req) {
        Student student = getById(id);

        if (req.getBranch()       != null) student.setBranch(req.getBranch());
        if (req.getSemester()     != null) student.setSemester(req.getSemester());
        if (req.getPhone()        != null) student.setPhone(req.getPhone());
        if (req.getAddress()      != null) student.setAddress(req.getAddress());
        if (req.getGuardianName() != null) student.setGuardianName(req.getGuardianName());
        if (req.getGuardianPhone()!= null) student.setGuardianPhone(req.getGuardianPhone());

        // Update name on the User record too
        if (req.getName() != null) {
            student.getUser().setName(req.getName());
            userRepo.save(student.getUser());
        }

        return studentRepo.save(student);
    }

    // ── Update admission status ───────────────────────────────────────────
    @Transactional
    public Student updateStatus(Long id, String status) {
        Student student = getById(id);
        student.setStatus(Student.AdmissionStatus.valueOf(status.toUpperCase()));
        return studentRepo.save(student);
    }

    // ── Soft-delete: deactivate ───────────────────────────────────────────
    @Transactional
    public void deactivateStudent(Long id) {
        Student student = getById(id);
        student.setStatus(Student.AdmissionStatus.DROPPED);
        student.getUser().setActive(false);
        userRepo.save(student.getUser());
        studentRepo.save(student);
    }
}
