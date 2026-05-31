<template>
  <div v-if="isOpen" class="modal-overlay" @click="closeModal">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2 class="modal-title">Dodaj nowy przedmiot</h2>
        <button class="modal-close" @click="closeModal">✕</button>
      </div>

      <form class="item-form" @submit.prevent="handleSubmit">
        <div class="item-form-group">
          <label class="item-form-label">Nazwa przedmiotu</label>
          <input
            v-model="form.name"
            type="text"
            placeholder="np. Pakiet ogniw Li-ion 4S"
            class="item-form-input"
            required
          />
        </div>

        <div class="item-form-group">
          <label class="item-form-label">Link do przedmiotu (URL)</label>
          <input
            v-model="form.link"
            type="url"
            placeholder="https://sklep..."
            class="item-form-input"
            required
          />
        </div>

        <div class="item-form-row">
          <div class="item-form-group half">
            <label class="item-form-label">Cena</label>
            <input
              v-model.number="form.price"
              type="number"
              step="0.01"
              min="0.01"
              placeholder="0.00"
              class="item-form-input"
              required
            />
          </div>
          <div class="item-form-group half">
            <label class="item-form-label">Waluta</label>
            <select v-model="form.currency" class="item-form-select" required>
              <option value="PLN">PLN</option>
              <option value="EUR">EUR</option>
              <option value="USD">USD</option>
            </select>
          </div>
        </div>

        <div class="item-form-group">
          <label class="item-form-label">Kategoria główna (CPV)</label>
          <select
            v-model="form.categoryId"
            class="item-form-select"
            @change="handleCategoryChange"
            required
          >
            <option value="" disabled>Wybierz kategorię</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">
              {{ cat.name }} (CPV: {{ cat.cpv }})
            </option>
          </select>
        </div>

        <div class="item-form-group">
          <label class="item-form-label">Podkategoria</label>
          <select
            v-model="form.subcategoryId"
            class="item-form-select"
            :disabled="!form.categoryId"
            required
          >
            <option value="" disabled>
              {{ form.categoryId ? 'Wybierz podkategorię' : 'Najpierw wybierz kategorię główną' }}
            </option>
            <option v-for="sub in availableSubcategories" :key="sub.id" :value="sub.id">
              {{ sub.name }}
            </option>
          </select>
        </div>

        <div class="item-form-info">
          <span class="info-icon">ℹ️</span>
          <p>Przedmiot zostanie przesłany do akceptacji przez skarbnika ze statusem <strong>Oczekujący (pending)</strong>.</p>
        </div>

        <div class="modal-actions">
          <button type="button" class="modal-btn modal-btn-cancel" @click="closeModal">Anuluj</button>
          <button
            type="submit"
            class="modal-btn modal-btn-save"
            :disabled="isLoading">{{ isLoading ? 'Zapisywanie...' : 'Dodaj do akceptacji' }}</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const props = defineProps({
  isOpen: { type: Boolean, required: true },
  isLoading: { type: Boolean, default: false }
})

const emit = defineEmits(['close', 'submit-item'])

const categories = ref([])
const allSubcategories = ref([])

const fetchClassifications = async () => {
  try {
    const catResponse = await fetch('http://localhost:8080/api/categories')
    if (catResponse.ok) {
      const catData = await catResponse.json()
      categories.value = catData.map(c => ({
        id: c.product_category_id || c.id,
        name: c.product_category_name || c.name,
        cpv: c.cpv || c.cpv_code
      }))
    }

    const subResponse = await fetch('http://localhost:8080/api/subcategories')
    if (subResponse.ok) {
      const subData = await subResponse.json()
      allSubcategories.value = subData.map(s => ({
        id: s.product_subcategory_id || s.id,
        name: s.product_subcategory_name || s.name,
        categoryId: s.product_category_id || s.category_id
      }))
    }
  } catch (error) {
    console.error("Błąd pobierania klasyfikacji:", error)
  }
}

onMounted(() => {
  fetchClassifications()
})

const form = ref({
  name: '',
  link: '',
  price: null,
  currency: 'PLN',
  categoryId: '',
  subcategoryId: ''
})

const availableSubcategories = computed(() => {
  if (!form.value.categoryId) return []
  return allSubcategories.value.filter(sub => sub.categoryId === form.value.categoryId)
})

const handleCategoryChange = () => {
  form.value.subcategoryId = ''
}

const closeModal = () => {
  emit('close')
  setTimeout(() => {
    form.value = { name: '', link: '', price: null, currency: 'PLN', categoryId: '', subcategoryId: '' }
  }, 200)
}

const handleSubmit = () => {
  const newItem = {
    ...form.value,
    status: 'pending',
    addedDate: new Date().toISOString()
  }

  emit('submit-item', newItem)
  closeModal()
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
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: #0f172a;
  border: 0.1vw solid rgba(59, 130, 246, 0.2);
  border-radius: 1.2vw;
  padding: 2.5vw;
  width: 90%;
  max-width: 40vw;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6);
}

.modal-content::-webkit-scrollbar { display: none; }

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2vw;
  padding-bottom: 1.5vw;
  border-bottom: 0.1vw solid rgba(59, 130, 246, 0.2);
}

.modal-title {
  font-size: 1.5vw;
  font-weight: 700;
  color: #bfdbfe;
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  color: rgba(226, 232, 240, 0.6);
  font-size: 1.5vw;
  cursor: pointer;
  transition: color 0.2s;
}
.modal-close:hover { color: #ffffff; }

.item-form-group {
  margin-bottom: 1.5vw;
}

.item-form-row {
  display: flex;
  gap: 1.5vw;
  margin-bottom: 1.5vw;
}
.item-form-row .half {
  flex: 1;
  margin-bottom: 0;
}

.item-form-label {
  display: block;
  margin-bottom: 0.6vw;
  color: rgba(226, 232, 240, 0.9);
  font-size: 0.95vw;
  font-weight: 600;
}

.item-form-input, .item-form-select {
  width: 100%;
  padding: 0.9vw;
  background: rgba(30, 41, 59, 0.6);
  border: 0.08vw solid rgba(148, 163, 184, 0.2);
  border-radius: 0.6vw;
  color: #ffffff;
  font-size: 0.95vw;
  transition: all 0.2s;
}

.item-form-input:focus, .item-form-select:focus {
  outline: none;
  border-color: #3b82f6;
  background: rgba(30, 41, 59, 0.9);
}

.item-form-select:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.item-form-info {
  display: flex;
  gap: 0.8vw;
  padding: 1vw;
  background: rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.2);
  border-radius: 0.6vw;
  margin-top: 2vw;
}

.item-form-info p {
  margin: 0;
  font-size: 0.85vw;
  color: rgba(253, 230, 138, 0.9);
  line-height: 1.4;
}

.modal-actions {
  display: flex;
  gap: 1vw;
  justify-content: flex-end;
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
  transition: all 0.2s;
  border: 1px solid transparent;
}

.modal-btn-cancel {
  background: rgba(148, 163, 184, 0.1);
  color: #e2e8f0;
}
.modal-btn-cancel:hover {
  background: rgba(148, 163, 184, 0.2);
}

.modal-btn-save {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: #ffffff;
}
.modal-btn-save:hover {
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
  transform: translateY(-2px);
}

.modal-btn-save:disabled {
  background: rgba(59, 130, 246, 0.5);
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
  opacity: 0.7;
}

@media (max-width: 1024px) {
  .modal-content { max-width: 60vw; }
}
@media (max-width: 640px) {
  .modal-content { max-width: 90vw; padding: 1.5vw; }
  .item-form-label, .item-form-input, .item-form-select, .modal-btn { font-size: 1.2vw; }
}
</style>