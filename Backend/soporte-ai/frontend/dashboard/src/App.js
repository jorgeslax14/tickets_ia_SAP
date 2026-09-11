import React, { useState } from "react";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import UserTicketsPage from "./pages/UserTicketsPage";

function App() {
  // 1. Inicializamos el estado leyendo de localStorage para persistir la sesión al recargar
  const [session, setSession] = useState(() => {
    try {
      const savedSession = localStorage.getItem("session");
      return savedSession ? JSON.parse(savedSession) : null;
    } catch (e) {
      console.error("Error al leer el localStorage", e);
      return null;
    }
  });

  // 2. Guardamos la sesión en localStorage al iniciar sesión exitosamente
  const handleLogin = (userSession) => {
    setSession(userSession);
    localStorage.setItem("session", JSON.stringify(userSession));
  };

  // 3. Limpiamos localStorage al cerrar sesión (FE-003)
  const handleLogout = () => {
    setSession(null);
    localStorage.removeItem("session");
  };

  if (!session) {
    return <Login onLogin={handleLogin} />;
  }

  if (session.role === "admin") {
    return <Dashboard user={session.username} onLogout={handleLogout} />;
  }

  return <UserTicketsPage user={session.username} userId={session.id} onLogout={handleLogout} />;
}

export default App;