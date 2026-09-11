import React, { useState } from "react";
import {
  Box, Paper, TextField, Button, Typography, Alert
} from "@mui/material";
import { login } from "../services/api";

const Login = ({ onLogin }) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!username || !password) {
      setError("Usuario y contraseña son requeridos");
      return;
    }

    setError("");
    setSubmitting(true);

    try {
      const res = await login(username, password);
      
      // Manejo seguro por si el backend devuelve el objeto directo o envuelto en .data
      const user = res.data.data || res.data;
      
      onLogin({ 
        id: user.id, 
        username: user.name || user.username, 
        role: user.role || user.role_id 
      });
    } catch (err) {
      setError(err.response?.data?.detail || "No se pudo validar el usuario");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Box
      sx={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        minHeight: "100vh",
        bgcolor: "#f5f5f5"
      }}
    >
      <Paper elevation={3} sx={{ p: 4, width: 340 }}>
        <Typography variant="h5" align="center" gutterBottom>
          🎯 Soporte SAP
        </Typography>
        <Typography variant="body2" align="center" color="text.secondary" sx={{ mb: 3 }}>
          Ingresa para ver el dashboard de tickets
        </Typography>

        <form onSubmit={handleSubmit}>
          <TextField
            label="Usuario / Correo"
            fullWidth
            margin="normal"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <TextField
            label="Contraseña"
            type="password"
            fullWidth
            margin="normal"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          {error && <Alert severity="error" sx={{ mt: 1 }}>{error}</Alert>}

          <Button
            type="submit"
            variant="contained"
            fullWidth
            disabled={submitting}
            sx={{ mt: 2 }}
          >
            {submitting ? "Verificando..." : "Ingresar"}
          </Button>
        </form>
      </Paper>
    </Box>
  );
};

export default Login;