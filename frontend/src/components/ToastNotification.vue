<template>
  <div class="toast-container">
    <TransitionGroup name="toast-anim">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        :class="['toast', `toast-${toast.type}`]"
      >
        <span class="toast-message">{{ toast.message }}</span>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup>
import { useToast } from '@/composables/useToast'
const { toasts } = useToast()
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;500;600;700;800&display=swap');

.toast-container {
  position: fixed;
  top: 2vw;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  gap: 0.8vw;
  z-index: 9999;
  pointer-events: none;
}

.toast {
  display: flex;
  align-items: center;
  gap: 0.8vw;
  padding: 1vw 1.5vw;
  border-radius: 0.8vw;
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(8px);
  color: white;
  font-size: 0.95vw;
  font-weight: 600;
  font-family: 'Nunito', system-ui, sans-serif;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
  border-left: 0.3vw solid;
  pointer-events: auto;
}

.toast-success { border-color: #22c55e; }
.toast-error { border-color: #ef4444; }
.toast-info { border-color: #3b82f6; }

.toast-anim-enter-active, .toast-anim-leave-active {
  transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
.toast-anim-enter-from { opacity: 0; transform: translateY(-100%); }
.toast-anim-leave-to { opacity: 0; transform: translateY(-100%); }
</style>