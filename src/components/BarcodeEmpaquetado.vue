<template>
  <div class="scanner-container">
    <div class="header">
      <img src="../assets/logoMC.png" alt="Logo" class="logo" width="150"/>
      <h1>EMPAQUETADO - Detalles del Producto</h1>
    </div>
    <input v-model="codigoOF" @keydown.enter="verificarCodigo" placeholder="Escanea o ingresa el código OF" />
    <div v-if="datosProducto" class="producto-detalles">
      <h2>Detalles del Producto</h2>
      <p><strong>Código OF:</strong> {{ datosProducto.codigoof }}</p>
      <p><strong>Código Producto:</strong> {{ datosProducto.codigoproducto }}</p>
      <p><strong>Descripción:</strong> {{ datosProducto.descripcion }}</p>
      <p><strong>Largo:</strong> {{ datosProducto.largo }}</p>
      <p><strong>Ancho:</strong> {{ datosProducto.ancho }}</p>
      <p><strong>Fecha de Creación:</strong> {{ datosProducto.fechacreacion }}</p>
      <p><strong>Lectura Calidad:</strong> {{ datosProducto.lecturacalidadactiva ? 'Realizada' : 'No realizada' }}</p>
      <p><strong>Lectura Empaquetado:</strong> {{ datosProducto.lecturaempaquetadoactiva ? 'Realizada' : 'No realizada' }}</p>
    </div>
    <div v-if="error" class="error-message">{{ error }}</div>
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex';

export default {
  data() {
    return {
      codigoOF: '',
      error: null,
      loading: false,
    };
  },
  computed: {
    ...mapState(['datosProducto']),
  },
  methods: {
    ...mapActions(['registrarLecturaEmpaquetado']),
    async verificarCodigo() {
      this.loading = true; // Inicia la carga
      try {
        await this.registrarLecturaEmpaquetado(this.codigoOF);
        this.error = null;
        console.log('Código OF verificado:', this.codigoOF);
        console.log('Datos del producto:', this.datosProducto); // Muestra el estado actualizado
      } catch (err) {
        this.error = 'Error al registrar la lectura de empaquetado';
      } finally {
        this.loading = false; // Termina la carga
      }
    },
  },
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');

* {
  font-family: 'Roboto', sans-serif;
}

.scanner-container {
  background-color: #f5f5f5;
  padding: 40px;
  border-radius: 12px;
  max-width: 1600px;
  margin: 0 auto;
}
</style>