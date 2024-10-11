<template>
  <div class="scanner-container">
    <div class="header">
      <img src="../assets/logoMC.png" alt="Logo" class="logo" width="150" />
      <h1>CALIDAD - Escaneo de Código OF</h1>
    </div>
    
    <input
      v-model="codigoOF"
      @keydown.enter="manejarLectura"
      placeholder="Escanea o ingresa el código OF"
    />
    <button @click="manejarLectura">Registrar Lectura</button>
    
    <div v-if="loading" class="loading-message">Cargando...</div>
    <div v-if="error" class="error-message">{{ error }}</div>

    <div v-if="datosProducto" class="producto-detalles">
      <h2>Detalles del Producto</h2>
      <p><strong>Código OF:</strong> {{ datosProducto.codigoof }}</p>
      <p><strong>Descripción:</strong> {{ datosProducto.descripcion }}</p>
      <p><strong>Lectura Calidad:</strong>
        <span :style="{ color: datosProducto.lecturacalidadactiva ? 'red' : 'black' }">
          {{ datosProducto.lecturacalidadactiva ? 'Ya ha sido leída' : 'No realizada' }}
        </span>
      </p>
    </div>
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex';

export default {
  data() {
    return {
      codigoOF: '',
    };
  },
  computed: {
    ...mapState(['datosProducto', 'loading', 'error']),
  },
  methods: {
    ...mapActions(['updateDatosProducto', 'registrarLecturaCalidad']),
    
    async manejarLectura() {
      this.error = null;
      try {
        await this.registrarLecturaCalidad(this.codigoOF);
        await this.updateDatosProducto(this.codigoOF);
      } catch (err) {
        this.error = 'Error al manejar la lectura';
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
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

h1 {
  font-size: 32px;
  text-align: center;
  margin-bottom: 20px;
}

input {
  width: 100%;
  padding: 15px;
  margin-bottom: 20px;
  border: 2px solid #ccc;
  border-radius: 8px;
  font-size: 26px;
}

.loading-message {
  font-size: 20px;
  text-align: center;
  color: blue;
}

.producto-detalles {
  padding: 20px;
  background-color: #ffffff;
  border: 1px solid #ccc;
  border-radius: 8px;
}

.producto-detalles p {
  font-size: 30px;
  line-height: 1.6;
}

.error-message {
  color: white;
  background-color: red;
  padding: 20px;
  margin-top: 20px;
  border-radius: 8px;
  font-size: 38px;
  text-align: center;
}

.header {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  align-items: center;
}

.header img {
  grid-column: span 4;
  padding: 25px;
}

.header h1 {
  grid-column: span 8;
  text-align: left;
  margin: 0;
}
</style>
