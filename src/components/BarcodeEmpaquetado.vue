<template>
  <div id="app">
    <header class="header-grid">
      <img src="../assets/logoMC.png" alt="Logo de la empresa" class="logo" width="200" />
      <h1 class="titulo">Registro de Lectura de Empaquetado</h1>
    </header>
    <main>
      <section class="input-section">
        <input
          type="text"
          v-model="codigo"
          @keyup.enter="registrarLectura"
          placeholder="Escanea el código OF y presiona Enter"
          aria-label="Código OF"
        />
        <div v-if="loading" class="loading">Cargando...</div>
        <div v-if="error" class="error">
          <p>{{ error }}</p>
        </div>
      </section>

      <section v-if="historialFiltrado.length > 0" class="historial-cajas">
        <h2>Códigos Leídos por Calidad</h2>
        <div class="historial-grid">
          <div 
            v-for="(producto, index) in historialFiltrado.slice(0, 10)" 
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
      codigo: '',
      historial: [],
      socket: null,
      loading: false,
      error: null,
    };
  },
  computed: {
    historialFiltrado() {
      // Filtra los productos que han sido leídos en calidad y empaquetado, y los ordena del más antiguo al más reciente
      return this.historial
      .filter(producto => producto.lecturacalidadactiva && !producto.lecturaempaquetadoactiva)
        .reverse();
    }
  },
  methods: {
    async registrarLectura() {
      this.loading = true;
      this.error = null;
      try {
        const url = `http://127.0.0.1:8000/productos/of/${this.codigo}/empaquetado`;
        const options = {
          method: 'PUT',
        };
        const response = await fetch(url, options);

        if (!response.ok) {
          throw new Error('Error al registrar la lectura de empaquetado');
        }

        // Eliminar el producto del historial
        this.historial = this.historial.filter(producto => producto.codigoof !== this.codigo);
      } catch (error) {
        this.error = error.message;
      } finally {
        this.loading = false;
        this.codigo = ''; // Limpiar el campo de entrada
      }
    }
  },
  created() {
    this.socket = new WebSocket("ws://127.0.0.1:8000/ws");
    this.socket.onopen = () => {
      console.log("Conexión WebSocket establecida");
    };
    this.socket.onerror = (error) => {
      console.error("Error en WebSocket:", error);
    };
    this.socket.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'update') {
    // Verifica si el producto ya existe en el historial
    const productoExistente = this.historial.find(producto => producto.codigoof === data.producto.codigoof);
    
    if (!productoExistente) {
      this.historial.unshift(data.producto);
      
      // Si hay más de 10 productos, elimina el último
      if (this.historial.length > 10) {
        this.historial.pop();
      }
    }
  } else if (data.type === 'delete') {
    this.historial = this.historial.filter(producto => producto.codigoof !== data.codigoof);
    console.log("Producto eliminado:", data.codigoof);
  }
  };
  }
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
  max-width: 1800px;
  margin: 0 auto;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

header {
  text-align: center;
  margin-bottom: 20px;
}

h1 {
  font-size: 30px;
  color: #333;
}

input {
  width: 100%;
  padding: 15px;
  margin-bottom: 10px;
  border: 2px solid #ccc;
  border-radius: 8px;
  font-size: 20px;
  transition: border-color 0.3s;
}

.historial-cajas {
  margin-top: 20px;
  background-color: #ffffff;
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 20px;
}

.historial-cajas h2 {
  font-size: 30px;
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

.header-grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr); /* 12 columnas en total */
  align-items: center; /* Alinea verticalmente el logo y el título */
  gap: 10px; /* Espacio entre elementos */
}

.logo {
  grid-column: span 4; /* El logo ocupa 4 columnas */
  justify-self: start; /* Alinea el logo a la izquierda */
}

.titulo {
  grid-column: span 8; /* El título ocupa 8 columnas */
  justify-self: start; /* Alinea el título a la izquierda */
}

</style>