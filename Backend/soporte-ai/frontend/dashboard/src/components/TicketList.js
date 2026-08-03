import React, { useEffect, useState } from "react";
import { getTickets } from "../services/api";
import TicketCard from "./TicketCard";

const TicketList = () => {
  const [tickets, setTickets] = useState([]);

  useEffect(() => {
    fetchTickets();
  }, []);

  const fetchTickets = async () => {
    try {
      const response = await getTickets();
      setTickets(response.data);
    } catch (error) {
      console.error("Error cargando tickets", error);
    }
  };

  return (
    <div>
      <h2>Tickets</h2>
      {tickets.map((ticket) => (
        <TicketCard key={ticket.id} ticket={ticket} />
      ))}
    </div>
  );
};

export default TicketList;