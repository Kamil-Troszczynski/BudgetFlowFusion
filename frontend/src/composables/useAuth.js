import { ref, computed } from 'vue'

const user = ref(null)
const isAuthenticated = computed(() => user.value !== null)

export function useAuth() {

  const login = async (userData) => {
    try {
      const response = await fetch('http://localhost:8080/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: userData.email,
          password: userData.password
        })
      })

      if (!response.ok) {
        throw new Error('Nieprawidłowy e-mail lub hasło')
      }

      const dbUser = await response.json()

      user.value = {
        id: dbUser.id,
        association_id: dbUser.association_id,
        firstName: dbUser.firstName,
        lastName: dbUser.lastName,
        email: dbUser.email,
        circleName: dbUser.circleName,
        position: dbUser.position,
        inSAP: dbUser.inSAP,
        role: dbUser.role,
        loginTime: new Date()
      }

      localStorage.setItem('user', JSON.stringify(user.value))
      return { success: true }

    } catch (error) {
      console.error("Błąd logowania:", error)
      return { success: false, message: error.message }
    }
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
    logout,
    restoreSession
  }
}