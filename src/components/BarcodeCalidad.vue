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
          placeholder="Escanea la matrícula"
          aria-label="Matrícula"
        />
        <div v-if="loading" class="loading">Cargando...</div>
        <div v-if="error" class="error">
          <p>{{ error }}</p>
        </div>
      </section>

      <section v-if="producto" class="producto-detalles">
        <h2>Detalles del Producto</h2>
        <p><strong>Matrícula:</strong> {{ producto.matricula }}</p>
        <p><strong>Código Producto:</strong> {{ producto.codigoproducto }}</p>
        <p><strong>Descripción:</strong> {{ producto.descripcion }}</p>      
        <p>Largo:  <strong>{{ producto.largo }}</strong></p>
        <p>Ancho: <strong>{{ producto.ancho }}</strong></p> 
      </section>

      <section v-if="historial.length > 0" class="historial-cajas">
        <h2>Últimas Matrículas Leídas</h2>
        <div class="historial-grid">
          <div 
            v-for="(histProducto, index) in historial.filter(p => p.matricula !== producto?.matricula)" 
            :key="index" 
            class="codigo-card"
          >
            <p>Matrícula: <strong>{{ histProducto.matricula }}</strong></p>
            <p>Código Producto: <strong>{{ histProducto.codigoproducto }}</strong></p>
            <p>Descripción: <strong>{{ histProducto.descripcion }}</strong></p>
            <p>Largo:  <strong>{{ histProducto.largo }}</strong></p>
            <p>Ancho: <strong>{{ histProducto.ancho }}</strong></p>
            <p>Fecha de Creación: <strong>{{ histProducto.fechacreacion }}</strong></p>
          </div>        
        </div>
      </section>

      <!-- Popup de confirmación con códigos de barras -->
      <div v-if="showConfirmPopup" class="popup">
          <div class="popup-content">
            <!-- Mostrar la matrícula -->
            <p>Esta matrícula ya ha sido leída por calidad.</p>
            <p>¿Quiere sacar de la línea este producto?</p>
            <p>Escanee "Sí" para sacar o "No" para cancelar.</p>

            <!-- Códigos de barras -->
            <div class="barcode-container">
              <svg id="barcodeSi"></svg>
              <svg id="barcodeNo"></svg>
            </div>
          </div>
      </div>
    </main>
  </div>
</template>

<script>
import JsBarcode from 'jsbarcode'; // Importamos JsBarcode para generar los códigos de barras

export default {
  data() {
    return {
      codigo: '',
      producto: null,
      historial: [],
      error: null,
      loading: false,
      socket: null,
      showConfirmPopup: false,
      productoParaEliminar: null,
      isConfirming: false, // Bloqueo para evitar confirmaciones múltiples
    };
  },
  created() {
    // Inicializamos el WebSocket y escuchamos los mensajes entrantes
    this.socket = new WebSocket("ws://127.0.0.1:8000/ws");
    this.socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'update') {
        if (!this.producto || this.producto.matricula !== data.producto.matricula) {
          const exists = this.historial.some(p => p.matricula === data.producto.matricula);
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
  mounted() {
    // Escuchar todos los escaneos
    window.addEventListener('keyup', this.detectarEscaneo);
  },
  beforeUnmount() {
    // Limpiar el listener al destruir el componente
    window.removeEventListener('keyup', this.detectarEscaneo);
  },
  methods: {
    async registrarLectura() {
      this.error = null;
      this.loading = true;
      try {
        // Filtrar el escaneo de "SI" o "NO" antes de hacer una solicitud al servidor
        const valorEscaneado = this.codigo.toUpperCase().trim();

        if (valorEscaneado === "SI") {
          await this.confirmarEliminacion();  // Confirmar eliminación si se escanea "Sí"
          return;
        } else if (valorEscaneado === "NO") {
          this.cancelarEliminacion();  // Cancelar eliminación si se escanea "No"
          return;
        }

        // Si no es "SI" o "NO", proceder con la solicitud GET al servidor
        if (!this.codigo) {
          throw new Error("Por favor ingrese una matrícula válida.");
        }

        const getResponse = await fetch(`http://127.0.0.1:8000/productos/${this.codigo}`);
        
        if (!getResponse.ok) {
          throw new Error("Producto no encontrado.");
        }

        const producto = await getResponse.json();

        if (producto.lecturacalidadactiva) {
          this.productoParaEliminar = producto;
          this.showConfirmPopup = true; // Mostrar popup cuando el producto ya fue leído
          this.codigo = '';
          this.$nextTick(() => this.generateBarcodes()); // Asegurar que los códigos se generen después de que el DOM esté cargado
          this.loading = false;
          return;
        }

        const putResponse = await fetch(`http://127.0.0.1:8000/productos/${this.codigo}/calidad`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          }
        });

        if (!putResponse.ok) {
          throw new Error("No se pudo registrar la lectura.");
        }

        if (this.producto && this.producto.matricula !== producto.matricula) {
          const exists = this.historial.some(p => p.matricula === this.producto.matricula);
          if (!exists) {
            this.historial.unshift(this.producto);
            if (this.historial.length > 4) {
              this.historial.pop();
            }
          }
        }
        

        this.producto = producto;
        this.codigo = '';
        this.socket.send(JSON.stringify({ type: 'update', producto: this.producto })); // Enviar actualización por WebSocket
      } catch (err) {
        this.error = err.message;
      } finally {
        this.loading = false;
      }
    },

    // Detectar el escaneo de "Sí" o "No" cuando el popup está activo
    detectarEscaneo() {
      if (!this.showConfirmPopup) return;

      const valorEscaneado = this.codigo.toUpperCase().trim();
      if (valorEscaneado === "SI") {
        this.confirmarEliminacion();
      } else if (valorEscaneado === "NO") {
        this.cancelarEliminacion();
      }
    },

    generateBarcodes() {
      JsBarcode("#barcodeSi", "SI", { format: "CODE128", lineColor: "#000", width: 2, height: 60, displayValue: true });
      JsBarcode("#barcodeNo", "NO", { format: "CODE128", lineColor: "#000", width: 2, height: 60, displayValue: true });
    },

    async confirmarEliminacion() {
      // Verificar si ya se está ejecutando una confirmación para evitar duplicados
      if (this.isConfirming) return;

      this.isConfirming = true; // Bloqueamos nuevas confirmaciones hasta que termine

      try {
        const response = await fetch(`http://127.0.0.1:8000/productos/${this.productoParaEliminar.matricula}/reset`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          }
        });
        if (!response.ok) {
          throw new Error("No se pudo eliminar el producto.");
        }

        // Eliminar el producto del historial
        this.historial = this.historial.filter(p => p.matricula !== this.productoParaEliminar.matricula);

        // Si el producto actual en el recuadro grande es el mismo que el que se va a eliminar, limpiar la variable 'producto'
        if (this.producto?.matricula === this.productoParaEliminar.matricula) {
          this.producto = null;
        }

        // Enviar mensaje de eliminación por WebSocket
        this.socket.send(JSON.stringify({ type: 'delete', matricula: this.productoParaEliminar.matricula }));

        this.productoParaEliminar = null;
        this.showConfirmPopup = false;
        this.codigo = '';
      } catch (err) {
        this.error = err.message;
      } finally {
        this.isConfirming = false; // Desbloqueamos la confirmación
      }
    },

    cancelarEliminacion() {
      this.productoParaEliminar = null;
      this.showConfirmPopup = false;
      this.codigo = '';
      this.$refs.codigoInput.focus(); // Reenfocar el input
    }
  },
};
</script>




<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');

* {
  font-family: 'Roboto', sans-serif;
  box-sizing: border-box;
}

.popup {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.popup-content {
  background: white;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
}

.barcode-container {
  margin-top: 30px;
  display: flex;
  justify-content: space-around;
 
}

.barcode-container svg {
  width: 250px;
  height: 100px;
}

.loading {
  font-style: italic;
  color: #9ec4ec;
}

.error {
  color: red;
  margin-top: 10px;
  text-align: center;
}

.producto-detalles {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
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
  border-color: #a4ccf7;
}

.loading {
  font-style: italic;
  color: #9ec4ec;
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
  background-color: #c0dbf1;
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

/* Estilos para el popup */
.popup {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 40px;
 
}

.popup-content {
  background: white;
  padding: 20px;
  border-radius: 5px;
  text-align: center;
}

.popup-buttons {
  display: flex;
  justify-content: space-around;
  margin-top: 20px;
}

.btn-yes {
  background-color: red;
  color: white;
  border: none;
  padding: 10px 50px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 25px;
}

.btn-no {
  background-color: green;
  color: white;
  border: none;
  padding: 10px 50px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 25px;
}
</style>