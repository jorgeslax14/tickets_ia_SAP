import React from "react";
import TicketTable from "./components/TicketTable";
import TicketList from "./components/TicketList";

function App() {
  return (
    <div style={{ padding: "20px" }}>
      <h1>🎯 Dashboard de Tickets</h1>
      <TicketTable />  
    </div>
  );
}

export default App;