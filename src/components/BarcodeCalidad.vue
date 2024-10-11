<template>
  <div id="app">
    <h1>Registro de Lectura de Calidad</h1>
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

    <!-- Cuadro grande para el producto actual -->
    <div v-if="producto" class="producto-detalles">
      <h2>Detalles del Producto</h2>
      <p><strong>Código OF:</strong> {{ producto.codigoof }}</p>
      <p><strong>Código Producto:</strong> {{ producto.codigoproducto }}</p>
      <p><strong>Descripción:</strong> {{ producto.descripcion }}</p>
      <p><strong>Descripción Completa:</strong> {{ producto.descripcioncompleta }}</p>
      <p><strong>Largo:</strong> {{ producto.largo }}</p>
      <p><strong>Ancho:</strong> {{ producto.ancho }}</p>
    </div>

    <!-- Historial de códigos OF -->
    <div class="historial-cajas" v-if="historial.length > 0">
      <h2>Últimos Códigos Leídos</h2>
      <div class="historial-grid">
        <div 
          v-for="(producto, index) in historial" 
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
          <button @click="eliminarRegistro(producto.codigoof)">Eliminar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      codigo: '',
      producto: null,
      historial: [],
      error: null,
      loading: false,
    };
  },
  methods: {
    async registrarLectura() {
      this.error = null;
      this.loading = true; // Start loading
      try {
        // Validate input
        if (!this.codigo) {
          throw new Error("Por favor ingrese un código válido.");
        }

        // Obtener los datos del producto
        const getResponse = await fetch(`http://127.0.0.1:8000/productos/of/${this.codigo}`);
        
        if (!getResponse.ok) {
          throw new Error("Producto no encontrado.");
        }

        const producto = await getResponse.json();

        // Verificar si ya ha sido leído por calidad
        if (producto.lecturacalidadactiva) {
          // Eliminar del historial si ya fue leído
          this.historial = this.historial.filter(p => p.codigoof !== producto.codigoof);
          throw new Error("Este código OF ya ha sido leído por calidad.");
        }

        // Registrar la lectura
        const putResponse = await fetch(`http://127.0.0.1:8000/productos/of/${this.codigo}/lectura`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            horaleccalidad: new Date().toISOString(),
            lecturacalidadactiva: true
          })
        });

        if (!putResponse.ok) {
          throw new Error("No se pudo registrar la lectura.");
        }

        // Mover el producto actual al historial si existe
        if (this.producto) {
          this.historial.unshift(this.producto);
          if (this.historial.length > 10) {
            this.historial.pop();
          }
        }

        // Actualizar el producto actual
        this.producto = producto;

        // Limpiar el campo de entrada
        this.codigo = '';
      } catch (err) {
        this.error = err.message;
      } finally {
        this.loading = false; // Stop loading
      }
    },
    eliminarRegistro(codigoof) {
      this.historial = this.historial.filter(producto => producto.codigoof !== codigoof);
    }
  },
};
</script>
<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');

* {
  font-family: 'Roboto', sans-serif;
}

#app {
  background-color: #f5f5f5;
  padding: 40px;
  border-radius: 12px;
  max-width: 800px;
  margin: 0 auto;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

h1 {
  font-size: 28px;
  text-align: center;
  margin-bottom: 20px;
}

input {
  width: 100%;
  padding: 15px;
  margin-bottom: 20px;
  border: 2px solid #ccc;
  border-radius: 8px;
  font-size: 20px;
}

.loading {
  font-style: italic;
}

.error {
  color: red;
  margin-top: 20px;
  font-size: 18px;
  text-align: center;
}

.producto-detalles {
  padding: 20px;
  background-color: #ffffff;
  border: 1px solid #ccc;
  border-radius: 8px;
  margin-bottom: 20px;
}

.producto-detalles p {
  font-size: 24px;
  line-height: 1.6;
}

.historial-cajas {
  margin-top: 20px;
  background-color: #ffffff;
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 20px;
}

.historial-cajas h2 {
  font-size: 28px;
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
}

button {
  background-color: #ff4d4d;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 10px;
  cursor: pointer;
  margin-top: 10px;
}

button:hover {
  background-color: #ff1a1a;
}
</style>