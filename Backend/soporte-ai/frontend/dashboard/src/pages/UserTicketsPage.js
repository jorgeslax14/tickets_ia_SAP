import React, { useState } from "react";
import { Box, Typography, Button, Tabs, Tab } from "@mui/material";
import TicketTable from "../components/TicketTable";
import TicketHistoryTable from "../components/TicketHistoryTable";

// Cada pestaña corresponde a una etapa del ciclo de vida del ticket:
// OPEN (asignado, listo para tomar) -> IN_PROGRESS (en proceso) -> DONE (finalizado, en ticket_history).
const TABS = [
  { label: "Tickets asignados", statusFilter: "OPEN" },
  { label: "Tickets en proceso", statusFilter: "IN_PROGRESS" },
  { label: "Tickets finalizados", statusFilter: "DONE" },
];

const UserTicketsPage = ({ user, onLogout }) => {
  const [tabIndex, setTabIndex] = useState(0);
  const currentTab = TABS[tabIndex];

  return (
    <div style={{ padding: "20px" }}>
      <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <Typography variant="h4">🎫 Mis Tickets</Typography>
        <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
          {user && <Typography variant="body1">Hola, {user}</Typography>}
          <Button variant="outlined" size="small" onClick={onLogout}>
            Cerrar sesión
          </Button>
        </Box>
      </Box>

      <Tabs value={tabIndex} onChange={(_, value) => setTabIndex(value)} sx={{ mt: 2 }}>
        {TABS.map((tab) => (
          <Tab key={tab.label} label={tab.label} />
        ))}
      </Tabs>

      {currentTab.statusFilter === "DONE" ? (
        <TicketHistoryTable compact />
      ) : (
        <TicketTable compact statusFilter={currentTab.statusFilter} />
      )}
    </div>
  );
};

export default UserTicketsPage;
