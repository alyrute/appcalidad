import axios from 'axios';

const api = axios.create({
  baseURL: 'http://192.168.1.33:8080/', // Cambia esto a la URL de tu API
  timeout: 10000, // Puedes ajustar el tiempo de espera si lo necesitas
});

export default api;
