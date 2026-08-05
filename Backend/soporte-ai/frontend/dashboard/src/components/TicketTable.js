import { useEffect, useState } from "react";
import {
  Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Paper, Chip, CircularProgress, Button,
  Select, MenuItem
} from "@mui/material";
import { getTickets, updateTicketStatus } from "../services/api";

// Nombres de prueba para el selector de "Asignado a" (solo UI, no persiste todavía).
const ASSIGNEES = ["Jorge Velásquez", "María Gómez", "Carlos Pérez", "Laura Ramírez", "Andrés Torres"];

function getPriorityColor(priority) {
  if (priority >= 8) return "error";      // 🔴 Alto
  if (priority >= 5) return "warning";    // 🟡 Medio
  return "success";                       // 🟢 Bajo
}

function getStatusColor(status) {
  switch (status) {
    case "OPEN":
      return "warning";
    case "IN_PROGRESS":
      return "info";
    case "DONE":
      return "success";
    default:
      return "default";
  }
}

// Próximo estado y texto del botón de acción según el estado actual del ticket.
const NEXT_STEP = {
  OPEN: { status: "IN_PROGRESS", label: "Tomar" },
  IN_PROGRESS: { status: "DONE", label: "Finalizar" },
};

export default function TicketTable({ statusFilter, compact = false }) {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [assignments, setAssignments] = useState({});

  const assignTicket = (id, name) => {
    setAssignments(prev => ({ ...prev, [id]: name }));
  };

  const fetchTickets = async () => {
    try {
      const res = await getTickets();
      setTickets(res.data.data);
    } catch (err) {
      console.error("Error cargando tickets:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTickets();
  }, []);

  const advanceTicket = async (id, nextStatus) => {
    try {
      await updateTicketStatus(id, nextStatus);
      await fetchTickets();
    } catch (error) {
      console.error("Error actualizando ticket:", error);
    }
  };

  if (loading) return <CircularProgress />;

  const visibleTickets = statusFilter
    ? tickets.filter(ticket => ticket.status === statusFilter)
    : tickets;

  return (
    <TableContainer component={Paper} sx={{ mt: 4 }}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell><b>ID</b></TableCell>
            <TableCell><b>Título</b></TableCell>
            <TableCell><b>Módulo SAP</b></TableCell>
            <TableCell><b>Transacción</b></TableCell>
            <TableCell><b>Prioridad</b></TableCell>
            <TableCell><b>Estado</b></TableCell>
            {!compact && <TableCell><b>Creado por</b></TableCell>}
            {!compact && <TableCell><b>Asignado a</b></TableCell>}
            <TableCell><b>Acciones</b></TableCell>
          </TableRow>
        </TableHead>

        <TableBody>
          {visibleTickets.map(ticket => (
            <TableRow key={ticket.id}>
              <TableCell>{ticket.id}</TableCell>
              <TableCell>{ticket.title}</TableCell>
              <TableCell>{ticket.module}</TableCell>
              <TableCell>{ticket.transaction_code}</TableCell>

              <TableCell>
                <Chip label={ticket.priority} color={getPriorityColor(ticket.priority)} />
              </TableCell>

              <TableCell>
                <Chip label={ticket.status} color={getStatusColor(ticket.status)} />
              </TableCell>

              {!compact && <TableCell>{ticket.created_by}</TableCell>}

              {!compact && (
                <TableCell>
                  <Select
                    size="small"
                    displayEmpty
                    value={assignments[ticket.id] || ""}
                    onChange={(e) => assignTicket(ticket.id, e.target.value)}
                    sx={{ minWidth: 160 }}
                  >
                    <MenuItem value="">
                      <em>Sin asignar</em>
                    </MenuItem>
                    {ASSIGNEES.map((name) => (
                      <MenuItem key={name} value={name}>{name}</MenuItem>
                    ))}
                  </Select>
                </TableCell>
              )}

              <TableCell>
                {NEXT_STEP[ticket.status] && (
                  <Button
                    variant="contained"
                    color="primary"
                    size="small"
                    onClick={() => advanceTicket(ticket.id, NEXT_STEP[ticket.status].status)}
                  >
                    {NEXT_STEP[ticket.status].label}
                  </Button>
                )}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
