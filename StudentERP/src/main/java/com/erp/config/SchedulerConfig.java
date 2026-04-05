package com.erp.config;

import com.erp.service.FeeService;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.annotation.Configuration;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.scheduling.annotation.Scheduled;

@Configuration
@EnableScheduling
@RequiredArgsConstructor
public class SchedulerConfig {

    private static final Logger log = LoggerFactory.getLogger(SchedulerConfig.class);

    private final FeeService feeService;

    /**
     * Runs every day at midnight.
     * Marks all pending fees whose due date has passed as OVERDUE.
     */
    @Scheduled(cron = "0 0 0 * * *")
    public void checkOverdueFees() {
        int count = feeService.markOverdueFees();
        log.info("[Scheduler] Marked {} fees as OVERDUE", count);
    }
}
