<template>
  <div id="app">
    <header>
      <h1>Registro de Lectura de Empaquetado</h1>
    </header>
    <main>
      <section v-if="historial.length > 0" class="historial-cajas">
        <h2>Últimos Códigos Leídos por Calidad</h2>
        <div class="historial-grid">
          <div 
            v-for="(producto, index) in historialFiltrado" 
            :key="index" 
            class="codigo-card"
          >
            <p><strong>Código OF:</strong> {{ producto.codigoof }}</p>
            <p><strong>Código Producto:</strong> {{ producto.codigoproducto }}</p>
            <p><strong>Descripción:</strong> {{ producto.descripcion }}</p>
            <p><strong>Descripción Completa:</strong> {{ producto.descripcioncompleta }}</p>
            <p><strong>Largo:</strong> {{ producto.largo }}</p>
            <p><strong>Ancho:</strong> {{ producto.ancho }}</p>
            <p><strong>Fecha de Creación:</strong> {{ producto.fechacreacion }}</p>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script>
export default {
  data() {
    return {
      historial: [],
      socket: null,
    };
  },
  computed: {
    historialFiltrado() {
      // Filtra los productos que han sido leídos en calidad
      return this.historial.filter(producto => producto.lecturacalidadactiva);
    }
  },
  created() {
    this.socket = new WebSocket("ws://127.0.0.1:8000/ws");
    this.socket.onopen = () => {
      console.log("WebSocket connection established");
    };
    this.socket.onerror = (error) => {
      console.error("WebSocket error:", error);
    };
    this.socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'update') {
        this.historial.unshift(data.producto);
        if (this.historial.length > 10) {
          this.historial.pop();  // Limita la lista a 10 productos
        }
        console.log("Updated historial:", this.historial); // Log the updated historial
      }
    };
  },
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');

* {
  font-family: 'Roboto', sans-serif;
  box-sizing: border-box;
}

#app {
  background-color: #f5f5f5;
  padding: 40px;
  border-radius: 12px;
  max-width: 800px;
  margin: 0 auto;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

header {
  text-align: center;
  margin-bottom: 20px;
}

h1 {
  font-size: 28px;
  color: #333;
}

.historial-cajas {
  margin-top: 20px;
  background-color: #ffffff;
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 20px;
}

.historial-cajas h2 {
  font-size: 24px;
  margin-bottom: 10px;
}

.historial-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.codigo-card {
  background-color: #f9f9f9;
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s, box-shadow 0.3s;
}

.codigo-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
}
</style>
