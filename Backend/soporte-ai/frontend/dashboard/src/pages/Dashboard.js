import React from "react";
import TicketList from "../components/TicketList";
import TicketTable from "../components/TicketTable";

const Dashboard = () => {
  return (
    <div>
      <h1>📊 Dashboard Soporte SAP</h1>
      <TicketTable />
    </div>
  );
};

export default Dashboard;