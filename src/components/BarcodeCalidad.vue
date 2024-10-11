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
    <div v-if="loading">Cargando...</div>
    <div v-if="producto">
      <h2>Detalles del Producto</h2>
      <p><strong>Código OF:</strong> {{ producto.codigoof }}</p>
      <p><strong>Código Producto:</strong> {{ producto.codigoproducto || 'No disponible' }}</p>
      <p><strong>Descripción:</strong> {{ producto.descripcion || 'No disponible' }}</p>
      <p><strong>Descripción Completa:</strong> {{ producto.descripcioncompleta || 'No disponible' }}</p>
      <p><strong>Largo:</strong> {{ producto.largo || 'No disponible' }}</p>
      <p><strong>Ancho:</strong> {{ producto.ancho || 'No disponible' }}</p>
      <p><strong>Fecha de Creación:</strong> {{ producto.fechacreacion ? new Date(producto.fechacreacion).toLocaleString() : 'No disponible' }}</p>
    </div>
    <div v-if="error" class="error">
      <p>{{ error }}</p>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      codigo: '',
      producto: null,
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

        const putResponse = await fetch(`http://127.0.0.1:8000/productos/of/${this.codigo}/lectura`, {
          method: 'PUT',
        });

        if (!putResponse.ok) {
          throw new Error("No se pudo registrar la lectura.");
        }

        const getResponse = await fetch(`http://127.0.0.1:8000/productos/of/${this.codigo}`);
        
        if (!getResponse.ok) {
          throw new Error("Producto no encontrado.");
        }

        this.producto = await getResponse.json();
      } catch (err) {
        this.error = err.message;
      } finally {
        this.loading = false; // Stop loading
        this.codigo = ''; // Clear input
      }
    },
  },
};
</script>

<style>
#error {
  color: red;
}
.loading {
  font-style: italic;
}
</style>
