package com.erp.repository;

import com.erp.model.Student;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface StudentRepository extends JpaRepository<Student, Long> {

    Optional<Student> findByRollNo(String rollNo);
    Optional<Student> findByUser_Id(Long userId);
    List<Student> findByBranchAndSemester(String branch, int semester);
    List<Student> findByStatus(Student.AdmissionStatus status);
    boolean existsByRollNo(String rollNo);
    List<Student> findByStatusNot(Student.AdmissionStatus status);
    List<Student> findByBranchAndSemesterAndStatusNot(String branch, int semester, Student.AdmissionStatus status);

    @Query("""
        SELECT s FROM Student s
        JOIN s.user u
        WHERE s.status <> 'DROPPED'
          AND (LOWER(u.name)   LIKE LOWER(CONCAT('%', :q, '%'))
           OR LOWER(s.rollNo) LIKE LOWER(CONCAT('%', :q, '%'))
           OR LOWER(s.branch) LIKE LOWER(CONCAT('%', :q, '%')))
        """)
    List<Student> search(@Param("q") String query);
}
