package com.erp.security;

import com.erp.model.User;
import com.fasterxml.jackson.annotation.JsonIgnore;
import lombok.Getter;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;

import java.util.Collection;
import java.util.List;
import java.util.Objects;

@Getter
public class UserDetailsImpl implements UserDetails {

    private final Long   id;
    private final String name;
    private final String email;
    private final String role;

    @JsonIgnore
    private final String password;

    private final Collection<? extends GrantedAuthority> authorities;

    public UserDetailsImpl(Long id, String name, String email,
                           String password, String role,
                           Collection<? extends GrantedAuthority> authorities) {
        this.id          = id;
        this.name        = name;
        this.email       = email;
        this.password    = password;
        this.role        = role;
        this.authorities = authorities;
    }

    // ── Factory method from User entity ───────────────────────────────────
    public static UserDetailsImpl build(User user) {
        List<GrantedAuthority> authorities = List.of(
            new SimpleGrantedAuthority("ROLE_" + user.getRole().name())
        );
        return new UserDetailsImpl(
            user.getId(),
            user.getName(),
            user.getEmail(),
            user.getPassword(),
            user.getRole().name(),
            authorities
        );
    }

    // ── UserDetails contract ──────────────────────────────────────────────
    @Override public String getUsername()  { return email; }
    @Override public boolean isAccountNonExpired()    { return true; }
    @Override public boolean isAccountNonLocked()     { return true; }
    @Override public boolean isCredentialsNonExpired(){ return true; }
    @Override public boolean isEnabled()              { return true; }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof UserDetailsImpl that)) return false;
        return Objects.equals(id, that.id);
    }

    @Override public int hashCode() { return Objects.hash(id); }
}
