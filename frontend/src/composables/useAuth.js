import { ref, computed } from 'vue'

const user = ref(null)
const isAuthenticated = computed(() => user.value !== null)

export function useAuth() {
  const login = (userData) => {
    user.value = {
      id: Math.random().toString(36).substring(7),
      firstName: userData.firstName,
      lastName: userData.lastName,
      email: userData.email,
      circleName: userData.circleName,
      role: userData.role || 'member',
      loginTime: new Date()
    }
    localStorage.setItem('user', JSON.stringify(user.value))
  }

  const register = (userData) => {
    user.value = {
      id: Math.random().toString(36).substring(7),
      firstName: userData.firstName,
      lastName: userData.lastName,
      email: userData.email,
      circleName: userData.circleName,
      role: userData.role || 'member',
      registeredAt: new Date(),
      loginTime: new Date()
    }
    localStorage.setItem('user', JSON.stringify(user.value))
  }

  const logout = () => {
    user.value = null
    localStorage.removeItem('user')
  }

  const restoreSession = () => {
    const stored = localStorage.getItem('user')
    if (stored) {
      user.value = JSON.parse(stored)
    }
  }

  return {
    user: computed(() => user.value),
    isAuthenticated,
    login,
    register,
    logout,
    restoreSession
  }
}
