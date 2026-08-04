# Soporte-AI — Documentación del proyecto

Sistema de gestión de tickets de soporte SAP con priorización asistida por IA (OpenAI).
Arquitectura: **Backend** en FastAPI + MySQL, **Frontend** en React (Create React App + MUI).

```
Backend/soporte-ai/
├── backend/            → API FastAPI (Python)
├── database/           → schema.sql (MySQL)
└── frontend/dashboard/ → SPA React
```

---

## 1. Backend (`Backend/soporte-ai/backend`)

### 1.1 Stack
- **FastAPI** como framework web.
- **SQLAlchemy** (ORM) + **mysql-connector-python** (queries directas) contra **MySQL**.
- **OpenAI SDK** (v0.28) para análisis de tickets con IA.
- **python-dotenv** para cargar configuración desde `.env`.

### 1.2 Configuración — variables de entorno
Toda credencial y configuración sensible vive en `backend/.env` (no se versiona; ver `.gitignore`).
Usa `backend/.env.example` como plantilla:

| Variable | Descripción | Default |
|---|---|---|
| `OPENAI_API_KEY` | Clave de la API de OpenAI | *(requerida, sin default)* |
| `DB_HOST` / `DB_PORT` / `DB_USER` / `DB_PASSWORD` / `DB_NAME` | Conexión MySQL | `localhost` / `3306` / `root` / `root` / `soporte_ai` |
| `SQL_ECHO` | Loguear las queries SQL en consola (debug) | `false` |
| `CORS_ORIGINS` | Orígenes permitidos, separados por coma | `http://localhost:3000` |

**Instalación y arranque:**
```bash
cd Backend/soporte-ai/backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
copy .env.example .env       # y completar los valores reales
uvicorn app.main:app --reload
```

### 1.3 Punto de entrada — [main.py](Backend/soporte-ai/backend/app/main.py)
- Crea la app FastAPI y habilita CORS según `CORS_ORIGINS` (por defecto solo `localhost:3000`, ya no `*`).
- Registra el router de tickets (`app/api/tickets.py`).
- `GET /` → healthcheck (`{"status": "running"}`).

### 1.4 API — [app/api/tickets.py](Backend/soporte-ai/backend/app/api/tickets.py)

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/tickets` | Crea un ticket a partir de un mensaje en texto libre |
| `GET` | `/tickets` | Lista todos los tickets ordenados por prioridad (desc) |
| `PUT` | `/tickets/{ticket_id}` | Cambia el estado del ticket a `IN_PROGRESS` |

**Flujo de `POST /tickets`:**
1. Recibe `{"message": "...", "created_by": "..."}`. Si falta `message`, responde `400`.
2. Llama a `analyze_ticket()` (servicio de IA) para extraer módulo SAP, transacción, urgencia e impacto.
3. Si la IA falla o responde algo no parseable, cae a un fallback fijo (`FALLBACK_ANALYSIS` en el mismo archivo).
4. Calcula la prioridad con `calculate_priority()`.
5. Inserta el ticket en MySQL vía `create_ticket_db()`.
6. Responde con `status`, `ticket_id` y `priority`.

`GET /tickets` y `PUT /tickets/{id}` usan conexión directa con `mysql.connector`. `PUT` responde `404` si el ticket no existe.

### 1.5 Modelo — [app/models/ticket.py](Backend/soporte-ai/backend/app/models/ticket.py)
Entidad SQLAlchemy `Ticket`: `id, title, description, module, transaction_code, priority, status, created_by`.

### 1.6 Base de datos — [app/db/database.py](Backend/soporte-ai/backend/app/db/database.py) y [database/schema.sql](Backend/soporte-ai/database/schema.sql)
- Conexión MySQL a `soporte_ai`, credenciales tomadas de `.env`.
- `schema.sql` define 3 tablas: `users`, `tickets` (con `assigned_to`, `created_at`), `ticket_history` (auditoría de acciones). El modelo ORM actual **no usa** `ticket_history` ni `users` todavía — pendiente si se necesita historial o autenticación real.

### 1.7 Servicios
- [ai_service.py](Backend/soporte-ai/backend/app/services/ai_service.py): arma un prompt y llama a `openai.ChatCompletion.create` (modelo `gpt-4o-mini`) pidiendo un JSON con `modulo`, `transaccion`, `urgencia`, `impacto`. La clave se lee de `OPENAI_API_KEY`.
- [prioritization.py](Backend/soporte-ai/backend/app/services/prioritization.py): `priority = urgencia*2 + impacto`.
- [ticket_service.py](Backend/soporte-ai/backend/app/services/ticket_service.py): `create_ticket_db()` abre sesión ORM, inserta el ticket con `status="OPEN"` y hace commit/rollback.

---

## 2. Frontend (`Backend/soporte-ai/frontend/dashboard`)

### 2.1 Stack
Create React App (`react-scripts 5`) + **React 19** + **MUI v9** (`@mui/material`) + **axios**.

### 2.2 Configuración — variables de entorno
`REACT_APP_API_URL` define la URL base del backend (`frontend/dashboard/.env`, plantilla en `.env.example`). Por defecto `http://127.0.0.1:8000`.

**Instalación y arranque:**
```bash
cd Backend/soporte-ai/frontend/dashboard
npm install
copy .env.example .env   # ajustar si el backend corre en otra URL
npm start
```

### 2.3 Estructura
```
src/
├── App.js               → shell de la app; controla si se muestra Login o Dashboard
├── pages/
│   ├── Login.js          → formulario de acceso (solo UI, ver nota abajo)
│   └── Dashboard.js       → página del dashboard, compone <TicketTable /> + logout
├── components/
│   └── TicketTable.js    → tabla MUI con listado, prioridad, estado y acción "Tomar"
└── services/api.js       → cliente axios centralizado (getTickets, createTicket, updateTicketStatus)
```

### 2.3.1 Login (`pages/Login.js`)
Pantalla de acceso previa al dashboard. **Es solo UI por ahora**: valida que usuario y contraseña
no estén vacíos, pero no verifica credenciales contra ningún backend (cualquier valor no vacío
entra). `App.js` guarda el usuario logueado en estado de React (`useState`), sin persistencia:
al recargar la página vuelve a pedir login. Hay un botón "Cerrar sesión" en el Dashboard para
volver al login sin recargar.

Cuando se quiera una autenticación real, falta: columna de contraseña (hasheada) en la tabla
`users`, un endpoint `POST /login` en el backend, y proteger `/tickets` con el token resultante.
> Se eliminaron `TicketCard.js`, `TicketList.js` y `Navbar.js`: eran una implementación alternativa (tarjetas) y un componente vacío que no estaban montados en la app. Siguen disponibles en el historial de git (commit baseline) si se necesitan recuperar.

### 2.4 Componentes clave
- **`services/api.js`**: único punto de acceso a la API. Todas las llamadas HTTP pasan por aquí (antes `TicketTable.js` llamaba a `axios` directo con la URL hardcodeada).
- **`TicketTable.js`**: tabla MUI con `Chip` de color según prioridad (🔴 ≥8, 🟡 ≥5, 🟢 <5) y estado (`OPEN/IN_PROGRESS/DONE`). Botón **"Tomar"** en tickets `OPEN` → actualiza a `IN_PROGRESS` y refresca la lista.

### 2.5 Flujo end-to-end
1. Un proceso externo (o formulario futuro) envía `POST /tickets` con un mensaje.
2. El backend usa IA para clasificar y calcular prioridad, y guarda el ticket en MySQL.
3. El dashboard React (`TicketTable`) hace fetch de `GET /tickets` al montar y pinta la tabla ordenada por prioridad.
4. Un agente de soporte pulsa "Tomar" → `PUT /tickets/{id}` → estado pasa a `IN_PROGRESS`.

---

## 3. Seguridad y control de versiones

- El proyecto ahora tiene **git inicializado** (antes no lo tenía) con un commit baseline previo al refactor.
- `.gitignore` en la raíz excluye `venv/`, `node_modules/`, `build/` y **`.env`** (nunca se versionan credenciales).
- ⚠️ La clave de OpenAI que estaba hardcodeada en el código fue movida a `backend/.env` (fuera de git), pero como estuvo en texto plano en el código fuente, **se recomienda rotarla desde el panel de OpenAI** y reemplazarla por una nueva en `.env`.

---

*Generado a partir de una revisión directa del código fuente. Última actualización: 2026-08-03.*
