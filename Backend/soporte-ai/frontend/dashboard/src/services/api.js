import axios from "axios";

const API = axios.create({
  baseURL: process.env.REACT_APP_API_URL || "http://127.0.0.1:8000"
});

export const getTickets = () => API.get("/tickets");

export const createTicket = (message, createdBy) =>
  API.post("/tickets", { message, created_by: createdBy });

export const updateTicketStatus = (ticketId, status) =>
  API.put(`/tickets/${ticketId}`, { status });

export const getTicketHistory = () => API.get("/tickets/history");

export const login = (username) => API.post("/login", { username });

export const getUsersByRole = (role) => API.get("/users", { params: { role } });

export const assignTicket = (ticketId, userId) =>
  API.put(`/tickets/${ticketId}/assign`, { assigned_to: userId });

export default API;
