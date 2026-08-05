import React, { useState } from "react";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import UserTicketsPage from "./pages/UserTicketsPage";

function App() {
  const [session, setSession] = useState(null);

  if (!session) {
    return <Login onLogin={setSession} />;
  }

  const handleLogout = () => setSession(null);

  if (session.role === "administrador") {
    return <Dashboard user={session.username} onLogout={handleLogout} />;
  }

  return <UserTicketsPage user={session.username} onLogout={handleLogout} />;
}

export default App;
