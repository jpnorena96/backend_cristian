-- IuristaTech Database Schema
-- Created: 2026-02-17

CREATE DATABASE IF NOT EXISTS legaltech_db;
USE legaltech_db;

-- 1. Users Table
-- Stores customer and admin information
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL, -- Ensure to store hashed passwords, not plain text in prod
    full_name VARCHAR(100),
    role ENUM('client', 'admin') DEFAULT 'client',
    is_admin BOOLEAN DEFAULT FALSE,
    is_approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 2. Conversations Table
-- Groups messages into chat sessions
CREATE TABLE IF NOT EXISTS conversations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    title VARCHAR(255),
    status ENUM('active', 'archived', 'risk_detected') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- 3. Messages Table
-- Individual messages within a conversation
CREATE TABLE IF NOT EXISTS messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    conversation_id INT NOT NULL,
    sender_role ENUM('user', 'assistant', 'system') NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

-- 4. Initial Seed Data (Optional)
-- Client user (password: '123456') - Hash in real app
INSERT INTO users (email, password_hash, full_name, role) 
VALUES ('admin@legaltech.com', 'admin', 'Admin User', 'admin')
ON DUPLICATE KEY UPDATE email=email;
