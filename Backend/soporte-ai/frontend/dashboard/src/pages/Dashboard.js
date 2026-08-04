import React from "react";
import { Box, Typography, Button } from "@mui/material";
import TicketsPanel from "../components/TicketsPanel";

const Dashboard = ({ user, onLogout }) => {
  return (
    <div style={{ padding: "20px" }}>
      <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <Typography variant="h4">📊 Dashboard Soporte SAP</Typography>
        <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
          {user && <Typography variant="body1">Hola, {user}</Typography>}
          <Button variant="outlined" size="small" onClick={onLogout}>
            Cerrar sesión
          </Button>
        </Box>
      </Box>

      <TicketsPanel />
    </div>
  );
};

export default Dashboard;
