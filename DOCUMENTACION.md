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
- **OpenAI SDK** para análisis de tickets con IA.
- ⚠️ `requirements.txt` está **vacío** — las dependencias reales no quedaron congeladas en el repo.

### 1.2 Punto de entrada — [main.py](Backend/soporte-ai/backend/app/main.py)
- Crea la app FastAPI, habilita **CORS abierto** (`allow_origins=["*"]`) para permitir llamadas del frontend React.
- Registra el router de tickets (`app/api/tickets.py`).
- `GET /` → healthcheck simple (`{"status": "running"}`).

### 1.3 API — [app/api/tickets.py](Backend/soporte-ai/backend/app/api/tickets.py)

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/tickets` | Crea un ticket a partir de un mensaje en texto libre |
| `GET` | `/tickets` | Lista todos los tickets ordenados por prioridad (desc) |
| `PUT` | `/tickets/{ticket_id}` | Cambia el estado del ticket a `IN_PROGRESS` |

**Flujo de `POST /tickets`:**
1. Recibe `{"message": "..."}`.
2. Llama a `analyze_ticket()` (servicio de IA) para extraer del texto: módulo SAP, transacción, urgencia e impacto.
3. Si la respuesta de la IA no es un JSON parseable, cae a un fallback fijo (`modulo: FI`, `transaccion: ZFI_PRUEBA`, etc.).
4. Calcula la prioridad con `calculate_priority()`.
5. Inserta el ticket en MySQL vía `create_ticket_db()`.
6. Responde con `status`, `ticket_id` y `priority`.

`GET /tickets` y `PUT /tickets/{id}` usan conexión directa con `mysql.connector` (no el ORM) y devuelven `{"success": bool, ...}`.

### 1.4 Modelo — [app/models/ticket.py](Backend/soporte-ai/backend/app/models/ticket.py)
Entidad SQLAlchemy `Ticket`: `id, title, description, module, transaction_code, priority, status, created_by`.

### 1.5 Base de datos — [app/db/database.py](Backend/soporte-ai/backend/app/db/database.py) y [database/schema.sql](Backend/soporte-ai/database/schema.sql)
- Conexión MySQL a `soporte_ai` en `localhost:3306`, usuario/clave **hardcodeados** (`root/root`).
- `schema.sql` define 3 tablas: `users`, `tickets` (con `assigned_to`, `created_at`), `ticket_history` (auditoría de acciones). El modelo ORM actual **no usa** `ticket_history` ni `users` todavía.

### 1.6 Servicios
- [ai_service.py](Backend/soporte-ai/backend/app/services/ai_service.py): arma un prompt y llama a `openai.ChatCompletion.create` (modelo `gpt-4o-mini`) pidiendo un JSON con `modulo`, `transaccion`, `urgencia`, `impacto`.
- [prioritization.py](Backend/soporte-ai/backend/app/services/prioritization.py): `priority = urgencia*2 + impacto` (fórmula simple, sin ponderaciones adicionales).
- [ticket_service.py](Backend/soporte-ai/backend/app/services/ticket_service.py): `create_ticket_db()` abre sesión ORM, inserta el ticket con `status="OPEN"` y hace commit/rollback.

---

## 2. Frontend (`Backend/soporte-ai/frontend/dashboard`)

### 2.1 Stack
Create React App (`react-scripts 5`) + **React 19** + **MUI v9** (`@mui/material`) + **axios**.

### 2.2 Estructura
```
src/
├── App.js               → raíz de la app
├── pages/Dashboard.js    → página del dashboard
├── components/
│   ├── Navbar.js         → (archivo vacío, sin implementar)
│   ├── TicketCard.js     → tarjeta simple de ticket (HTML plano)
│   ├── TicketList.js     → lista de TicketCard, hace su propio fetch
│   └── TicketTable.js    → tabla MUI con acciones (usada en producción)
└── services/api.js       → cliente axios (solo GET /tickets)
```

### 2.3 Componentes clave
- **[TicketTable.js](Backend/soporte-ai/frontend/dashboard/src/components/TicketTable.js)** es el componente "real" que se renderiza (usado por `App.js` y `Dashboard.js`). Hace `axios.get`/`axios.put` directo contra `http://127.0.0.1:8000` (URL hardcodeada, no usa `services/api.js`).
  - Muestra tickets en tabla MUI con `Chip` de color según prioridad (🔴 ≥8, 🟡 ≥5, 🟢 <5) y estado (`OPEN/IN_PROGRESS/DONE`).
  - Botón **"Tomar"** en tickets `OPEN` → `PUT /tickets/{id}` para pasarlo a `IN_PROGRESS`, luego refresca la lista.
  - Nota: filtra `tickets.filter(t => t.status === "OPEN")` en una variable `filtered` que **no se usa** para renderizar (la tabla pinta `tickets` completo, no `filtered`).
- **TicketList.js / TicketCard.js**: implementación alternativa/antigua (tarjetas en vez de tabla), usa `services/api.js`. No está montada en `App.js` actualmente (se importa pero no se renderiza).
- **Navbar.js**: archivo vacío, componente sin construir.
- **services/api.js**: solo expone `getTickets()`; no tiene funciones para crear ticket ni cambiar estado (eso lo hace `TicketTable.js` directamente con axios).

### 2.4 Flujo end-to-end
1. Usuario/proceso externo envía `POST /tickets` con un mensaje.
2. Backend usa IA para clasificar y calcular prioridad, guarda en MySQL.
3. El dashboard React (`TicketTable`) hace polling manual (al montar) de `GET /tickets` y pinta la tabla ordenada por prioridad.
4. Un agente de soporte pulsa "Tomar" → `PUT /tickets/{id}` → estado pasa a `IN_PROGRESS`.

---

## 3. Puntos a revisar (no bloqueantes para documentar, pero relevantes)

- 🔴 **Clave de API de OpenAI hardcodeada en texto plano** en `ai_service.py:4`. Debe rotarse y moverse a variable de entorno; si este repo se llegó a subir a un control de versiones remoto, la clave debe considerarse comprometida.
- Credenciales de MySQL (`root/root`) hardcodeadas en `database.py`.
- CORS abierto a `*` en `main.py`.
- `requirements.txt` vacío — no hay forma reproducible de instalar dependencias del backend.
- Endpoint `POST /tickets` no valida que `data["message"]` exista (KeyError si falta).
- `TicketList`/`TicketCard`/`Navbar` parecen código muerto o en progreso (no montado en `App.js`, o vacío).
- Duplicación de lógica de fetch de tickets entre `TicketTable.js` (axios directo) y `services/api.js` (no usado por la tabla real).

---

*Generado a partir de una revisión directa del código fuente el 2026-08-03.*
