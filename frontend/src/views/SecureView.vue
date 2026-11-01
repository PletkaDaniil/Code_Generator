<script setup>
import { ref } from 'vue'
import { getSecureCode, login, register } from '../api'
import CodeDisplay from '../components/CodeDisplay.vue'

const mode = ref('login')
const username = ref('')
const password = ref('')
const code = ref('')
const error = ref('')
const info = ref('')
const loading = ref(false)

function switchMode(next) {
  mode.value = next
  error.value = ''
  info.value = ''
}

function logout() {
  code.value = ''
  switchMode('login')
}

async function submit() {
  error.value = ''
  info.value = ''
  loading.value = true
  try {
    if (mode.value === 'register') {
      await register(username.value, password.value)
      password.value = ''
      mode.value = 'login'
      info.value = 'Регистрация прошла успешно. Теперь войдите.'
      return
    }

    const { token } = await login(username.value, password.value)

    // Токен будет жить только в этой локальной переменной и нигде не сохраняется,
    // поэтому после обновления страницы он потеряется, и нужен новый вход
    code.value = (await getSecureCode(token)).code
    username.value = ''
    password.value = ''
    mode.value = 'code'
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <h1>Задание 2: код после авторизации</h1>

  <template v-if="mode === 'code'">
    <CodeDisplay :code="code" />
    <p class="hint">Обновите страницу, и вы выйдете из системы.</p>
    <button @click="logout">Выйти</button>
  </template>

  <form v-else class="form" @submit.prevent="submit">
    <h2>{{ mode === 'login' ? 'Вход' : 'Регистрация' }}</h2>

    <input
      v-model="username"
      placeholder="Логин"
      autocomplete="username"
      required
      autofocus
    />
    <input
      v-model="password"
      type="password"
      placeholder="Пароль"
      :autocomplete="mode === 'login' ? 'current-password' : 'new-password'"
      required
    />

    <p v-if="info" class="info">{{ info }}</p>
    <p v-if="error" class="error">{{ error }}</p>

    <button type="submit" :disabled="loading">
      {{ mode === 'login' ? 'Войти' : 'Зарегистрироваться' }}
    </button>

    <button
      v-if="mode === 'login'"
      type="button"
      class="link"
      @click="switchMode('register')"
    >
      Нет аккаунта? Зарегистрироваться
    </button>
    <button v-else type="button" class="link" @click="switchMode('login')">
      Уже есть аккаунт? Войти
    </button>
  </form>
</template>