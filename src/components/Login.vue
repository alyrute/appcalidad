<template>
    <div class="login-container">
      <h1>Iniciar Sesión</h1>
      <input v-model="username" placeholder="Nombre de Usuario" />
      <input type="password" v-model="password" placeholder="Contraseña" />
      <button @click="login">Iniciar Sesión</button>
      <div v-if="error" style="color: red;">{{ error }}</div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'LoginComponent',
    data() {
      return {
        username: '',
        password: '',
        error: null,
      };
    },
    methods: {
      async login() {
        if (this.username === 'admin' && this.password === '1234') {
          localStorage.setItem('authenticated', 'true');
          this.$router.push('/scanner');
        } else {
          this.error = 'Usuario o contraseña incorrectos.';
        }
      },
    },
  };
  </script>
  
  <style scoped>
  .login-container {
    display: flex;
    flex-direction: column;
    max-width: 300px;
    margin: 100px auto;
    text-align: center;
  }
  input {
    margin-bottom: 15px;
    padding: 10px;
    width: 100%;
  }
  button {
    padding: 10px;
    background-color: #5cb85c;
    color: white;
    border: none;
    cursor: pointer;
  }
  </style>