<script setup>
import { onMounted, ref } from 'vue'
import { getPublicCode } from '../api'
import CodeDisplay from '../components/CodeDisplay.vue'

const code = ref('')
const error = ref('')
const loading = ref(true)

async function load() {
  loading.value = true
  error.value = ''
  try {
    code.value = (await getPublicCode()).code
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <h1>Задание 1: случайный код</h1>

  <CodeDisplay :code="code" :loading="loading" />
  <p v-if="error" class="error">{{ error }}</p>

  <p class="hint">Обновите страницу (F5), и код изменится.</p>
  <button :disabled="loading" @click="load">Получить новый код</button>
</template>