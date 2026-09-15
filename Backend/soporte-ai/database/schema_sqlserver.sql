-- ============================================================================
--  Schema de base de datos: soporte_sap_ia
--  Motor: Microsoft SQL Server 2016+
--
--  Cómo usarlo:
--    1) Abrir SQL Server Management Studio (SSMS)
--    2) Conectarse a la instancia
--    3) Ejecutar este script completo (F5)
-- ============================================================================

SET NOCOUNT ON;
GO

-- ---------------------------------------------------------------------------
-- 1) CREAR LA BASE DE DATOS (si no existe)
-- ---------------------------------------------------------------------------
IF NOT EXISTS (SELECT 1 FROM sys.databases WHERE name = N'soporte_sap_ia')
BEGIN
    CREATE DATABASE soporte_sap_ia;
END
GO

USE soporte_sap_ia;
GO

-- ---------------------------------------------------------------------------
-- 2) TABLA CATÁLOGO: dbo.status
-- ---------------------------------------------------------------------------
IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = 'status')
BEGIN
    CREATE TABLE dbo.status (
        status_id    INT IDENTITY(1,1) PRIMARY KEY,
        description  NVARCHAR(100) NOT NULL
    );
END
GO

-- ---------------------------------------------------------------------------
-- 3) TABLA CATÁLOGO: dbo.priorities
-- ---------------------------------------------------------------------------
IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = 'priorities')
BEGIN
    CREATE TABLE dbo.priorities (
        priority_id  INT IDENTITY(1,1) PRIMARY KEY,
        description  NVARCHAR(100) NOT NULL
    );
END
GO

-- ---------------------------------------------------------------------------
-- 4) TABLA CATÁLOGO: dbo.roles
-- ---------------------------------------------------------------------------
IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = 'roles')
BEGIN
    CREATE TABLE dbo.roles (
        role_id    INT IDENTITY(1,1) PRIMARY KEY,
        role_name  NVARCHAR(50) NOT NULL UNIQUE
    );
END
GO

-- ---------------------------------------------------------------------------
-- 5) TABLA: dbo.users
-- ---------------------------------------------------------------------------
IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = 'users')
BEGIN
    CREATE TABLE dbo.users (
        id            INT IDENTITY(1,1) PRIMARY KEY,
        name          NVARCHAR(100) NOT NULL,
        email         NVARCHAR(100) NOT NULL,
        role_id       INT NOT NULL,
        password_hash NVARCHAR(255) NULL,
        created_at    DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
        updated_at    DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),

        CONSTRAINT uq_users_email UNIQUE (email),
        CONSTRAINT fk_users_role  FOREIGN KEY (role_id) REFERENCES dbo.roles(role_id)
    );
END
GO

-- ---------------------------------------------------------------------------
-- 6) TABLA MAESTRA: dbo.tickets
-- ---------------------------------------------------------------------------
IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = 'tickets')
BEGIN
    CREATE TABLE dbo.tickets (
        id               INT IDENTITY(1,1) PRIMARY KEY,
        title            NVARCHAR(MAX) NULL,
        description      NVARCHAR(MAX) NULL,
        module           NVARCHAR(50)  NULL,
        transaction_code NVARCHAR(20)  NULL,
        status_id        INT NOT NULL,
        priority_id      INT NOT NULL,
        created_by       NVARCHAR(100) NULL,
        assigned_to      INT NULL,
        created_at       DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
        updated_at       DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),

        CONSTRAINT fk_tickets_status      FOREIGN KEY (status_id)   REFERENCES dbo.status(status_id),
        CONSTRAINT fk_tickets_priority    FOREIGN KEY (priority_id) REFERENCES dbo.priorities(priority_id),
        CONSTRAINT fk_tickets_assigned_to FOREIGN KEY (assigned_to) REFERENCES dbo.users(id) ON DELETE SET NULL ON UPDATE CASCADE
    );

    CREATE NONCLUSTERED INDEX idx_tickets_status      ON dbo.tickets (status_id);
    CREATE NONCLUSTERED INDEX idx_tickets_priority    ON dbo.tickets (priority_id);
    CREATE NONCLUSTERED INDEX idx_tickets_assigned_to ON dbo.tickets (assigned_to);
END
GO

-- ---------------------------------------------------------------------------
-- 7) TABLA DE HISTORIAL: dbo.ticket_history
-- ---------------------------------------------------------------------------
IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = 'ticket_history')
BEGIN
    CREATE TABLE dbo.ticket_history (
        id         INT IDENTITY(1,1) PRIMARY KEY,
        ticket_id  INT NOT NULL,
        action     NVARCHAR(MAX) NOT NULL,
        created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
    );

    CREATE NONCLUSTERED INDEX idx_history_ticket_id  ON dbo.ticket_history (ticket_id);
    CREATE NONCLUSTERED INDEX idx_history_created_at ON dbo.ticket_history (created_at DESC);
END
GO

-- ============================================================================
-- 8) REGISTROS SEMILLA (SEED DATA)
-- ============================================================================

-- 8.1) dbo.status
IF NOT EXISTS (SELECT 1 FROM dbo.status)
BEGIN
    SET IDENTITY_INSERT dbo.status ON;
    INSERT INTO dbo.status (status_id, description) VALUES (1, N'OPEN'), (2, N'IN_PROGRESS'), (3, N'DONE');
    SET IDENTITY_INSERT dbo.status OFF;
END
GO

-- 8.2) dbo.priorities
IF NOT EXISTS (SELECT 1 FROM dbo.priorities)
BEGIN
    SET IDENTITY_INSERT dbo.priorities ON;
    INSERT INTO dbo.priorities (priority_id, description) VALUES (1, N'BAJA'), (2, N'MEDIA'), (3, N'ALTA');
    SET IDENTITY_INSERT dbo.priorities OFF;
END
GO

-- 8.3) dbo.roles
IF NOT EXISTS (SELECT 1 FROM dbo.roles)
BEGIN
    SET IDENTITY_INSERT dbo.roles ON;
    INSERT INTO dbo.roles (role_id, role_name) VALUES (1, N'admin'), (3, N'user');
    SET IDENTITY_INSERT dbo.roles OFF;
END
GO

-- 8.4) Usuario admin inicial
IF NOT EXISTS (SELECT 1 FROM dbo.users WHERE email = N'admin@comfama.com')
BEGIN
    INSERT INTO dbo.users (name, email, role_id, password_hash)
    VALUES (
        N'Administrador',
        N'admin@comfama.com',
        1, -- ID del rol admin
        N'$2b$12$H3hQe0jN6c0U5VnQyL3q5uJ8yW7e6R5t4S3d2F1g0h9z8x7c6v5b'
    );
END
GO

-- ============================================================================
-- 9) TRIGGERS para updated_at
-- ============================================================================
IF NOT EXISTS (SELECT 1 FROM sys.triggers WHERE name = N'trg_users_updated_at')
EXEC('CREATE TRIGGER dbo.trg_users_updated_at ON dbo.users AFTER UPDATE AS BEGIN SET NOCOUNT ON; UPDATE dbo.users SET updated_at = SYSUTCDATETIME() WHERE id IN (SELECT id FROM inserted); END');
GO

IF NOT EXISTS (SELECT 1 FROM sys.triggers WHERE name = N'trg_tickets_updated_at')
EXEC('CREATE TRIGGER dbo.trg_tickets_updated_at ON dbo.tickets AFTER UPDATE AS BEGIN SET NOCOUNT ON; UPDATE dbo.tickets SET updated_at = SYSUTCDATETIME() WHERE id IN (SELECT id FROM inserted); END');
GO

PRINT '✅ Script finalizado. Base de datos, tablas, índices y datos semilla creados correctamente.';
GO