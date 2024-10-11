// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import BarcodeCalidad from '../components/BarcodeCalidad.vue';

const routes = [
  {
    path: '/calidad',  // Cambiado a 'calidad'
    name: 'Calidad',
    component: BarcodeCalidad,
  },
  // Agrega más rutas aquí según sea necesario
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
