// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import BarcodeCalidad from '../components/BarcodeCalidad.vue';
import BarcodeEmpaquetado from '@/components/BarcodeEmpaquetado.vue';

const routes = [
  {
    path: '/calidad',  // Cambiado a 'calidad'
    name: 'Calidad',
    component: BarcodeCalidad,
  },
  {
    path: '/empaquetado',  // Cambiado a 'calidad'
    name: 'Empaquetado',
    component: BarcodeEmpaquetado,
  },
 
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
