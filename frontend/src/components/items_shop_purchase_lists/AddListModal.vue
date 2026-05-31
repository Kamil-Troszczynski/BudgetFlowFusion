<template>
  <div v-if="isOpen" class="modal-overlay" @click="closeModal">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2 class="modal-title">Utwórz nową listę zakupów</h2>
        <button class="modal-close" @click="closeModal">✕</button>
      </div>

      <form class="list-form" @submit.prevent="handleSubmit">
        <div class="list-form-group">
          <label class="list-form-label">Nazwa listy (opcjonalnie)</label>
          <input
            v-model="form.name"
            type="text"
            placeholder="np. Zamówienie elektroniki na maj"
            class="list-form-input"
          />
        </div>

        <div class="list-form-group">
          <label class="list-form-label">Sklep docelowy</label>
          <select
            v-model="form.shopId"
            class="list-form-select"
            required
          >
            <option value="" disabled>Wybierz sklep z bazy...</option>
            <option v-for="shop in shops" :key="shop.id" :value="shop.id">
              {{ shop.name }}
            </option>
          </select>
        </div>

        <div class="list-form-group">
          <label class="list-form-label">Projekt / Źródło finansowania</label>
          <select
            v-model="form.fundingId"
            class="list-form-select"
            required
          >
            <option value="" disabled>Wybierz budżet...</option>
            <option v-for="funding in fundings" :key="funding.id" :value="funding.id">
              {{ funding.name }} (Dostępne: {{ funding.available }} PLN)
            </option>
          </select>
        </div>

        <div class="list-form-group">
          <label class="list-form-label">Priorytet zamówienia</label>
          <select
            v-model.number="form.priority"
            class="list-form-select"
            required
          >
            <option value="1">Wysoki (Pilne)</option>
            <option value="2">Normalny</option>
            <option value="3">Niski (Może poczekać)</option>
          </select>
        </div>

        <div class="modal-actions">
          <button type="button" class="modal-btn modal-btn-cancel" @click="closeModal">Anuluj</button>
          <button type="submit" class="modal-btn modal-btn-save">Utwórz listę</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuth } from '@/composables/useAuth'

const props = defineProps({
  isOpen: {
    type: Boolean,
    required: true
  }
})

const emit = defineEmits(['close', 'submit-list'])

const shops = ref([])
const fundings = ref([])
const { user } = useAuth()

const form = ref({
  name: '',
  shopId: '',
  fundingId: '',
  priority: 2
})

const fetchShops = async () => {
  try {
    const response = await fetch('http://localhost:8080/api/shops')
    if (!response.ok) throw new Error('Błąd sieci')
    const data = await response.json()
    shops.value = data.map(shop => ({
      id: shop.shop_id,
      name: shop.shop_name
    }))
  } catch (error) {
    console.error("Błąd pobierania sklepów:", error)
  }
}

const fetchFundings = async () => {
  try {
    const response = await fetch(`http://localhost:8080/api/fundings?association_id=${user.value.association_id}`)
    if (!response.ok) throw new Error('Błąd sieci')
    const data = await response.json()
    fundings.value = data.map(funding => ({
      id: funding.funding_id,
      name: funding.funding_name,
      available: (funding.funding_price - funding.spent_money).toFixed(2)
    }))
  } catch (error) {
    console.error("Błąd pobierania budżetów:", error)
  }
}

onMounted(() => {
  fetchShops()
  fetchFundings()
})

const closeModal = () => {
  emit('close')
  setTimeout(() => {
    form.value = { name: '', shopId: '', fundingId: '', priority: 2 }
  }, 200)
}

const handleSubmit = () => {
  const selectedShop = shops.value.find(s => s.id === form.value.shopId)

  const finalName = form.value.name.trim() === ''
    ? `Zamówienie: ${selectedShop.name}`
    : form.value.name

  const newList = {
    ...form.value,
    name: finalName,
    shopName: selectedShop.name,
    itemCount: 0,
    itemTotal: 0,
    totalPrice: 0.00,
    participants: 1,
    createdDate: new Date()
  }

  emit('submit-list', newList)
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
.list-form-group { margin-bottom: 1.5vw; }
.list-form-label { display: block; margin-bottom: 0.6vw; color: rgba(226, 232, 240, 0.9); font-size: 0.95vw; font-weight: 600; }
.list-form-input, .list-form-select { width: 100%; padding: 0.9vw; background: rgba(30, 41, 59, 0.6); border: 0.08vw solid rgba(148, 163, 184, 0.2); border-radius: 0.6vw; color: #ffffff; font-size: 0.95vw; transition: all 0.2s; }
.list-form-input:focus, .list-form-select:focus { outline: none; border-color: #3b82f6; background: rgba(30, 41, 59, 0.9); }
.modal-actions { display: flex; gap: 1vw; justify-content: flex-end; margin-top: 2vw; padding-top: 1.5vw; border-top: 0.1vw solid rgba(59, 130, 246, 0.2); }
.modal-btn { padding: 0.8vw 1.6vw; border-radius: 0.6vw; font-size: 0.95vw; font-weight: 600; cursor: pointer; border: 1px solid transparent; transition: all 0.2s; }
.modal-btn-cancel { background: rgba(148, 163, 184, 0.1); color: #e2e8f0; }
.modal-btn-cancel:hover { background: rgba(148, 163, 184, 0.2); }
.modal-btn-save { background: linear-gradient(135deg, #3b82f6, #2563eb); color: #ffffff; }
.modal-btn-save:hover { box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3); transform: translateY(-2px); }
</style>