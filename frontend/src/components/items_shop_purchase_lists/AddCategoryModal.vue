<template>
  <div v-if="isOpen" class="modal-overlay" @click="closeModal">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2 class="modal-title">Zarządzanie Klasyfikacją (CPV)</h2>
        <button class="modal-close" @click="closeModal">✕</button>
      </div>

      <div class="type-selector">
        <button
          :class="['type-btn', { active: formType === 'category' }]"
          @click="formType = 'category'"
        >
          Nowa Kategoria Główna
        </button>
        <button
          :class="['type-btn', { active: formType === 'subcategory' }]"
          @click="formType = 'subcategory'"
        >
          Nowa Podkategoria
        </button>
      </div>

      <form class="item-form" @submit.prevent="handleSubmit">

        <template v-if="formType === 'category'">
          <div class="item-form-group">
            <label class="item-form-label">Nazwa kategorii (np. Narzędzia specjalistyczne)</label>
            <input v-model="catForm.name" type="text" class="item-form-input" required />
          </div>
          <div class="item-form-group">
            <label class="item-form-label">Kod CPV (np. 42000000-6)</label>
            <input v-model="catForm.cpv" type="text" class="item-form-input" required />
          </div>
        </template>

        <template v-if="formType === 'subcategory'">
          <div class="item-form-group">
            <label class="item-form-label">Wybierz Kategorię Główną</label>
            <select v-model="subcatForm.categoryId" class="item-form-select" required>
              <option value="" disabled>Wybierz kategorię...</option>
              <option v-for="cat in existingCategories" :key="cat.id" :value="cat.id">
                {{ cat.name }} (CPV: {{ cat.cpv }})
              </option>
            </select>
          </div>
          <div class="item-form-group">
            <label class="item-form-label">Nazwa Podkategorii (np. Drukarki 3D)</label>
            <input v-model="subcatForm.name" type="text" class="item-form-input" required />
          </div>
        </template>

        <div class="modal-actions">
          <button type="button" class="modal-btn modal-btn-cancel" @click="closeModal">Anuluj</button>
          <button type="submit" class="modal-btn modal-btn-save">Dodaj do bazy</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  isOpen: Boolean,
  existingCategories: Array
})

const emit = defineEmits(['close', 'refresh-categories'])

const formType = ref('category')

const catForm = ref({ name: '', cpv: '' })
const subcatForm = ref({ categoryId: '', name: '' })

const closeModal = () => {
  emit('close')
  catForm.value = { name: '', cpv: '' }
  subcatForm.value = { categoryId: '', name: '' }
}

const handleSubmit = async () => {
  try {
    let endpoint = ''
    let payload = {}

    if (formType.value === 'category') {
      endpoint = 'http://localhost:8080/api/categories'
      payload = { name: catForm.value.name, cpv: catForm.value.cpv }
    } else {
      endpoint = 'http://localhost:8080/api/subcategories'
      payload = {
        name: subcatForm.value.name,
        product_category_id: subcatForm.value.categoryId
      }
    }

    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })

    if (!response.ok) throw new Error('Błąd zapisu w bazie')

    alert('Zapisano pomyślnie!')
    emit('refresh-categories')
    closeModal()
  } catch (error) {
    console.error("Błąd zapisu:", error)
    alert("Nie udało się zapisać danych.")
  }
}
</script>

<style scoped>
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background-color: rgba(0, 0, 0, 0.75); display: flex; align-items: center; justify-content: center; z-index: 1000; backdrop-filter: blur(4px); }
.modal-content { background: #0f172a; border: 0.1vw solid rgba(59, 130, 246, 0.2); border-radius: 1.2vw; padding: 2.5vw; width: 90%; max-width: 35vw; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6); }
.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2vw; padding-bottom: 1vw; border-bottom: 0.1vw solid rgba(59, 130, 246, 0.2); }
.modal-title { font-size: 1.5vw; font-weight: 700; color: #bfdbfe; margin: 0; }
.modal-close { background: none; border: none; color: rgba(226, 232, 240, 0.6); font-size: 1.5vw; cursor: pointer; }
.modal-close:hover { color: #ffffff; }

.type-selector { display: flex; gap: 1vw; margin-bottom: 2vw; background: rgba(30, 41, 59, 0.4); padding: 0.5vw; border-radius: 0.8vw; }
.type-btn { flex: 1; padding: 0.8vw; background: transparent; border: none; color: #94a3b8; font-weight: 600; border-radius: 0.6vw; cursor: pointer; transition: all 0.2s; }
.type-btn.active { background: rgba(59, 130, 246, 0.2); color: #93c5fd; }

.item-form-group { margin-bottom: 1.5vw; }
.item-form-label { display: block; margin-bottom: 0.6vw; color: rgba(226, 232, 240, 0.9); font-size: 0.95vw; font-weight: 600; }
.item-form-input, .item-form-select { width: 100%; padding: 0.9vw; background: rgba(30, 41, 59, 0.6); border: 0.08vw solid rgba(148, 163, 184, 0.2); border-radius: 0.6vw; color: #ffffff; font-size: 0.95vw; }
.item-form-input:focus, .item-form-select:focus { outline: none; border-color: #3b82f6; }

.modal-actions { display: flex; justify-content: flex-end; gap: 1vw; margin-top: 2vw; padding-top: 1.5vw; border-top: 0.1vw solid rgba(59, 130, 246, 0.2); }
.modal-btn { padding: 0.8vw 1.6vw; border-radius: 0.6vw; font-size: 0.95vw; font-weight: 600; cursor: pointer; border: none; }
.modal-btn-cancel { background: rgba(148, 163, 184, 0.1); color: #e2e8f0; }
.modal-btn-save { background: linear-gradient(135deg, #3b82f6, #2563eb); color: #ffffff; }
</style>