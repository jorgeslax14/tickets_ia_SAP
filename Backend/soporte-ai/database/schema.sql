-- Esquema de soporte_ai
--
-- Actualizado para: (a) reflejar cómo la aplicación usa la base hoy en día
-- (created_by es texto libre, no un id) y (b) cerrar los huecos de
-- historias-usuario-basedatos.html (US-DB-004 a US-DB-016, salvo las dos que
-- no son cambios de esquema — ver nota al final).
--
-- Pensado para levantar un ambiente NUEVO desde cero. La base de desarrollo
-- ya tiene estas tablas con datos, así que este script fallará con
-- "table already exists" si se corre tal cual encima de ella — para llevar
-- una base ya poblada a esta versión hace falta un script de migración
-- (ALTER TABLE) aparte.

CREATE DATABASE IF NOT EXISTS soporte_ai
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_0900_ai_ci; -- US-DB-016: charset explícito, no heredado del server

USE soporte_ai;

-- ---------------------------------------------------------------------------
-- users
-- ---------------------------------------------------------------------------
CREATE TABLE users (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    email         VARCHAR(100) NOT NULL,
    role          VARCHAR(50) NOT NULL DEFAULT 'user',
    password_hash VARCHAR(255) NULL, -- US-DB-009: columna lista, el login no la usa todavía
    CONSTRAINT uq_users_email UNIQUE (email),
    CONSTRAINT chk_users_role CHECK (role IN ('admin', 'user')) -- US-DB-006
) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

-- ---------------------------------------------------------------------------
-- tickets
-- ---------------------------------------------------------------------------
CREATE TABLE tickets (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    title            TEXT,
    description      TEXT,
    module           VARCHAR(50),
    transaction_code VARCHAR(20),
    priority         INT,
    status           VARCHAR(50) NOT NULL DEFAULT 'OPEN',
    created_by       VARCHAR(50), -- texto libre (nombre), no FK: así lo manda tickets.py hoy
    assigned_to      INT NULL,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, -- US-DB-014
    CONSTRAINT fk_tickets_assigned_to FOREIGN KEY (assigned_to) REFERENCES users(id)
        ON DELETE SET NULL ON UPDATE CASCADE, -- US-DB-004
    CONSTRAINT chk_tickets_status CHECK (status IN ('OPEN', 'IN_PROGRESS', 'DONE')) -- US-DB-005
) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

CREATE INDEX idx_tickets_status ON tickets (status);           -- US-DB-011
CREATE INDEX idx_tickets_assigned_to ON tickets (assigned_to);
CREATE INDEX idx_tickets_priority ON tickets (priority);

-- ---------------------------------------------------------------------------
-- ticket_history
-- ---------------------------------------------------------------------------
CREATE TABLE ticket_history (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    ticket_id  INT NOT NULL, -- sin FK a tickets.id: el ticket referenciado ya se borró al archivarse
    action     JSON,         -- antes TEXT; mismo snapshot, ahora consultable con JSON_EXTRACT (US-DB-013)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

CREATE INDEX idx_history_ticket_id ON ticket_history (ticket_id);   -- US-DB-012
CREATE INDEX idx_history_created_at ON ticket_history (created_at);

-- ---------------------------------------------------------------------------
-- Lo que este script NO resuelve, porque no son cambios de esquema:
--
--   US-DB-010 — usuario de MySQL de mínimo privilegio para la app
--   (hoy la conexión usa root/root). Ejemplo:
--     CREATE USER 'soporte_ai_app'@'%' IDENTIFIED BY 'una-clave-fuerte';
--     GRANT SELECT, INSERT, UPDATE, DELETE ON soporte_ai.* TO 'soporte_ai_app'@'%';
--
--   US-DB-015 — versionar los cambios de esquema con una herramienta de
--   migraciones (p. ej. Alembic) en vez de un único schema.sql editado a mano.
-- ---------------------------------------------------------------------------
