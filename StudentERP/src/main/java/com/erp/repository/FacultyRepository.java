package com.erp.repository;

import com.erp.model.Faculty;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface FacultyRepository extends JpaRepository<Faculty, Long> {

    Optional<Faculty> findByUser_Id(Long userId);
    List<Faculty> findByDepartment(String department);
    boolean existsByUser_Email(String email);

    @Query("""
        SELECT f FROM Faculty f
        JOIN f.user u
        WHERE f.active = true
          AND (LOWER(u.name)        LIKE LOWER(CONCAT('%', :q, '%'))
           OR LOWER(f.department)   LIKE LOWER(CONCAT('%', :q, '%'))
           OR LOWER(f.designation)  LIKE LOWER(CONCAT('%', :q, '%')))
        """)
    List<Faculty> search(@Param("q") String query);

    List<Faculty> findByActiveTrue();
    List<Faculty> findByDepartmentAndActiveTrue(String department);
}
