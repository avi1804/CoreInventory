package com.erp.dto;

import jakarta.validation.constraints.*;
import lombok.*;

// ── Login request payload ─────────────────────────────────────────────────
public class AuthDTOs {

    @Getter @Setter @NoArgsConstructor @AllArgsConstructor
    public static class LoginRequest {

        @Email(message = "Must be a valid email address")
        @NotBlank(message = "Email is required")
        private String email;

        @NotBlank(message = "Password is required")
        @Size(min = 6, message = "Password must be at least 6 characters")
        private String password;
    }

    // ── JWT response payload ──────────────────────────────────────────────
    @Getter @Builder
    public static class JwtResponse {
        private final String  token;
        private final String  type  = "Bearer";
        private final Long    id;
        private final String  name;
        private final String  email;
        private final String  role;
    }

    // ── Register request payload ──────────────────────────────────────────
    @Getter @Setter @NoArgsConstructor @AllArgsConstructor
    public static class RegisterRequest {

        @NotBlank private String name;

        @Email @NotBlank
        private String email;

        @NotBlank @Size(min = 8)
        private String password;

        @NotBlank
        private String role;   // ADMIN | FACULTY | STUDENT

        // Student-specific (required only when role == STUDENT)
        private String rollNo;
        private String branch;
        private Integer semester;

        // Faculty-specific (required only when role == FACULTY)
        private String department;
        private String designation;
    }

    // ── Generic API response wrapper ──────────────────────────────────────
    @Getter @Builder
    public static class ApiResponse {
        private final boolean success;
        private final String  message;
        private final Object  data;

        public static ApiResponse ok(String msg, Object data) {
            return ApiResponse.builder().success(true).message(msg).data(data).build();
        }
        public static ApiResponse ok(String msg) {
            return ok(msg, null);
        }
        public static ApiResponse error(String msg) {
            return ApiResponse.builder().success(false).message(msg).build();
        }
    }
}
