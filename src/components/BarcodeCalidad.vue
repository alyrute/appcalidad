<template>
  <div id="app">
    <header class="header-grid">
      <img src="../assets/logoMC.png" alt="Logo de la empresa" class="logo" width="200" />
      <h1 class="titulo">Registro de Lectura de Calidad</h1>
    </header>
    <main>
      <section class="input-section">
        <input
          ref="codigoInput" 
          type="text"
          v-model="codigo"
          @keyup.enter="registrarLectura"
          placeholder="Escanea el código OF"
          aria-label="Código OF"
        />
        <div v-if="loading" class="loading">Cargando...</div>
        <div v-if="error" class="error">
          <p>{{ error }}</p>
        </div>
      </section>

      <section v-if="producto" class="producto-detalles">
        <h2>Detalles del Producto</h2>
        <p><strong>Código OF:</strong> {{ producto.codigoof }}</p>
        <p><strong>Código Producto:</strong> {{ producto.codigoproducto }}</p>
        <p><strong>Descripción:</strong> {{ producto.descripcion }}</p>
        <p><strong>Descripción Completa:</strong> {{ producto.descripcioncompleta }}</p>
        <p><strong>Largo:</strong> {{ producto.largo }}</p>
        <p><strong>Ancho:</strong> {{ producto.ancho }}</p>
      </section>

      <section v-if="historial.length > 0" class="historial-cajas">
        <h2>Últimos Códigos Leídos</h2>
        <div class="historial-grid">
          <div 
            v-for="(histProducto, index) in historial.filter(p => p.codigoof !== producto?.codigoof)" 
            :key="index" 
            class="codigo-card"
          >
            <p>Código OF: <strong>{{ histProducto.codigoof }}</strong></p>
            <p>Código Producto: <strong>{{ histProducto.codigoproducto }}</strong></p>
            <p>Descripción: <strong>{{ histProducto.descripcion }}</strong></p>
            <p>Descripción Completa: <strong>{{ histProducto.descripcioncompleta }}</strong></p>
            <p>Largo:  <strong>{{ histProducto.largo }}</strong></p>
            <p>Ancho:<strong>{{ histProducto.ancho }}</strong></p>
            <p>Fecha de Creación: <strong>{{ histProducto.fechacreacion }}</strong></p>
          </div>        </div>
      </section>
    </main>
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
      socket: null,
    };
  },
  created() {
    this.socket = new WebSocket("ws://127.0.0.1:8000/ws");
    this.socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'update') {
        if (!this.producto || this.producto.codigoof !== data.producto.codigoof) {
          const exists = this.historial.some(p => p.codigoof === data.producto.codigoof);
          if (!exists) {
            this.historial.unshift(data.producto);
            if (this.historial.length > 4) {
              this.historial.pop();
            }
          }
        }
      }
    };
  },
  methods: {
    async registrarLectura() {
      this.error = null;
      this.loading = true;
      try {
        if (!this.codigo) {
          throw new Error("Por favor ingrese un código válido.");
        }

        const getResponse = await fetch(`http://127.0.0.1:8000/productos/of/${this.codigo}`);
        
        if (!getResponse.ok) {
          throw new Error("Producto no encontrado.");
        }

        const producto = await getResponse.json();

        if (producto.lecturacalidadactiva) {
          this.error = `Este código OF ${producto.codigoof} ya ha sido leído por calidad.`;
          this.codigo = ''; // Limpiar el input
          this.$refs.codigoInput.focus(); // Reenfocar el input
          return;
        }

        const putResponse = await fetch(`http://127.0.0.1:8000/productos/of/${this.codigo}/calidad`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          }
        });

        if (!putResponse.ok) {
          throw new Error("No se pudo registrar la lectura.");
        }

        if (this.producto && this.producto.codigoof !== producto.codigoof) {
          const exists = this.historial.some(p => p.codigoof === this.producto.codigoof);
          if (!exists) {
            this.historial.unshift(this.producto);
            if (this.historial.length > 4) {
              this.historial.pop();
            }
          }
        }

        this.producto = producto;
        this.codigo = '';

        this.socket.send(JSON.stringify({ type: 'update', producto: this.producto }));
      } catch (err) {
        this.error = err.message;
      } finally {
        this.loading = false;
      }
    },
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
  max-width: 1800px;
  margin: 0 auto;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

header {
  text-align: center;
  margin-bottom: 20px;
}

h1 {
  font-size: 38px;
  color: #333;
}

.input-section {
  margin-bottom: 20px;
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

input:focus {
  border-color: #007BFF;
}

.loading {
  font-style: italic;
  color: #007BFF;
}

.error {
  color: red;
  margin-top: 10px;
  font-size: 10px;
  text-align: center;
  font-size: 35px;
}

.producto-detalles {
  padding: 20px;
  background-color: #ddee9f;
  border: 1px solid #ccc;
  border-radius: 8px;
  margin-bottom: 20px;
}

.producto-detalles {
  font-size: 30px;
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