CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    role VARCHAR(50)
);

CREATE TABLE tickets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title TEXT,
    description TEXT,
    module VARCHAR(50),
    transaction_code VARCHAR(20),
    priority INT,
    status VARCHAR(50) DEFAULT 'OPEN',
    created_by INT,
    assigned_to INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE ticket_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticket_id INT,
    action TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);