-- ============================================================
--  StudentERP — Database Schema
--  Run this manually OR let Hibernate auto-create via ddl-auto=update
-- ============================================================

CREATE DATABASE IF NOT EXISTS student_erp
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE student_erp;

-- ── Users (all roles share this table) ───────────────────────
CREATE TABLE IF NOT EXISTS users (
    id         BIGINT       NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    email      VARCHAR(150) NOT NULL UNIQUE,
    password   VARCHAR(255) NOT NULL,
    role       ENUM('ADMIN','FACULTY','STUDENT') NOT NULL,
    active     TINYINT(1)   NOT NULL DEFAULT 1,
    created_at DATETIME,
    updated_at DATETIME
);

-- ── Students ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS students (
    id              BIGINT       NOT NULL AUTO_INCREMENT PRIMARY KEY,
    roll_no         VARCHAR(20)  NOT NULL UNIQUE,
    branch          VARCHAR(50)  NOT NULL,
    semester        INT          NOT NULL,
    phone           VARCHAR(15),
    address         TEXT,
    date_of_birth   DATE,
    guardian_name   VARCHAR(100),
    guardian_phone  VARCHAR(15),
    status          ENUM('ACTIVE','PENDING','GRADUATED','DROPPED') NOT NULL DEFAULT 'ACTIVE',
    user_id         BIGINT       NOT NULL UNIQUE,
    admission_date  DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ── Faculty ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS faculty (
    id            BIGINT       NOT NULL AUTO_INCREMENT PRIMARY KEY,
    department    VARCHAR(80)  NOT NULL,
    designation   VARCHAR(80)  NOT NULL,
    qualification VARCHAR(100),
    phone         VARCHAR(15),
    user_id       BIGINT       NOT NULL UNIQUE,
    joined_at     DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ── Subjects ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS subjects (
    id         BIGINT      NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    code       VARCHAR(20)  NOT NULL UNIQUE,
    semester   INT          NOT NULL,
    branch     VARCHAR(50)  NOT NULL,
    credits    INT,
    faculty_id BIGINT,
    FOREIGN KEY (faculty_id) REFERENCES faculty(id) ON DELETE SET NULL
);

-- ── Attendance ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS attendance (
    id          BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    student_id  BIGINT NOT NULL,
    subject_id  BIGINT NOT NULL,
    date        DATE   NOT NULL,
    status      ENUM('PRESENT','ABSENT','LATE') NOT NULL,
    marked_by   BIGINT,
    UNIQUE KEY uq_attendance (student_id, subject_id, date),
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    FOREIGN KEY (marked_by)  REFERENCES faculty(id)  ON DELETE SET NULL
);

-- ── Marks ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS marks (
    id              BIGINT  NOT NULL AUTO_INCREMENT PRIMARY KEY,
    student_id      BIGINT  NOT NULL,
    subject_id      BIGINT  NOT NULL,
    exam_type       ENUM('MID_SEM','END_SEM','INTERNAL','PRACTICAL') NOT NULL,
    marks_obtained  DOUBLE  NOT NULL,
    total_marks     DOUBLE  NOT NULL,
    UNIQUE KEY uq_marks (student_id, subject_id, exam_type),
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
);

-- ── Fees ──────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS fees (
    id              BIGINT         NOT NULL AUTO_INCREMENT PRIMARY KEY,
    student_id      BIGINT         NOT NULL,
    amount          DECIMAL(10,2)  NOT NULL,
    due_date        DATE           NOT NULL,
    paid_date       DATE,
    receipt_number  VARCHAR(50),
    fee_type        VARCHAR(50),
    status          ENUM('PENDING','PAID','OVERDUE','WAIVED') NOT NULL DEFAULT 'PENDING',
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- ── Notices ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS notices (
    id        BIGINT   NOT NULL AUTO_INCREMENT PRIMARY KEY,
    title     VARCHAR(200) NOT NULL,
    content   TEXT,
    category  ENUM('GENERAL','EXAM','FEE','EVENT','HOLIDAY','URGENT') NOT NULL DEFAULT 'GENERAL',
    posted_by BIGINT,
    posted_at DATETIME,
    active    TINYINT(1) NOT NULL DEFAULT 1,
    FOREIGN KEY (posted_by) REFERENCES users(id) ON DELETE SET NULL
);

-- ── Sample data (optional) ────────────────────────────────────
-- Password for all sample users: "Password@1"
-- (BCrypt hash below is for "Password@1")

INSERT IGNORE INTO users (name, email, password, role) VALUES
  ('System Administrator', 'admin@college.edu',
   '$2a$12$hVzJG0T7lS1Z8bsGdGjOJOdjEqKuqW4H5tJLaKGymFTiqA1PRRAmG', 'ADMIN'),
  ('Dr. Ramesh Patel', 'r.patel@college.edu',
   '$2a$12$hVzJG0T7lS1Z8bsGdGjOJOdjEqKuqW4H5tJLaKGymFTiqA1PRRAmG', 'FACULTY'),
  ('Anika Sharma', 'anika@college.edu',
   '$2a$12$hVzJG0T7lS1Z8bsGdGjOJOdjEqKuqW4H5tJLaKGymFTiqA1PRRAmG', 'STUDENT');
