const { Pool } = require('pg');

const pool = new Pool({
  user: process.env.DB_USER, // Lee el nombre de usuario desde la variable de entorno DB_USER
  host: process.env.DB_HOST, // Lee el host desde la variable de entorno DB_HOST
  database: process.env.DB_NAME, // Lee el nombre de la base de datos desde la variable de entorno DB_NAME
  password: process.env.DB_PASSWORD, // Lee la contraseña desde la variable de entorno DB_PASSWORD
  port: process.env.DB_PORT || 5432, // Lee el puerto desde la variable de entorno DB_PORT, o usa 5432 por defecto
});

module.exports = pool;
