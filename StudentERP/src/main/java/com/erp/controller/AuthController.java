package com.erp.controller;

import com.erp.dto.AuthDTOs.*;
import com.erp.model.*;
import com.erp.repository.UserRepository;
import com.erp.security.*;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.*;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthenticationManager authManager;
    private final UserRepository        userRepo;
    private final PasswordEncoder       encoder;
    private final JwtUtils              jwtUtils;

    // ── POST /api/auth/login ──────────────────────────────────────────────
    @PostMapping("/login")
    public ResponseEntity<JwtResponse> login(@Valid @RequestBody LoginRequest req) {

        Authentication auth = authManager.authenticate(
            new UsernamePasswordAuthenticationToken(req.getEmail(), req.getPassword()));

        SecurityContextHolder.getContext().setAuthentication(auth);

        String jwt = jwtUtils.generateJwtToken(auth);

        UserDetailsImpl user = (UserDetailsImpl) auth.getPrincipal();

        return ResponseEntity.ok(JwtResponse.builder()
            .token(jwt)
            .id(user.getId())
            .name(user.getName())
            .email(user.getEmail())
            .role(user.getRole())
            .build());
    }

    // ── POST /api/auth/register ───────────────────────────────────────────
    @PostMapping("/register")
    public ResponseEntity<ApiResponse> register(@Valid @RequestBody RegisterRequest req) {

        if (userRepo.existsByEmail(req.getEmail())) {
            return ResponseEntity.badRequest()
                .body(ApiResponse.error("Email already in use"));
        }

        User.Role role;
        try {
            role = User.Role.valueOf(req.getRole().toUpperCase());
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest()
                .body(ApiResponse.error("Invalid role. Use: ADMIN, FACULTY, STUDENT"));
        }

        User user = User.builder()
            .name(req.getName())
            .email(req.getEmail())
            .password(encoder.encode(req.getPassword()))
            .role(role)
            .build();

        userRepo.save(user);

        return ResponseEntity.ok(ApiResponse.ok("User registered successfully"));
    }

    // ── GET /api/auth/me ──────────────────────────────────────────────────
    @GetMapping("/me")
    public ResponseEntity<ApiResponse> getCurrentUser() {
        UserDetailsImpl user = (UserDetailsImpl)
            SecurityContextHolder.getContext().getAuthentication().getPrincipal();

        return ResponseEntity.ok(ApiResponse.ok("Current user", user));
    }
}
