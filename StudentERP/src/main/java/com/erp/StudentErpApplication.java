package com.erp;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.data.jpa.repository.config.EnableJpaAuditing;

@SpringBootApplication
@EnableJpaAuditing
public class StudentErpApplication {

    public static void main(String[] args) {
        SpringApplication.run(StudentErpApplication.class, args);
    }
}
