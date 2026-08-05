import React, { useState } from "react";
import { ButtonGroup, Button } from "@mui/material";
import TicketTable from "./TicketTable";
import TicketHistoryTable from "./TicketHistoryTable";

export default function TicketsPanel() {
  const [view, setView] = useState("open");

  return (
    <div>
      <ButtonGroup sx={{ mt: 2 }}>
        <Button
          variant={view === "open" ? "contained" : "outlined"}
          onClick={() => setView("open")}
        >
          Tickets abiertos
        </Button>
        <Button
          variant={view === "history" ? "contained" : "outlined"}
          onClick={() => setView("history")}
        >
          Historial de tickets
        </Button>
      </ButtonGroup>

      {view === "open"
        ? <TicketTable statusFilter={["OPEN", "IN_PROGRESS"]} />
        : <TicketHistoryTable />}
    </div>
  );
}
