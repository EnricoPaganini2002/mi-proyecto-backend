const express = require('express');
const cors = require('cors');
const pool = require('./db'); // Importa el pool de conexiones
const app = express();
const port = 3000;

// Configura CORS para permitir las peticiones desde tu dominio de Vercel
const corsOptions = {
  origin: 'https://<your-vercel-app-name>.vercel.app', // Reemplaza con la URL de tu frontend en Vercel
  optionsSuccessStatus: 200 // some legacy browsers (IE11, various SmartTVs) choke on 204
}

app.use(cors(corsOptions));

app.get('/api/data', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM your_table');
    res.json(result.rows);
  } catch (err) {
    console.error(err);
    res.status(500).send('Error al obtener los datos');
  }
});

app.listen(port, () => {
  console.log(`Servidor escuchando en el puerto ${port}`);
});