import { useEffect, useState } from "react";
import axios from "axios";
import { Button } from "@mui/material";

// MUI
import {
  Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Paper, Chip, CircularProgress
} from "@mui/material";

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

  useEffect(() => {
    axios.get("http://127.0.0.1:8000/tickets")
      .then(res => {
        setTickets(res.data.data); // 👈 importante
        setLoading(false);
      })
      .catch(err => {
        console.error(err, "ACA");
        setLoading(false);
      });
  }, []);

  const takeTicket = async (id) => {
    try {
      await axios.put(`http://127.0.0.1:8000/tickets/${id}`);

      // 🔄 Refrescar tickets después de actualizar
      const res = await axios.get("http://127.0.0.1:8000/tickets");
      setTickets(res.data.data);

    } catch (error) {
      console.error(error);
    }
  };

  if (loading) return <CircularProgress />;

  const filtered = tickets.filter(t => t.status === "OPEN");
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

              {/* PRIORIDAD */}
              <TableCell>
                <Chip
                  label={ticket.priority}
                  color={getPriorityColor(ticket.priority)}
                />
              </TableCell>

              {/* ESTADO */}
              <TableCell>
                <Chip
                  label={ticket.status}
                  color={getStatusColor(ticket.status)}
                />
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
                  </Button>)}
              </TableCell>



            </TableRow>
          ))}
        </TableBody>
      </Table>

    </TableContainer>
  );
}