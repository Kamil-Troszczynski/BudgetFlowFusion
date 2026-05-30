<template>
  <div v-if="isOpen" class="modal-overlay" @click="closeModal">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2 class="modal-title">Dodaj pozycję do listy</h2>
        <button class="modal-close" @click="closeModal">✕</button>
      </div>

      <form class="item-form" @submit.prevent="handleSubmit">
        <div class="item-form-group">
          <label class="item-form-label">Wybierz przedmiot z Katalogu</label>
          <select
            v-model="form.itemId"
            class="item-form-select"
            required
          >
            <option value="" disabled>Wybierz z listy zatwierdzonych...</option>
            <option v-for="item in catalogItems" :key="item.id" :value="item.id">
              {{ item.name }} ({{ item.price }} {{ item.currency }})
            </option>
          </select>
          <p class="helper-text">Nie widzisz przedmiotu? Dodaj go najpierw do katalogu w zakładce Pulpit.</p>
        </div>

        <div class="item-form-group">
          <label class="item-form-label">Ilość sztuk</label>
          <input
            v-model.number="form.amount"
            type="number"
            min="1"
            placeholder="1"
            class="item-form-input"
            required
          />
        </div>

        <div class="item-form-info">
          <span class="info-icon">ℹ️</span>
          <p>Suma dla tej pozycji: <strong>{{ calculatedTotal }}</strong></p>
        </div>

        <div class="modal-actions">
          <button type="button" class="modal-btn modal-btn-cancel" @click="closeModal">Anuluj</button>
          <button type="submit" class="modal-btn modal-btn-save">Dodaj do listy</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const props = defineProps({
  isOpen: {
    type: Boolean,
    required: true
  }
})

const emit = defineEmits(['close', 'add-to-list'])

const catalogItems = ref([])

const fetchItems = async () => {
  try {
    const response = await fetch('http://localhost:8080/api/items')
    if (!response.ok) throw new Error('Błąd sieci')

    const data = await response.json()

    catalogItems.value = data.map(item => ({
      ...item,
      id: item.item_id
    }))

  } catch (error) {
    console.error("Nie udało się pobrać katalogu przedmiotów:", error)
  }
}

onMounted(() => {
  fetchItems()
})

const form = ref({
  itemId: '',
  amount: 1
})

const calculatedTotal = computed(() => {
  if (!form.value.itemId) return '0.00 PLN'
  const selected = catalogItems.value.find(i => i.id === form.value.itemId)
  return `${(selected.price * form.value.amount).toFixed(2)} ${selected.currency}`
})

const closeModal = () => {
  emit('close')
  setTimeout(() => {
    form.value = { itemId: '', amount: 1 }
  }, 200)
}

const handleSubmit = () => {
  const selectedItem = catalogItems.value.find(i => i.id === form.value.itemId)
  emit('add-to-list', {
    ...selectedItem,
    amount: form.value.amount,
    totalPrice: selectedItem.price * form.value.amount
  })
  closeModal()
}
</script>

<style scoped>
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background-color: rgba(0, 0, 0, 0.75); display: flex; align-items: center; justify-content: center; z-index: 1000; backdrop-filter: blur(4px); }
.modal-content { background: #0f172a; border: 0.1vw solid rgba(59, 130, 246, 0.2); border-radius: 1.2vw; padding: 2.5vw; width: 90%; max-width: 35vw; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6); }
.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2vw; padding-bottom: 1.5vw; border-bottom: 0.1vw solid rgba(59, 130, 246, 0.2); }
.modal-title { font-size: 1.5vw; font-weight: 700; color: #bfdbfe; margin: 0; }
.modal-close { background: none; border: none; color: rgba(226, 232, 240, 0.6); font-size: 1.5vw; cursor: pointer; transition: color 0.2s; }
.modal-close:hover { color: #ffffff; }
.item-form-group { margin-bottom: 1.5vw; }
.item-form-label { display: block; margin-bottom: 0.6vw; color: rgba(226, 232, 240, 0.9); font-size: 0.95vw; font-weight: 600; }
.item-form-input, .item-form-select { width: 100%; padding: 0.9vw; background: rgba(30, 41, 59, 0.6); border: 0.08vw solid rgba(148, 163, 184, 0.2); border-radius: 0.6vw; color: #ffffff; font-size: 0.95vw; transition: all 0.2s; }
.item-form-input:focus, .item-form-select:focus { outline: none; border-color: #3b82f6; background: rgba(30, 41, 59, 0.9); }
.helper-text { margin: 0.5vw 0 0 0; font-size: 0.8vw; color: #94a3b8; }
.item-form-info { display: flex; align-items: center; gap: 0.8vw; padding: 1vw; background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.2); border-radius: 0.6vw; margin-top: 2vw; }
.item-form-info p { margin: 0; font-size: 1vw; color: #bfdbfe; }
.modal-actions { display: flex; gap: 1vw; justify-content: flex-end; margin-top: 2vw; padding-top: 1.5vw; border-top: 0.1vw solid rgba(59, 130, 246, 0.2); }
.modal-btn { padding: 0.8vw 1.6vw; border-radius: 0.6vw; font-size: 0.95vw; font-weight: 600; cursor: pointer; border: 1px solid transparent; transition: all 0.2s; }
.modal-btn-cancel { background: rgba(148, 163, 184, 0.1); color: #e2e8f0; }
.modal-btn-cancel:hover { background: rgba(148, 163, 184, 0.2); }
.modal-btn-save { background: linear-gradient(135deg, #3b82f6, #2563eb); color: #ffffff; }
.modal-btn-save:hover { box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3); transform: translateY(-2px); }
</style>