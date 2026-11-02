<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { getSecureCode, login, logout, register } from '../api'
import CodeDisplay from '../components/CodeDisplay.vue'

const mode = ref('login')
const username = ref('')
const password = ref('')
const code = ref('')
const error = ref('')
const info = ref('')
const loading = ref(false)
const secondsLeft = ref(0)

// токен хранится только в памяти страницы
let token = null
// оставшееся время действия сессии
let timerId = null

const timeLeft = computed(() => {
  const minutes = Math.floor(secondsLeft.value / 60)
  const seconds = String(secondsLeft.value % 60).padStart(2, '0')
  return `${minutes}:${seconds}`
})

// запускаем таймер сессии
function startTimer(seconds) {
  const expiresAt = Date.now() + seconds * 1000
  secondsLeft.value = seconds
  timerId = setInterval(() => {
    secondsLeft.value = Math.max(0, Math.ceil((expiresAt - Date.now()) / 1000))
    if (secondsLeft.value === 0) endSession('Сессия истекла. Войдите снова.')
  }, 1000)
}

function stopTimer() {
  clearInterval(timerId)
  timerId = null
}

// отзываем токен на сервере
function revokeToken(keepalive = false) {
  if (!token) return
  logout(token, keepalive).catch(() => {})
  token = null
}

function endSession(message = '') {
  stopTimer()
  revokeToken()
  code.value = ''
  error.value = ''
  info.value = message
  mode.value = 'login'
}

function switchMode(next) {
  mode.value = next
  error.value = ''
  info.value = ''
}

async function generate() {
  error.value = ''
  loading.value = true
  try {
    code.value = (await getSecureCode(token)).code
  } catch (e) {
    if (e.status === 401) endSession('Сессия истекла. Войдите снова.')
    else error.value = e.message
  } finally {
    loading.value = false
  }
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

    const data = await login(username.value, password.value)
    token = data.token
    startTimer(data.expires_in)
    username.value = ''
    password.value = ''
    code.value = ''
    mode.value = 'session'
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

// отзываем токен при закрытии или обновлении страницы
const onPageHide = () => revokeToken(true)

onMounted(() => window.addEventListener('pagehide', onPageHide))

onUnmounted(() => {
  window.removeEventListener('pagehide', onPageHide)
  stopTimer()
  revokeToken()
})
</script>

<template>
  <h1>Задание 2: код после авторизации</h1>

  <template v-if="mode === 'session'">
    <CodeDisplay :code="code" :loading="loading" />
    <p v-if="error" class="error">{{ error }}</p>

    <p class="hint">
      Сессия закончится через {{ timeLeft }}. Обновление страницы тоже завершит её.
    </p>

    <div class="actions">
      <button :disabled="loading" @click="generate">Сгенерировать код</button>
      <button class="link" @click="endSession()">Выйти</button>
    </div>
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