import { ref, watchEffect } from 'vue'

const STORAGE_KEY = 'bff-theme'
const theme = ref(localStorage.getItem(STORAGE_KEY) ?? 'dark')

watchEffect(() => {
  document.documentElement.setAttribute('data-theme', theme.value)
  localStorage.setItem(STORAGE_KEY, theme.value)
})

export function useTheme() {
  function toggle() {
    theme.value = theme.value === 'dark' ? 'light' : 'dark'
  }

  return { theme, toggle }
}
