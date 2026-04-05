package com.erp.repository;

import com.erp.model.Marks;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface MarksRepository extends JpaRepository<Marks, Long> {

    List<Marks> findByStudentId(Long studentId);
    List<Marks> findByStudentIdAndExamType(Long studentId, Marks.ExamType examType);
    List<Marks> findBySubjectIdAndExamType(Long subjectId, Marks.ExamType examType);

    Optional<Marks> findByStudentIdAndSubjectIdAndExamType(
            Long studentId, Long subjectId, Marks.ExamType examType);
}
