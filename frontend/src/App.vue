<script setup>
import ToastNotification from '@/components/ToastNotification.vue'
import { useTheme } from '@/composables/useTheme'
useTheme()
</script>

<template>
  <RouterView />

  <ToastNotification />
</template>