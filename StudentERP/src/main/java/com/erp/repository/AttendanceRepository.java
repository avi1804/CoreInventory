package com.erp.repository;

import com.erp.model.Attendance;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

@Repository
public interface AttendanceRepository extends JpaRepository<Attendance, Long> {

    List<Attendance> findByStudentIdAndSubjectId(Long studentId, Long subjectId);
    List<Attendance> findByStudentId(Long studentId);
    List<Attendance> findBySubjectIdAndDate(Long subjectId, LocalDate date);

    Optional<Attendance> findByStudentIdAndSubjectIdAndDate(
            Long studentId, Long subjectId, LocalDate date);

    @Query("""
        SELECT
          COUNT(a)                                               AS total,
          SUM(CASE WHEN a.status = 'PRESENT' THEN 1 ELSE 0 END) AS present
        FROM Attendance a
        WHERE a.student.id = :studentId
          AND a.subject.id = :subjectId
        """)
    Object[] getAttendanceCounts(
            @Param("studentId") Long studentId,
            @Param("subjectId")  Long subjectId);
}
