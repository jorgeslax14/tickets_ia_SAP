import React, { useState } from "react";
import {
  Box, Paper, TextField, Button, Typography, Alert,
  FormControl, FormLabel, RadioGroup, FormControlLabel, Radio
} from "@mui/material";

const Login = ({ onLogin }) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("usuario");
  const [error, setError] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!username || !password) {
      setError("Usuario y contraseña son requeridos");
      return;
    }

    // TODO: validar contra el backend cuando exista autenticación real.
    setError("");
    onLogin({ username, role });
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
            label="Usuario"
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

          <FormControl sx={{ mt: 1 }}>
            <FormLabel>Rol</FormLabel>
            <RadioGroup
              row
              value={role}
              onChange={(e) => setRole(e.target.value)}
            >
              <FormControlLabel value="usuario" control={<Radio />} label="Usuario" />
              <FormControlLabel value="administrador" control={<Radio />} label="Administrador" />
            </RadioGroup>
          </FormControl>

          {error && <Alert severity="error" sx={{ mt: 1 }}>{error}</Alert>}

          <Button
            type="submit"
            variant="contained"
            fullWidth
            sx={{ mt: 2 }}
          >
            Ingresar
          </Button>
        </form>
      </Paper>
    </Box>
  );
};

export default Login;
