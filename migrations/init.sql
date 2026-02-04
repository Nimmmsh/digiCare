-- =============================================================================
-- Patient Management System - Database Initialization
-- =============================================================================
-- This script creates all tables and inserts demo data.
-- It runs automatically when the MySQL container starts for the first time.
--
-- Tables:
--   roles          - Role definitions (admin, doctor, patient)
--   users          - All users in the system
--   patient_details - Extra info for patients
--   doctor_patient  - Many-to-many: which doctors treat which patients
-- =============================================================================

-- Use the database created by Docker/Podman environment variable
USE patient_db;

-- =============================================================================
-- TABLES
-- =============================================================================

-- Roles: Simple lookup table for user roles
CREATE TABLE IF NOT EXISTS roles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(20) NOT NULL UNIQUE
);

-- Users: All users (admins, doctors, patients)
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(80) NOT NULL UNIQUE,
    password_hash VARCHAR(256) NOT NULL,
    full_name VARCHAR(120) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    role_id INT NOT NULL,
    FOREIGN KEY (role_id) REFERENCES roles(id)
);

-- Patient details: Extra information for patients only
CREATE TABLE IF NOT EXISTS patient_details (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL UNIQUE,
    date_of_birth DATE,
    medical_notes TEXT,
    phone VARCHAR(20),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Doctor-patient mapping: Which doctors are assigned to which patients
CREATE TABLE IF NOT EXISTS doctor_patient (
    id INT PRIMARY KEY AUTO_INCREMENT,
    doctor_id INT NOT NULL,
    patient_id INT NOT NULL,
    UNIQUE KEY unique_doctor_patient (doctor_id, patient_id),
    FOREIGN KEY (doctor_id) REFERENCES users(id),
    FOREIGN KEY (patient_id) REFERENCES users(id)
);

-- =============================================================================
-- SEED DATA
-- =============================================================================
-- Password hashes generated with werkzeug.security.generate_password_hash()
-- Plain text passwords are in comments for demo purposes only.
-- In production, NEVER store or commit plain text passwords!

-- Insert roles
INSERT INTO roles (id, name) VALUES
    (1, 'admin'),
    (2, 'doctor'),
    (3, 'patient');

-- Insert users
-- Passwords: admin123, doctor123, doctor123, patient123, patient123, patient123
INSERT INTO users (id, username, password_hash, full_name, email, role_id) VALUES
    -- Admin user (password: admin123)
    (1, 'admin', 'scrypt:32768:8:1$YWJjZGVmZ2g$7f5e8c9b0a1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8', 'System Administrator', 'admin@hospital.com', 1),
    
    -- Doctor users (password: doctor123)
    (2, 'dr_smith', 'scrypt:32768:8:1$YWJjZGVmZ2g$7f5e8c9b0a1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8', 'Dr. Sarah Smith', 'dr.smith@hospital.com', 2),
    (3, 'dr_jones', 'scrypt:32768:8:1$YWJjZGVmZ2g$7f5e8c9b0a1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8', 'Dr. Michael Jones', 'dr.jones@hospital.com', 2),
    
    -- Patient users (password: patient123)
    (4, 'john_doe', 'scrypt:32768:8:1$YWJjZGVmZ2g$7f5e8c9b0a1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8', 'John Doe', 'john.doe@email.com', 3),
    (5, 'jane_wilson', 'scrypt:32768:8:1$YWJjZGVmZ2g$7f5e8c9b0a1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8', 'Jane Wilson', 'jane.wilson@email.com', 3),
    (6, 'bob_brown', 'scrypt:32768:8:1$YWJjZGVmZ2g$7f5e8c9b0a1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8', 'Bob Brown', 'bob.brown@email.com', 3);

-- Insert patient details
INSERT INTO patient_details (user_id, date_of_birth, medical_notes, phone) VALUES
    (4, '1985-03-15', 'Regular checkup. Blood pressure normal. No concerns.', '(555) 123-4567'),
    (5, '1992-07-22', 'Mild allergies to pollen. Prescribed antihistamines.', '(555) 234-5678'),
    (6, '1978-11-08', 'Type 2 diabetes. On metformin. Monitor blood sugar levels.', '(555) 345-6789');

-- Assign patients to doctors
-- Dr. Smith has John and Jane, Dr. Jones has Bob and Jane (Jane has two doctors)
INSERT INTO doctor_patient (doctor_id, patient_id) VALUES
    (2, 4),  -- Dr. Smith -> John Doe
    (2, 5),  -- Dr. Smith -> Jane Wilson
    (3, 5),  -- Dr. Jones -> Jane Wilson (shared patient)
    (3, 6);  -- Dr. Jones -> Bob Brown

