package com.erp.repository;

import com.erp.model.Subject;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface SubjectRepository extends JpaRepository<Subject, Long> {

    List<Subject> findByBranchAndSemester(String branch, int semester);
    List<Subject> findByBranch(String branch);
    List<Subject> findByFacultyId(Long facultyId);
    Optional<Subject> findByCode(String code);
    boolean existsByCode(String code);
}
