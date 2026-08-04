import { useEffect, useState } from "react";
import {
  Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Paper, Chip, CircularProgress, Button
} from "@mui/material";
import { getTickets, updateTicketStatus } from "../services/api";

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

export default function TicketTable() {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);

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

  const takeTicket = async (id) => {
    try {
      await updateTicketStatus(id);
      await fetchTickets();
    } catch (error) {
      console.error("Error actualizando ticket:", error);
    }
  };

  if (loading) return <CircularProgress />;

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
            <TableCell><b>Creado por</b></TableCell>
            <TableCell><b>Asignado a</b></TableCell>
            <TableCell><b>Acciones</b></TableCell>
          </TableRow>
        </TableHead>

        <TableBody>
          {tickets.map(ticket => (
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

              <TableCell>{ticket.created_by}</TableCell>
              <TableCell>{ticket.assigned_to}</TableCell>

              <TableCell>
                {ticket.status === "OPEN" && (
                  <Button
                    variant="contained"
                    color="primary"
                    size="small"
                    onClick={() => takeTicket(ticket.id)}
                  >
                    Tomar
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
