import { useEffect, useState } from "react";
import {
  Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Paper, Chip, CircularProgress
} from "@mui/material";
import { getTicketHistory } from "../services/api";

export default function TicketHistoryTable({ compact = false, assignedTo }) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getTicketHistory()
      .then(res => setHistory(res.data.data))
      .catch(err => console.error("Error cargando historial:", err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <CircularProgress />;

  const visibleHistory = history.filter(
    item => assignedTo == null || item.ticket?.assigned_to === assignedTo
  );

  return (
    <TableContainer component={Paper} sx={{ mt: 4 }}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell><b>{compact ? "ID" : "Ticket ID"}</b></TableCell>
            <TableCell><b>Título</b></TableCell>
            <TableCell><b>Módulo SAP</b></TableCell>
            <TableCell><b>Transacción</b></TableCell>
            <TableCell><b>Prioridad</b></TableCell>
            {compact ? (
              <>
                <TableCell><b>Estado</b></TableCell>
                <TableCell><b>Acciones</b></TableCell>
              </>
            ) : (
              <>
                <TableCell><b>Evento</b></TableCell>
                <TableCell><b>Archivado el</b></TableCell>
              </>
            )}
          </TableRow>
        </TableHead>

        <TableBody>
          {visibleHistory.map(item => (
            <TableRow key={item.id}>
              <TableCell>{item.ticket_id}</TableCell>
              <TableCell>{item.ticket?.title}</TableCell>
              <TableCell>{item.ticket?.module}</TableCell>
              <TableCell>{item.ticket?.transaction_code}</TableCell>
              <TableCell>
                {item.ticket?.priority != null && <Chip label={item.ticket.priority} />}
              </TableCell>
              {compact ? (
                <>
                  <TableCell><Chip label="DONE" color="success" /></TableCell>
                  <TableCell>{/* ya finalizado, sin acciones disponibles */}</TableCell>
                </>
              ) : (
                <>
                  <TableCell>{item.event}</TableCell>
                  <TableCell>{item.archived_at}</TableCell>
                </>
              )}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
