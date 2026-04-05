package com.erp.config;

import com.erp.model.User;
import com.erp.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

/**
 * Seeds a default Admin account on first startup.
 * Remove or disable this class in production after initial setup.
 *
 * Default credentials:
 *   Email    : admin@college.edu
 *   Password : Admin@1234
 */
@Component
@RequiredArgsConstructor
public class DataInitializer implements CommandLineRunner {

    private static final Logger log = LoggerFactory.getLogger(DataInitializer.class);

    private final UserRepository userRepo;
    private final PasswordEncoder encoder;

    @Override
    public void run(String... args) {
        seedAdmin();
    }

    private void seedAdmin() {
        String adminEmail = "admin@college.edu";

        if (userRepo.existsByEmail(adminEmail)) {
            log.info("Admin user already exists — skipping seed");
            return;
        }

        User admin = User.builder()
            .name("System Administrator")
            .email(adminEmail)
            .password(encoder.encode("Admin@1234"))
            .role(User.Role.ADMIN)
            .active(true)
            .build();

        userRepo.save(admin);
        log.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        log.info("  Default admin created:");
        log.info("  Email    : {}", adminEmail);
        log.info("  Password : Admin@1234");
        log.info("  ⚠ Change this password immediately!");
        log.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
    }
}
