package com.erp.repository;

import com.erp.model.Fee;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.math.BigDecimal;
import java.util.List;

@Repository
public interface FeeRepository extends JpaRepository<Fee, Long> {

    List<Fee> findByStudentId(Long studentId);
    List<Fee> findByStatus(Fee.FeeStatus status);

    @Query("SELECT f FROM Fee f WHERE f.dueDate < CURRENT_DATE AND f.status = 'PENDING'")
    List<Fee> findOverdueFees();

    @Query("SELECT SUM(f.amount) FROM Fee f WHERE f.status = 'PAID'")
    BigDecimal totalCollected();
}
