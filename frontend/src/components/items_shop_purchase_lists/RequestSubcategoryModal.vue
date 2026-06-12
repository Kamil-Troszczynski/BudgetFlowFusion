<template>
  <div v-if="isOpen" class="modal-overlay" @click="closeModal">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2 class="modal-title">Zgłoś nową podkategorię</h2>
        <button class="modal-close" @click="closeModal">✕</button>
      </div>

      <p class="modal-info">
        Skarbnik sprawdzi Twoje zgłoszenie i przypisze mu odpowiednią kategorię CPV.
        Po zatwierdzeniu podkategoria pojawi się na liście wyboru.
      </p>

      <form class="item-form" @submit.prevent="handleSubmit">
        <div class="item-form-group">
          <label class="item-form-label">Nazwa podkategorii *</label>
          <input
            v-model="form.name"
            type="text"
            placeholder="np. Drukarki 3D"
            class="item-form-input"
            required
          />
        </div>

        <div class="item-form-group">
          <label class="item-form-label">Opis (opcjonalnie)</label>
          <input
            v-model="form.description"
            type="text"
            placeholder="Krótki opis czego dotyczy podkategoria"
            class="item-form-input"
          />
        </div>

        <div class="modal-actions">
          <button type="button" class="modal-btn modal-btn-cancel" @click="closeModal">Anuluj</button>
          <button type="submit" class="modal-btn modal-btn-save" :disabled="isLoading">
            {{ isLoading ? 'Wysyłanie...' : 'Wyślij zgłoszenie' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useToast } from '@/composables/useToast'

const props = defineProps({
  isOpen: { type: Boolean, required: true }
})

const emit = defineEmits(['close'])

const toast = useToast()
const isLoading = ref(false)

const form = ref({ name: '', description: '' })

const closeModal = () => {
  form.value = { name: '', description: '' }
  emit('close')
}

const handleSubmit = async () => {
  isLoading.value = true
  try {
    const response = await fetch('http://localhost:8080/api/subcategories', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: form.value.name, product_category_id: null })
    })

    if (!response.ok) throw new Error('Błąd serwera')

    toast.success('Zgłoszenie wysłane! Skarbnik przypisze kategorię.')
    closeModal()
  } catch (error) {
    toast.error('Nie udało się wysłać zgłoszenia.')
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background-color: rgba(0, 0, 0, 0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1100;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: #0f172a;
  border: 0.1vw solid rgba(59, 130, 246, 0.2);
  border-radius: 1.2vw;
  padding: 2.5vw;
  width: 90%;
  max-width: 36vw;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.2vw;
  padding-bottom: 1vw;
  border-bottom: 0.1vw solid rgba(59, 130, 246, 0.2);
}

.modal-title {
  font-size: 1.5vw;
  font-weight: 700;
  color: #bfdbfe;
  margin: 0;
  font-family: 'Nunito', system-ui, sans-serif;
}

.modal-close {
  background: none;
  border: none;
  color: rgba(226, 232, 240, 0.6);
  font-size: 1.5vw;
  cursor: pointer;
}
.modal-close:hover { color: #ffffff; }

.modal-info {
  font-size: 0.9vw;
  color: rgba(253, 230, 138, 0.85);
  background: rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.2);
  border-radius: 0.6vw;
  padding: 0.9vw 1vw;
  margin-bottom: 1.8vw;
  line-height: 1.5;
  font-family: 'Nunito', system-ui, sans-serif;
}

.item-form-group { margin-bottom: 1.5vw; }

.item-form-label {
  display: block;
  margin-bottom: 0.6vw;
  color: rgba(226, 232, 240, 0.9);
  font-size: 0.95vw;
  font-weight: 600;
  font-family: 'Nunito', system-ui, sans-serif;
}

.item-form-input {
  width: 100%;
  padding: 0.9vw;
  background: rgba(30, 41, 59, 0.6);
  border: 0.08vw solid rgba(148, 163, 184, 0.2);
  border-radius: 0.6vw;
  color: #ffffff;
  font-size: 0.95vw;
  font-family: 'Nunito', system-ui, sans-serif;
  transition: all 0.2s;
  box-sizing: border-box;
}
.item-form-input:focus {
  outline: none;
  border-color: #3b82f6;
  background: rgba(30, 41, 59, 0.9);
}
.item-form-input::placeholder { color: rgba(226, 232, 240, 0.4); }

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1vw;
  margin-top: 2vw;
  padding-top: 1.5vw;
  border-top: 0.1vw solid rgba(59, 130, 246, 0.2);
}

.modal-btn {
  padding: 0.8vw 1.6vw;
  border-radius: 0.6vw;
  font-size: 0.95vw;
  font-weight: 600;
  cursor: pointer;
  border: none;
  font-family: 'Nunito', system-ui, sans-serif;
  transition: all 0.2s;
}

.modal-btn-cancel {
  background: rgba(148, 163, 184, 0.1);
  color: #e2e8f0;
}
.modal-btn-cancel:hover { background: rgba(148, 163, 184, 0.2); }

.modal-btn-save {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: #ffffff;
}
.modal-btn-save:hover { box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3); transform: translateY(-2px); }
.modal-btn-save:disabled { opacity: 0.6; cursor: not-allowed; transform: none; box-shadow: none; }
</style>
