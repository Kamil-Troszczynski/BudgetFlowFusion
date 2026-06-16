<template>
  <div v-if="isOpen" class="modal-overlay" @click="closeModal">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2 class="modal-title">Utwórz nową listę zakupów</h2>
        <button class="modal-close" @click="closeModal">✕</button>
      </div>

      <form class="list-form" @submit.prevent="handleSubmit">
        <div v-if="publicPurchasePlan" class="shop-meta-preview">
          <div class="meta-preview-item">
            <span class="meta-preview-label">Zamowienie publiczne:</span>
            <span class="meta-preview-value text-blue">CPV {{ publicPurchasePlan.cpv_code }}</span>
          </div>
          <div class="meta-preview-item">
            <span class="meta-preview-label">Limit:</span>
            <span class="meta-preview-value text-emerald">{{ Number(publicPurchasePlan.cost || 0).toFixed(2) }} PLN</span>
          </div>
        </div>

        <div class="list-form-group">
          <label class="list-form-label">Sklep docelowy</label>
          <select
            v-model="form.shopId"
            class="list-form-select"
            required
            @change="handleShopChange"
          >
            <option value="" disabled>Wybierz sklep z bazy...</option>
            <option v-for="shop in shops" :key="shop.id" :value="shop.id">
              {{ shop.name }}
            </option>
          </select>
        </div>

        <div v-if="selectedShopInfo" class="shop-meta-preview">
          <div class="meta-preview-item">
            <span class="meta-preview-label">Czas dostawy:</span>
            <span class="meta-preview-value text-blue">{{ selectedShopInfo.deliveryTime || 'Brak danych' }}</span>
          </div>
          <div class="meta-preview-item">
            <span class="meta-preview-label">Darmowa wysyłka:</span>
            <span class="meta-preview-value text-emerald">
              {{ selectedShopInfo.freeDeliveryThreshold ? `od ${Number(selectedShopInfo.freeDeliveryThreshold).toFixed(2)} PLN` : 'Brak danych / Brak progu' }}
            </span>
          </div>
          <div class="meta-preview-item">
            <span class="meta-preview-label">Opinia:</span>
            <span class="meta-preview-value text-amber">
              {{ selectedShopInfo.rating ? `★ ${selectedShopInfo.rating}/5` : 'Brak opinii' }}
            </span>
          </div>
        </div>

        <div class="list-form-group">
          <label class="list-form-label">Nazwa listy / Cel zamówienia</label>
          <textarea
            v-model="form.name"
            placeholder="np. Materiały i elektronika do budowy nowego łazika na zawody..."
            rows="3"
            class="list-form-input list-form-textarea"
            required
          ></textarea>
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

        <div v-if="isTreasurer" class="list-form-group group-treasurer-only">
          <div class="treasurer-badge-indicator">Panel Skarbnika</div>
          <label class="list-form-label">Dofinansowanie (Opcjonalnie dla skarbnika)</label>
          <select
            v-model="form.fundingId"
            class="list-form-select"
          >
            <option value="">Przypisz dofinansowanie później...</option>
            <option v-for="funding in fundings" :key="funding.id" :value="funding.id">
              {{ funding.name }} - {{ funding.sectionName }} (dostępne: {{ funding.available }} PLN)
            </option>
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
import { ref, computed, onMounted } from 'vue'
import { useAuth } from '@/composables/useAuth'

const props = defineProps({
  isOpen: {
    type: Boolean,
    required: true
  },
  publicPurchasePlan: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'submit-list'])

const shops = ref([])
const fundings = ref([])
const selectedShopInfo = ref(null)
const { user } = useAuth()

const isTreasurer = computed(() => user.value?.role === 'treasurer')

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
      name: shop.shop_name,
      deliveryTime: shop.delivery_time ? String(shop.delivery_time) : '',
      freeDeliveryThreshold: shop.free_delivery_threshold || shop.freeDeliveryThreshold,
      rating: shop.rating
    }))
  } catch (error) {
    console.error("Błąd pobierania sklepów:", error)
  }
}

const fetchFundings = async () => {
  try {
    if (!user.value?.association_id) return
    const response = await fetch(`http://localhost:8080/api/fundings?association_id=${user.value.association_id}`)
    if (!response.ok) throw new Error('Błąd sieci')
    const data = await response.json()
    fundings.value = data.map(funding => ({
      id: funding.funding_id,
      name: funding.funding_name,
      sectionName: funding.project_budget_name || 'Brak sekcji',
      available: Number(funding.available_after_purchase_requests).toFixed(2)
    }))
  } catch (error) {
    console.error("Błąd pobierania budżetów:", error)
  }
}

const handleShopChange = () => {
  const found = shops.value.find(s => s.id === form.value.shopId)
  selectedShopInfo.value = found || null
}

onMounted(() => {
  fetchShops()
  if (isTreasurer.value) {
    fetchFundings()
  }
})

const closeModal = () => {
  emit('close')
  setTimeout(() => {
    form.value = { name: '', shopId: '', fundingId: '', priority: 2 }
    selectedShopInfo.value = null
  }, 200)
}

const handleSubmit = () => {
  const selectedShop = shops.value.find(s => s.id === form.value.shopId)

  const newList = {
    ...form.value,
    name: form.value.name.trim(),
    shopName: selectedShop.name,
    publicPurchasePlanId: props.publicPurchasePlan?.public_purchase_plan_id || null,
    fundingId: props.publicPurchasePlan?.funding_id || form.value.fundingId,
    itemCount: 0,
    itemTotal: 0,
    totalPrice: 0.00,
    participants: 1,
    createdDate: new Date()
  }

  emit('submit-list', newList)
}
</script>

<style scoped>
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background-color: rgba(5, 8, 22, 0.85); display: flex; align-items: center; justify-content: center; z-index: 1000; backdrop-filter: blur(4px); padding: 3vh 0; box-sizing: border-box; }
.modal-content { background: #0f172a; border: 0.1vw solid rgba(148, 163, 184, 0.15); border-radius: 1.2vw; padding: 2.5vw; width: 90%; max-width: 35vw; max-height: 94vh; overflow-y: auto; scrollbar-width: thin; scrollbar-color: rgba(96, 165, 250, 0.75) rgba(15, 23, 42, 0.8); box-sizing: border-box; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6); animation: modalPop 0.25s ease; }
.modal-content::-webkit-scrollbar { width: 0.55vw; }
.modal-content::-webkit-scrollbar-track { background: rgba(15, 23, 42, 0.75); border-radius: 999px; margin: 0.9vw 0; }
.modal-content::-webkit-scrollbar-thumb { background: linear-gradient(180deg, #60a5fa, #2563eb); border-radius: 999px; border: 0.12vw solid rgba(15, 23, 42, 0.95); }
.modal-content::-webkit-scrollbar-thumb:hover { background: linear-gradient(180deg, #93c5fd, #3b82f6); }
@keyframes modalPop { 0% { transform: scale(0.95); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }

.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2vw; padding-bottom: 1.5vw; border-bottom: 0.1vw solid rgba(148, 163, 184, 0.1); }
.modal-title { font-size: 1.5vw; font-weight: 800; color: #bfdbfe; margin: 0; }
.modal-close { background: none; border: none; color: rgba(226, 232, 240, 0.6); font-size: 1.5vw; cursor: pointer; transition: color 0.2s; }
.modal-close:hover { color: #ffffff; }

.list-form-group { margin-bottom: 1.5vw; }
.list-form-label { display: block; margin-bottom: 0.6vw; color: rgba(226, 232, 240, 0.85); font-size: 0.9vw; font-weight: 700; text-transform: uppercase; letter-spacing: 0.03em; }
.list-form-input, .list-form-select { width: 100%; box-sizing: border-box; padding: 0.9vw; background: rgba(30, 41, 59, 0.6); border: 0.08vw solid rgba(148, 163, 184, 0.2); border-radius: 0.6vw; color: #ffffff; font-size: 0.95vw; transition: all 0.2s; font-family: inherit; }
.list-form-input:focus, .list-form-select:focus { outline: none; border-color: #3b82f6; background: rgba(30, 41, 59, 0.9); box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2); }
.list-form-textarea { resize: none; font-family: inherit; }

.shop-meta-preview { display: flex; flex-direction: column; gap: 0.5vw; padding: 0.9vw 1.2vw; background: rgba(15, 23, 42, 0.4); border: 1px solid rgba(148, 163, 184, 0.1); border-radius: 0.6vw; margin-top: -1vw; margin-bottom: 1.5vw; }
.meta-preview-item { display: flex; align-items: center; justify-content: space-between; font-size: 0.85vw; }
.meta-preview-label { color: #64748b; font-weight: 600; }
.meta-preview-value { font-weight: 700; }

.group-treasurer-only { border: 1px solid rgba(245, 158, 11, 0.2); border-radius: 0.8vw; padding: 1.2vw; background: rgba(245, 158, 11, 0.02); position: relative; margin-top: 2vw; }
.treasurer-badge-indicator { position: absolute; top: -0.7vw; right: 1vw; background: #d97706; color: #ffffff; font-size: 0.7vw; font-weight: 800; padding: 0.15vw 0.5vw; border-radius: 0.3vw; text-transform: uppercase; letter-spacing: 0.05em; }

.modal-actions { display: flex; gap: 1vw; justify-content: flex-end; margin-top: 2vw; padding-top: 1.5vw; border-top: 0.1vw solid rgba(148, 163, 184, 0.1); }
.modal-btn { padding: 0.8vw 1.8vw; border-radius: 0.6vw; font-size: 0.95vw; font-weight: 700; cursor: pointer; border: 1px solid transparent; transition: all 0.2s; font-family: inherit; }
.modal-btn-cancel { background: rgba(148, 163, 184, 0.1); color: #e2e8f0; }
.modal-btn-cancel:hover { background: rgba(148, 163, 184, 0.2); color: #ffffff; }
.modal-btn-save { background: linear-gradient(135deg, #3b82f6, #2563eb); color: #ffffff; box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3); }
.modal-btn-save:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4); }

.text-blue { color: #60a5fa; }
.text-emerald { color: #34d399; }
.text-amber { color: #fcd34d; }
</style>
