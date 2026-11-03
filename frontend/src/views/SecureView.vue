<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { getSecureCode, login, logout, register } from '../api'
import CodeDisplay from '../components/CodeDisplay.vue'

const mode = ref('login')
const username = ref('')
const password = ref('')
const passwordConfirm = ref('')
const showPassword = ref(false)
const code = ref('')
const error = ref('')
const info = ref('')
const loading = ref(false)
const secondsLeft = ref(0)

const registerProblem = computed(() => {
  if (mode.value !== 'register') return ''

  if (username.value.trim().length < 3) {
    return 'Имя пользователя должно содержать не менее 3 символов.'
  }

  if (username.value.trim().length > 64) {
    return 'Имя пользователя не должно превышать 64 символа.'
  }

  if (password.value.length < 6) {
    return 'Пароль должен содержать не менее 6 символов.'
  }

  if (password.value.length > 128) {
    return 'Пароль не должен превышать 128 символов.'
  }

  if (password.value !== passwordConfirm.value) {
    return 'Пароли не совпадают.'
  }

  return ''
})

// токен хранится только в памяти страницы
let token = null
// оставшееся время действия сессии
let timerId = null
// таймаут для скрытия ошибки через 5 секунд
let errorTimeout = null

const timeLeft = computed(() => {
  const minutes = Math.floor(secondsLeft.value / 60)
  const seconds = String(secondsLeft.value % 60).padStart(2, '0')
  return `${minutes}:${seconds}`
})

// показываем ошибку на 5 секунд
function showError(message) {
  clearTimeout(errorTimeout)
  error.value = message

  errorTimeout = setTimeout(() => {
    error.value = ''
    errorTimeout = null
  }, 5000)
}

// очищаем ошибку и таймер
function clearError() {
  clearTimeout(errorTimeout)
  errorTimeout = null
  error.value = ''
}

// запускаем таймер сессии
function startTimer(seconds) {
  const expiresAt = Date.now() + seconds * 1000
  secondsLeft.value = seconds
  timerId = setInterval(() => {
    secondsLeft.value = Math.max(0, Math.ceil((expiresAt - Date.now()) / 1000))

    if (secondsLeft.value === 0) {
      endSession('Сессия истекла. Войдите снова.')
    }
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
  clearError()
  info.value = message
  mode.value = 'login'
}

function switchMode(next) {
  mode.value = next
  clearError()
  info.value = ''
  password.value = ''
  passwordConfirm.value = ''
  showPassword.value = false
}

// генерируем код
async function generate() {
  clearError()
  loading.value = true
  try {
    code.value = (await getSecureCode(token)).code
  } catch (e) {
    if (e.status === 401) {
      endSession('Сессия истекла. Войдите снова.')
    } else {
      showError(e.message)
    }
  } finally {
    loading.value = false
  }
}

// обрабатываем вход и регистрацию
async function submit() {
  clearError()
  info.value = ''

  if (registerProblem.value) {
    showError(registerProblem.value)
    return
  }

  loading.value = true
  try {
    if (mode.value === 'register') {
      await register(username.value, password.value)
      switchMode('login')
      info.value = 'Регистрация прошла успешно. Теперь войдите.'
      return
    }

    const data = await login(username.value, password.value)
    token = data.token
    startTimer(data.expires_in)
    username.value = ''
    password.value = ''
    showPassword.value = false
    code.value = ''
    mode.value = 'session'
  } catch (e) {
    showError(e.message)
  } finally {
    loading.value = false
  }
}

// отзываем токен при закрытии или обновлении страницы
const onPageHide = () => revokeToken(true)

onMounted(() => {
  window.addEventListener('pagehide', onPageHide)
})

onUnmounted(() => {
  window.removeEventListener('pagehide', onPageHide)
  stopTimer()
  clearTimeout(errorTimeout)
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

  <form v-else class="form" novalidate @submit.prevent="submit">
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
      :type="showPassword ? 'text' : 'password'"
      placeholder="Пароль"
      :autocomplete="mode === 'login' ? 'current-password' : 'new-password'"
      required
    />
    <input
      v-if="mode === 'register'"
      v-model="passwordConfirm"
      :type="showPassword ? 'text' : 'password'"
      placeholder="Повторите пароль"
      autocomplete="new-password"
      required
    />

    <label class="check">
      <input v-model="showPassword" type="checkbox" />
      Показать пароль
    </label>

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
    <button
      v-else
      type="button"
      class="link"
      @click="switchMode('login')"
    >
      Уже есть аккаунт? Войти
    </button>
  </form>
</template>