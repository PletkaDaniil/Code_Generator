<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <header class="nav">
    <RouterLink to="/">Задание 1</RouterLink>
    <RouterLink to="/secure">Задание 2</RouterLink>
  </header>

  <main class="container">
    <RouterView />
  </main>
</template>