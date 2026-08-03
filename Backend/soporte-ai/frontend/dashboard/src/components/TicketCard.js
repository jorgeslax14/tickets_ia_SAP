import React from "react";

const getPriorityColor = (priority) => {
  if (priority >= 8) return "red";
  if (priority >= 5) return "orange";
  return "green";
};

const TicketCard = ({ ticket }) => {
  return (
    <div style={{
      border: "1px solid #ccc",
      padding: "10px",
      margin: "10px",
      borderRadius: "8px"
    }}>
      <h3>{ticket.title}</h3>
      <p>{ticket.description}</p>

      <p><b>Módulo:</b> {ticket.module}</p>
      <p><b>Transacción:</b> {ticket.transaction_code}</p>

      <p style={{ color: getPriorityColor(ticket.priority) }}>
        <b>Prioridad:</b> {ticket.priority}
      </p>

      <p><b>Estado:</b> {ticket.status}</p>
    </div>
  );
};

export default TicketCard;