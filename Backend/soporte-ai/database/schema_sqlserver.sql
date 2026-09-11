-- ============================================================================
--  Schema de base de datos: soporte_sap_ia
--  Motor: Microsoft SQL Server 2016+ (usa sintaxis moderna: IF NOT EXISTS,
--         DEFAULT con GETDATE(), etc.)
--
--  Cómo usarlo:
--    1) Abrir SQL Server Management Studio (SSMS)
--    2) Conectarse a tu instancia (ej: 02-5CD4284C3V) con un login que tenga
--       permisos de CREATE DATABASE (sa, administrador, etc.)
--    3) Abrir este script y ejecutarlo completo (F5)
--    4) Listo: crea la BD, todas las tablas, llaves foráneas, índices y los
--       registros semilla de las tablas de catálogo (status y priorities).
--
--  Nota sobre los IDs de los catálogos:
--    El código Python (app/db/database.py) usa estos MAPPINGS por defecto:
--      DEFAULT_STATUS_ID_MAP   = { "OPEN":1, "IN_PROGRESS":2, "DONE":3 }
--      DEFAULT_PRIORITY_ID_MAP = { "LOW":1,  "MEDIUM":2,     "HIGH":3 }
--    Si tu negocio usa otros IDs, edita los INSERT de este script y luego
--    edita también los diccionarios en database.py para que coincidan.
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
--    FK: tickets.status_id  → status.status_id
-- ---------------------------------------------------------------------------
IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES
               WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = 'status')
BEGIN
    CREATE TABLE dbo.status (
        status_id    INT IDENTITY(1,1) PRIMARY KEY,
        description  NVARCHAR(100) NOT NULL
    );
END
GO

-- ---------------------------------------------------------------------------
-- 3) TABLA CATÁLOGO: dbo.priorities
--    FK: tickets.priority_id  → priorities.priority_id
-- ---------------------------------------------------------------------------
IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES
               WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = 'priorities')
BEGIN
    CREATE TABLE dbo.priorities (
        priority_id  INT IDENTITY(1,1) PRIMARY KEY,
        description  NVARCHAR(100) NOT NULL
    );
END
GO

-- ---------------------------------------------------------------------------
-- 4) TABLA: dbo.users
--    FK: tickets.assigned_to → users.id  (ON DELETE SET NULL)
-- ---------------------------------------------------------------------------
IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES
               WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = 'users')
BEGIN
    CREATE TABLE dbo.users (
        id            INT IDENTITY(1,1) PRIMARY KEY,
        name          NVARCHAR(100) NOT NULL,
        email         NVARCHAR(100) NOT NULL,
        role          NVARCHAR(50)  NOT NULL DEFAULT N'user',
        password_hash NVARCHAR(255) NULL,
        created_at    DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
        updated_at    DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),

        CONSTRAINT uq_users_email UNIQUE (email),
        CONSTRAINT chk_users_role  CHECK (role IN (N'admin', N'user'))
    );
END
GO

-- ---------------------------------------------------------------------------
-- 5) TABLA MAESTRA: dbo.tickets
-- ---------------------------------------------------------------------------
IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES
               WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = 'tickets')
BEGIN
    CREATE TABLE dbo.tickets (
        id               INT IDENTITY(1,1) PRIMARY KEY,
        title            NVARCHAR(MAX) NULL,
        description      NVARCHAR(MAX) NULL,
        module           NVARCHAR(50)  NULL,
        transaction_code NVARCHAR(20)  NULL,
        status_id        INT NOT NULL,
        priority_id      INT NOT NULL,
        created_by       NVARCHAR(100) NULL,   -- texto libre (nombre del usuario)
        assigned_to      INT NULL,             -- FK → users.id (puede ser NULL)
        created_at       DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
        updated_at       DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),

        CONSTRAINT fk_tickets_status       FOREIGN KEY (status_id)
            REFERENCES dbo.status(status_id),
        CONSTRAINT fk_tickets_priority     FOREIGN KEY (priority_id)
            REFERENCES dbo.priorities(priority_id),
        CONSTRAINT fk_tickets_assigned_to  FOREIGN KEY (assigned_to)
            REFERENCES dbo.users(id)
            ON DELETE SET NULL
            ON UPDATE CASCADE,
    );

    CREATE NONCLUSTERED INDEX idx_tickets_status       ON dbo.tickets (status_id);
    CREATE NONCLUSTERED INDEX idx_tickets_priority     ON dbo.tickets (priority_id);
    CREATE NONCLUSTERED INDEX idx_tickets_assigned_to  ON dbo.tickets (assigned_to);
END
GO

-- ---------------------------------------------------------------------------
-- 6) TABLA DE ARCHIVO / HISTORIAL: dbo.ticket_history
--    Cuando un ticket pasa a DONE se archiva aquí y se borra de "tickets".
--    No lleva FK a tickets.id porque el registro origen ya no existe.
-- ---------------------------------------------------------------------------
IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES
               WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = 'ticket_history')
BEGIN
    CREATE TABLE dbo.ticket_history (
        id         INT IDENTITY(1,1) PRIMARY KEY,
        ticket_id  INT NOT NULL,
        action     NVARCHAR(MAX) NOT NULL,   -- JSON: { event, ticket: {...} }
        created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
    );

    CREATE NONCLUSTERED INDEX idx_history_ticket_id  ON dbo.ticket_history (ticket_id);
    CREATE NONCLUSTERED INDEX idx_history_created_at ON dbo.ticket_history (created_at DESC);
END
GO

-- ============================================================================
-- 7) REGISTROS SEMILLA (SEED DATA) — tablas de catálogo
--    (solo se insertan si la tabla está vacía, para no romper datos existentes)
-- ============================================================================

-- 7.1) dbo.status -----------------------------------------------------------
IF NOT EXISTS (SELECT 1 FROM dbo.status)
BEGIN
    SET IDENTITY_INSERT dbo.status ON;

    INSERT INTO dbo.status (status_id, description) VALUES (1, N'OPEN');
    INSERT INTO dbo.status (status_id, description) VALUES (2, N'IN_PROGRESS');
    INSERT INTO dbo.status (status_id, description) VALUES (3, N'DONE');

    SET IDENTITY_INSERT dbo.status OFF;
END
GO

-- 7.2) dbo.priorities -------------------------------------------------------
IF NOT EXISTS (SELECT 1 FROM dbo.priorities)
BEGIN
    SET IDENTITY_INSERT dbo.priorities ON;

    INSERT INTO dbo.priorities (priority_id, description) VALUES (1, N'LOW - Prioridad Baja');
    INSERT INTO dbo.priorities (priority_id, description) VALUES (2, N'MEDIUM - Prioridad Media');
    INSERT INTO dbo.priorities (priority_id, description) VALUES (3, N'HIGH - Prioridad Alta');

    SET IDENTITY_INSERT dbo.priorities OFF;
END
GO

-- 7.3) Usuario admin inicial (opcional — contraseña: Admin123!) -------------
--      Contraseña hasheada con passlib bcrypt (rounds=12).
--      Si prefieres crearlo desde la API puedes borrar este bloque.
IF NOT EXISTS (SELECT 1 FROM dbo.users WHERE email = N'admin@comfama.com')
BEGIN
    INSERT INTO dbo.users (name, email, role, password_hash)
    VALUES (
        N'Administrador',
        N'admin@comfama.com',
        N'admin',
        N'$2b$12$H3hQe0jN6c0U5VnQyL3q5uJ8yW7e6R5t4S3d2F1g0h9z8x7c6v5b'  -- placeholder
    );
    -- ⚠️ Importante: este hash es una MARCA DE AGUA. Cámbialo por uno real:
    --    desde Python ejecuta:
    --      from passlib.context import CryptContext
    --      pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
    --      print(pwd.hash("Admin123!"))
    --    y reemplaza el valor del INSERT.
END
GO

-- ============================================================================
-- 8) TRIGGER para mantener updated_at actualizado en cada UPDATE
--    Aplica a users y tickets.
-- ============================================================================

IF NOT EXISTS (SELECT 1 FROM sys.triggers WHERE name = N'trg_users_updated_at')
EXEC('CREATE TRIGGER dbo.trg_users_updated_at
ON dbo.users
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE dbo.users
       SET updated_at = SYSUTCDATETIME()
     WHERE id IN (SELECT id FROM inserted);
END');
GO

IF NOT EXISTS (SELECT 1 FROM sys.triggers WHERE name = N'trg_tickets_updated_at')
EXEC('CREATE TRIGGER dbo.trg_tickets_updated_at
ON dbo.tickets
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE dbo.tickets
       SET updated_at = SYSUTCDATETIME()
     WHERE id IN (SELECT id FROM inserted);
END');
GO

-- ============================================================================
-- FIN — Validación rápida (opcional): imprime las tablas creadas
-- ============================================================================
PRINT '✅ Base soporte_sap_ia lista. Tablas existentes:';
SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'dbo' ORDER BY TABLE_NAME;

PRINT '';
PRINT '📋 Contenido de dbo.status:';
SELECT * FROM dbo.status ORDER BY status_id;

PRINT '';
PRINT '📋 Contenido de dbo.priorities:';
SELECT * FROM dbo.priorities ORDER BY priority_id;
GO
