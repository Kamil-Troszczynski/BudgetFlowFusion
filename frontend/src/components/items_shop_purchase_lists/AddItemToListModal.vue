<template>
  <div v-if="isOpen" class="modal-overlay" @click="closeModal">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2 class="modal-title">Dodaj pozycje do koszyka</h2>
        <button class="modal-close" type="button" @click="closeModal">x</button>
      </div>

      <form class="item-form" @submit.prevent="handleSubmit">
        <div class="item-form-group">
          <label class="item-form-label">Nazwa przedmiotu</label>
          <input
            v-model="form.name"
            type="text"
            placeholder="np. Czujnik temperatury"
            class="item-form-input"
            required
          />
        </div>

        <div class="item-form-group">
          <label class="item-form-label">Link do przedmiotu</label>
          <input
            v-model="form.link"
            type="url"
            placeholder="https://..."
            class="item-form-input"
          />
        </div>

        <div class="item-form-row item-form-row--prices">
          <div class="item-form-group">
            <label class="item-form-label">Kwota netto</label>
            <input
              v-model.number="form.net_price"
              type="number"
              step="0.01"
              min="0.01"
              placeholder="0.00"
              class="item-form-input"
              required
              @input="handleNetInput"
            />
          </div>
          <div class="item-form-group">
            <label class="item-form-label">Podatek VAT (%)</label>
            <input
              v-model.number="form.tax_rate"
              type="number"
              step="0.01"
              min="0"
              placeholder="23"
              class="item-form-input"
              required
              @input="handleTaxInput"
            />
          </div>
          <div class="item-form-group">
            <label class="item-form-label">Cena brutto</label>
            <input
              v-model.number="form.price"
              type="number"
              step="0.01"
              min="0.01"
              placeholder="0.00"
              class="item-form-input"
              required
              @input="handleGrossInput"
            />
          </div>
        </div>

        <div class="item-form-row item-form-row--compact">
          <div class="item-form-group">
            <label class="item-form-label">Waluta</label>
            <select v-model="form.currency" class="item-form-select" required>
              <option value="PLN">PLN</option>
              <option value="EUR">EUR</option>
              <option value="USD">USD</option>
            </select>
          </div>
          <div class="item-form-group">
            <label class="item-form-label">Ilosc</label>
            <input
              v-model.number="form.amount"
              type="number"
              min="1"
              placeholder="1"
              class="item-form-input"
              required
            />
          </div>
        </div>

        <div class="item-form-group">
          <label class="item-form-label">Podkategoria produktu</label>
          <input
            v-model="subcategorySearch"
            type="text"
            placeholder="Szukaj podkategorii..."
            class="item-form-input item-form-search"
          />
          <select v-model.number="form.product_subcategory_id" class="item-form-select" required>
            <option value="" disabled>Wybierz podkategorie...</option>
            <option
              v-for="subcategory in filteredSubcategories"
              :key="subcategory.product_subcategory_id"
              :value="subcategory.product_subcategory_id"
            >
              {{ subcategoryLabel(subcategory) }}
            </option>
          </select>
        </div>

        <div class="item-form-group">
          <label class="item-form-label">Uwagi</label>
          <textarea
            v-model="form.notes"
            rows="2"
            placeholder="Opcjonalne szczegoly pozycji"
            class="item-form-input"
          ></textarea>
        </div>

        <div class="item-form-info" :class="{ 'error-bg': isOverBudget }">
          <div>
            <p>Suma dla tej pozycji: <strong>{{ calculatedItemTotal.toFixed(2) }} {{ form.currency }}</strong></p>
            <p :class="{ 'text-red': isOverBudget }">
              Stan koszyka po dodaniu: {{ projectedTotal.toFixed(2) }} / {{ maxBudget.toFixed(2) }} PLN
            </p>
            <p v-if="isOverBudget" class="text-red font-bold">
              Przekroczono dostepny budzet projektu.
            </p>
          </div>
        </div>

        <div class="modal-actions">
          <button type="button" class="modal-btn modal-btn-cancel" @click="closeModal">Anuluj</button>
          <button type="submit" class="modal-btn modal-btn-save" :disabled="isOverBudget || isLoading">
            {{ isLoading ? 'Dodawanie...' : 'Dodaj do koszyka' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useAuth } from '@/composables/useAuth'

const props = defineProps({
  isOpen: { type: Boolean, required: true },
  currentTotal: { type: Number, required: true },
  maxBudget: { type: Number, required: true }
})

const emit = defineEmits(['close', 'add-to-list'])
const { user } = useAuth()

const subcategories = ref([])
const subcategorySearch = ref('')
const isLoading = ref(false)
const currentStudentId = computed(() => user.value?.id)

const emptyForm = () => ({
  name: '',
  link: '',
  net_price: null,
  tax_rate: 23,
  price: null,
  currency: 'PLN',
  amount: 1,
  product_subcategory_id: '',
  notes: ''
})

const form = ref(emptyForm())
const lastEditedPriceField = ref('net')

const fetchSubcategories = async () => {
  try {
    const response = await fetch('http://localhost:8080/api/subcategories', { cache: 'no-store' })
    if (!response.ok) throw new Error('Blad sieci')
    const data = await response.json()
    subcategories.value = (data || []).map(subcategory => ({
      ...subcategory,
      category_name: subcategory.product_category?.product_category_name || subcategory.category_name || ''
    }))
  } catch (error) {
    console.error('Nie udalo sie pobrac podkategorii:', error)
  }
}

onMounted(fetchSubcategories)

watch(() => props.isOpen, isOpen => {
  if (isOpen) fetchSubcategories()
  else {
    form.value = emptyForm()
    subcategorySearch.value = ''
    isLoading.value = false
  }
})

const filteredSubcategories = computed(() => {
  const query = subcategorySearch.value.toLowerCase().trim()
  if (!query) return subcategories.value
  return subcategories.value.filter(subcategory =>
    `${subcategory.product_subcategory_name || ''} ${subcategory.category_name || ''}`
      .toLowerCase()
      .includes(query)
  )
})

const subcategoryLabel = subcategory =>
  [subcategory.product_subcategory_name, subcategory.category_name]
    .filter(Boolean)
    .join(' - ')

const roundMoney = value => {
  const number = Number(value)
  if (!Number.isFinite(number)) return null
  return Math.round(number * 100) / 100
}

const taxMultiplier = () => 1 + Number(form.value.tax_rate || 0) / 100

const updateGrossFromNetTax = () => {
  const net = Number(form.value.net_price)
  if (!Number.isFinite(net) || net <= 0) {
    form.value.price = null
    return
  }
  form.value.price = roundMoney(net * taxMultiplier())
}

const updateNetFromGrossTax = () => {
  const gross = Number(form.value.price)
  const multiplier = taxMultiplier()
  if (!Number.isFinite(gross) || gross <= 0 || multiplier <= 0) {
    form.value.net_price = null
    return
  }
  form.value.net_price = roundMoney(gross / multiplier)
}

const handleNetInput = () => {
  lastEditedPriceField.value = 'net'
  updateGrossFromNetTax()
}

const handleGrossInput = () => {
  lastEditedPriceField.value = 'gross'
  updateNetFromGrossTax()
}

const handleTaxInput = () => {
  if (lastEditedPriceField.value === 'gross') updateNetFromGrossTax()
  else updateGrossFromNetTax()
}

const calculatedItemTotal = computed(() =>
  Number(form.value.price || 0) * Number(form.value.amount || 0)
)

const projectedTotal = computed(() =>
  props.currentTotal + calculatedItemTotal.value
)

const isOverBudget = computed(() =>
  Number(props.maxBudget || 0) > 0 && projectedTotal.value > props.maxBudget
)

const closeModal = () => {
  emit('close')
  setTimeout(() => {
    form.value = emptyForm()
    subcategorySearch.value = ''
    isLoading.value = false
  }, 200)
}

const handleSubmit = () => {
  if (isOverBudget.value || isLoading.value) return
  isLoading.value = true
  emit('add-to-list', {
    ...form.value,
    amount: Number(form.value.amount),
    price: Number(form.value.price),
    tax_rate: Number(form.value.tax_rate || 0),
    student_id: currentStudentId.value
  })
}
</script>

<style scoped>
.modal-overlay { position: fixed; inset: 0; background-color: rgba(0, 0, 0, 0.75); display: flex; align-items: center; justify-content: center; z-index: 1000; backdrop-filter: blur(4px); }
.modal-content { background: #0f172a; border: 1px solid rgba(59, 130, 246, 0.2); border-radius: 14px; padding: 28px; width: min(92vw, 680px); max-height: 90vh; overflow-y: auto; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6); }
.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding-bottom: 16px; border-bottom: 1px solid rgba(59, 130, 246, 0.2); }
.modal-title { font-size: 22px; font-weight: 700; color: var(--color-heading); margin: 0; }
.modal-close { background: none; border: none; color: rgba(var(--rgb-muted), 0.6); font-size: 22px; cursor: pointer; }
.modal-close:hover { color: rgb(var(--rgb-text)); }
.item-form-row { display: grid; grid-template-columns: 1fr 0.7fr 0.7fr; gap: 14px; }
.item-form-row--prices { grid-template-columns: 1fr 0.75fr 1fr; }
.item-form-row--compact { grid-template-columns: 0.7fr 0.7fr; max-width: 360px; }
.item-form-group { margin-bottom: 16px; }
.item-form-label { display: block; margin-bottom: 7px; color: rgba(var(--rgb-muted), 0.9); font-size: 14px; font-weight: 700; }
.item-form-input, .item-form-select { width: 100%; padding: 11px 12px; background: rgba(var(--rgb-raised), 0.6); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 8px; color: rgb(var(--rgb-text)); font-size: 14px; transition: all 0.2s; box-sizing: border-box; }
.item-form-input:focus, .item-form-select:focus { outline: none; border-color: #3b82f6; background: rgba(var(--rgb-raised), 0.9); }
.item-form-input::placeholder { color: rgba(var(--rgb-muted), 0.4); }
.item-form-select option { background: #0f172a; }
.item-form-search { margin-bottom: 8px; }
.item-form-info { display: flex; gap: 12px; padding: 14px; background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.2); border-radius: 8px; margin-top: 18px; }
.item-form-info p { margin: 0; font-size: 14px; color: var(--color-heading); }
.item-form-info p + p { margin-top: 6px; }
.modal-actions { display: flex; gap: 12px; justify-content: flex-end; margin-top: 22px; padding-top: 18px; border-top: 1px solid rgba(59, 130, 246, 0.2); }
.modal-btn { padding: 10px 18px; border-radius: 8px; font-size: 14px; font-weight: 700; cursor: pointer; border: 1px solid transparent; transition: all 0.2s; }
.modal-btn-cancel { background: rgba(148, 163, 184, 0.1); color: rgb(var(--rgb-muted)); }
.modal-btn-cancel:hover { background: rgba(148, 163, 184, 0.2); }
.modal-btn-save { background: linear-gradient(135deg, #3b82f6, #2563eb); color: rgb(var(--rgb-text)); }
.modal-btn-save:hover { box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3); transform: translateY(-2px); }
.modal-btn-save:disabled { background: rgba(239, 68, 68, 0.5); color: rgba(255, 255, 255, 0.6); cursor: not-allowed; box-shadow: none; transform: none; }
.error-bg { background: rgba(239, 68, 68, 0.1) !important; border-color: rgba(239, 68, 68, 0.3) !important; }
.text-red { color: #fca5a5 !important; }
.font-bold { font-weight: 800; }
@media (max-width: 620px) {
  .item-form-row { grid-template-columns: 1fr; gap: 0; }
  .modal-actions { flex-direction: column; }
  .modal-btn { width: 100%; }
}
</style>
