package com.erp.exception;

import com.erp.dto.AuthDTOs.ApiResponse;
import org.springframework.http.*;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestControllerAdvice
public class GlobalExceptionHandler {

    // ── 404 – Resource not found ──────────────────────────────────────────
    @ExceptionHandler(ResourceNotFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    public ApiResponse handleNotFound(ResourceNotFoundException ex) {
        return ApiResponse.error(ex.getMessage());
    }

    // ── 400 – Validation errors ───────────────────────────────────────────
    @ExceptionHandler(MethodArgumentNotValidException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ApiResponse handleValidation(MethodArgumentNotValidException ex) {
        Map<String, String> errors = new HashMap<>();
        ex.getBindingResult().getAllErrors().forEach(err -> {
            String field   = ((FieldError) err).getField();
            String message = err.getDefaultMessage();
            errors.put(field, message);
        });
        return ApiResponse.builder()
            .success(false)
            .message("Validation failed")
            .data(errors)
            .build();
    }

    // ── 401 – Bad credentials ─────────────────────────────────────────────
    @ExceptionHandler(BadCredentialsException.class)
    @ResponseStatus(HttpStatus.UNAUTHORIZED)
    public ApiResponse handleBadCredentials(BadCredentialsException ex) {
        return ApiResponse.error("Invalid email or password");
    }

    // ── 403 – Access denied ───────────────────────────────────────────────
    @ExceptionHandler(AccessDeniedException.class)
    @ResponseStatus(HttpStatus.FORBIDDEN)
    public ApiResponse handleAccessDenied(AccessDeniedException ex) {
        return ApiResponse.error("Access denied: insufficient permissions");
    }

    // ── 400 – Illegal state (e.g. receipt for unpaid fee) ────────────────
    @ExceptionHandler(IllegalStateException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ApiResponse handleIllegalState(IllegalStateException ex) {
        return ApiResponse.error(ex.getMessage());
    }

    // ── 500 – Catch-all ───────────────────────────────────────────────────
    @ExceptionHandler(Exception.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public ApiResponse handleGeneric(Exception ex) {
        return ApiResponse.error("An unexpected error occurred: " + ex.getMessage());
    }
}
