const API_URL = 'http://127.0.0.1:8000/api'

export class ApiError extends Error {
  constructor(status, message) {
    super(message)
    this.status = status
  }
}

function errorMessage(status, data) {
  if (status === 422) return 'Проверьте данные: логин от 3 символов, пароль от 6'
  if (typeof data?.detail === 'string') return data.detail
  return 'Что-то пошло не так'
}

async function request(path, { method = 'GET', body, token } = {}) {
  const headers = {}
  if (body) headers['Content-Type'] = 'application/json'
  if (token) headers['Authorization'] = `Bearer ${token}`

  let response
  try {
    response = await fetch(`${API_URL}${path}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
      cache: 'no-store',
    })
  } catch {
    throw new ApiError(0, 'Сервер недоступен')
  }

  const data = await response.json().catch(() => null)
  if (!response.ok) {
    throw new ApiError(response.status, errorMessage(response.status, data))
  }
  return data
}

export const getPublicCode = () => request('/')

export const register = (username, password) =>
  request('/register', { method: 'POST', body: { username, password } })

export const login = (username, password) =>
  request('/login', { method: 'POST', body: { username, password } })

export const getSecureCode = (token) => request('/secure', { token })
