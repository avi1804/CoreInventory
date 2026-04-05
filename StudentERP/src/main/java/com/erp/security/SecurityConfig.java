package com.erp.security;

import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.authentication.*;
import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.*;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.web.cors.*;

import java.util.List;

@Configuration
@EnableWebSecurity
@EnableMethodSecurity          // enables @PreAuthorize on controllers
@RequiredArgsConstructor
public class SecurityConfig {

    private final JwtAuthenticationFilter jwtAuthFilter;
    private final UserDetailsServiceImpl  userDetailsService;

    // ── Password encoder ──────────────────────────────────────────────────
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder(12);
    }

    // ── Authentication manager ────────────────────────────────────────────
    @Bean
    public AuthenticationManager authenticationManager(
            AuthenticationConfiguration config) throws Exception {
        return config.getAuthenticationManager();
    }

    // ── Security filter chain ─────────────────────────────────────────────
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            // Disable CSRF — using JWT, not cookies
            .csrf(csrf -> csrf.disable())

            // CORS
            .cors(cors -> cors.configurationSource(corsConfigurationSource()))

            // Session policy — STATELESS for JWT
            .sessionManagement(session ->
                session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))

            // Route-level authorization
            .authorizeHttpRequests(auth -> auth

                // ── Public endpoints (no auth required)
                .requestMatchers("/api/auth/**").permitAll()
                .requestMatchers("/api/public/**").permitAll()

                // ── Admin only
                .requestMatchers("/api/admin/**").hasRole("ADMIN")

                // ── Faculty + Admin
                .requestMatchers("/api/attendance/mark").hasAnyRole("FACULTY", "ADMIN")
                .requestMatchers("/api/marks/enter").hasAnyRole("FACULTY", "ADMIN")
                .requestMatchers("/api/notices/create").hasAnyRole("FACULTY", "ADMIN")

                // ── Any authenticated user (Student, Faculty, Admin)
                .requestMatchers("/api/students/**").authenticated()
                .requestMatchers("/api/faculty/**").authenticated()
                .requestMatchers("/api/attendance/**").authenticated()
                .requestMatchers("/api/marks/**").authenticated()
                .requestMatchers("/api/fees/**").authenticated()
                .requestMatchers("/api/library/**").authenticated()
                .requestMatchers("/api/timetable/**").authenticated()
                .requestMatchers("/api/subjects/**").authenticated()
                .requestMatchers("/api/notices/**").authenticated()

                // Deny everything else
                .anyRequest().authenticated()
            )

            // Plug JWT filter before username/password filter
            .addFilterBefore(jwtAuthFilter, UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }

    // ── CORS configuration ────────────────────────────────────────────────
    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration config = new CorsConfiguration();
        config.setAllowedOriginPatterns(List.of("*"));
        config.setAllowedMethods(List.of("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"));
        config.setAllowedHeaders(List.of("*"));
        config.setAllowCredentials(false);
        config.setMaxAge(3600L);

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", config);
        return source;
    }
}