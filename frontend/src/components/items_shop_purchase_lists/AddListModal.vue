<template>
  <div v-if="isOpen" class="modal-overlay" @click="closeModal">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2 class="modal-title">Utwórz nową listę zakupów</h2>
        <button class="modal-close" @click="closeModal">✕</button>
      </div>

      <form class="list-form" @submit.prevent="handleSubmit">
  
        <div class="list-form-group">
          <label class="list-form-label">Sklep docelowy</label>
          <select
            v-model="form.shopId"
            class="list-form-select"
            :class="{ 'list-form-select--error': duplicateListWarning }"
            required
            @change="handleShopChange"
          >
            <option value="" disabled>Wybierz sklep z bazy...</option>
            <option v-for="shop in shops" :key="shop.id" :value="shop.id">
              {{ shop.name }}
            </option>
          </select>
        </div>

        <div v-if="duplicateListWarning" class="duplicate-warning-banner">
          <span class="warning-banner-icon">⚠</span>
          <div class="warning-banner-content">
            <strong>Ten sklep posiada już aktywną listę!</strong><br />
            Istnieje już otwarta lista dla tego dostawcy. Znajdź ją na głównym ekranie i dopisz swoje pozycje, aby połączyć przesyłkę.
          </div>
        </div>

        <div v-if="selectedShopInfo && !duplicateListWarning" class="shop-meta-preview">
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
          <div v-if="selectedShopInfo?.opinion && !duplicateListWarning" class="shop-meta-preview">
            <div class="meta-preview-item">
              <span class="meta-preview-label">Opinia tekstowa:</span>
              <span class="meta-preview-value text-amber">{{ selectedShopInfo.opinion }}</span>
            </div>
          </div>
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
        <div class="modal-actions">
          <button type="button" class="modal-btn modal-btn-cancel" @click="closeModal">Anuluj</button>
          <button type="submit" class="modal-btn modal-btn-save" :disabled="duplicateListWarning">Utwórz listę</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
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
const existingLists = ref([])
const selectedShopInfo = ref(null)
const duplicateListWarning = ref(false)
const { user } = useAuth()

const isTreasurer = computed(() => user.value?.role === 'treasurer')

const form = ref({
  name: '',
  shopId: '',
  fundingId: '',
  priority: 2
})

const fetchExistingLists = async () => {
  try {
    const timestamp = new Date().getTime()
    const params = new URLSearchParams({
      open_only: 'true',
      t: String(timestamp)
    })
    if (props.publicPurchasePlan?.purchase_request_id) {
      params.set('purchase_request_id', props.publicPurchasePlan.purchase_request_id)
    } else if (props.publicPurchasePlan?.public_purchase_plan_id) {
      params.set('public_purchase_plan_id', props.publicPurchasePlan.public_purchase_plan_id)
    } else if (props.publicPurchasePlan?.gslbccf_id) {
      params.set('gslbccf_id', props.publicPurchasePlan.gslbccf_id)
    }
    const response = await fetch(`http://localhost:8080/api/lists?${params.toString()}`)
    if (response.ok) {
      existingLists.value = await response.json()
    }
  } catch (error) {
    console.error("Błąd pobierania aktywnych list:", error)
  }
}

const fetchShops = async () => {
  try {
    const response = await fetch('http://localhost:8080/api/shops')
    if (!response.ok) throw new Error('Błąd sieci')
    const data = await response.json()
    shops.value = data.map(shop => ({
      id: shop.shop_id,
      name: shop.shop_name,
      link: shop.link || '',
      opinion: shop.opinion || '',
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

  if (form.value.shopId) {
    const hasDuplicate = existingLists.value.some(
      list => Number(list.shop_id) === Number(form.value.shopId) && (list.settlement_id === null || list.settlement_id === undefined)
    )
    duplicateListWarning.value = hasDuplicate
  } else {
    duplicateListWarning.value = false
  }
}

onMounted(() => {
  fetchShops()
  fetchExistingLists()
  if (isTreasurer.value) {
    fetchFundings()
  }
})

watch(
  () => props.publicPurchasePlan,
  async () => {
    existingLists.value = []
    duplicateListWarning.value = false
    await fetchExistingLists()
    handleShopChange()
  }
)

watch(
  () => props.isOpen,
  async isOpen => {
    if (!isOpen) return
    await fetchExistingLists()
    handleShopChange()
  }
)

const closeModal = () => {
  emit('close')
  setTimeout(() => {
    form.value = { name: '', shopId: '', fundingId: '', priority: 2 }
    selectedShopInfo.value = null
    duplicateListWarning.value = false
  }, 200)
}

const handleSubmit = () => {
  if (duplicateListWarning.value) return

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
.modal-content { background: #0f172a; border: 0.1vw solid rgba(148, 163, 184, 0.15); border-radius: 1.2vw; padding: 2.5vw; width: 90%; max-width: 35vw; max-height: 94vh; overflow-y: auto; scrollbar-width: thin; scrollbar-color: rgba(96, 165, 250, 0.75) rgba(var(--rgb-surface), 0.8); box-sizing: border-box; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6); animation: modalPop 0.25s ease; }
.modal-content::-webkit-scrollbar { width: 0.55vw; }
.modal-content::-webkit-scrollbar-track { background: rgba(var(--rgb-surface), 0.75); border-radius: 999px; margin: 0.9vw 0; }
.modal-content::-webkit-scrollbar-thumb { background: linear-gradient(180deg, #60a5fa, #2563eb); border-radius: 999px; border: 0.12vw solid rgba(var(--rgb-surface), 0.95); }
.modal-content::-webkit-scrollbar-thumb:hover { background: linear-gradient(180deg, #93c5fd, #3b82f6); }
@keyframes modalPop { 0% { transform: scale(0.95); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }

.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2vw; padding-bottom: 1.5vw; border-bottom: 0.1vw solid rgba(148, 163, 184, 0.1); }
.modal-title { font-size: 1.5vw; font-weight: 800; color: var(--color-heading); margin: 0; }
.modal-close { background: none; border: none; color: rgba(var(--rgb-muted), 0.6); font-size: 1.5vw; cursor: pointer; transition: color 0.2s; }
.modal-close:hover { color: rgb(var(--rgb-text)); }

.list-form-group { margin-bottom: 1.5vw; }
.list-form-label { display: block; margin-bottom: 0.6vw; color: rgba(var(--rgb-muted), 0.85); font-size: 0.9vw; font-weight: 700; text-transform: uppercase; letter-spacing: 0.03em; }
.list-form-input, .list-form-select { width: 100%; box-sizing: border-box; padding: 0.9vw; background: rgba(var(--rgb-raised), 0.6); border: 0.08vw solid rgba(148, 163, 184, 0.2); border-radius: 0.6vw; color: rgb(var(--rgb-text)); font-size: 0.95vw; transition: all 0.2s; font-family: inherit; }
.list-form-input:focus, .list-form-select:focus { outline: none; border-color: #3b82f6; background: rgba(var(--rgb-raised), 0.9); box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2); }
.list-form-select--error { border-color: #ef4444 !important; background: rgba(239, 68, 68, 0.05) !important; }
.list-form-textarea { resize: none; font-family: inherit; }

.duplicate-warning-banner { display: flex; gap: 1vw; align-items: flex-start; padding: 1vw; background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 0.6vw; margin-bottom: 1.5vw; text-align: left; }
.warning-banner-icon { font-size: 1.4vw; color: #f59e0b; line-height: 1; }
.warning-banner-content { font-size: 0.85vw; color: var(--color-subtle); line-height: 1.4; }

.shop-meta-preview { display: flex; flex-direction: column; gap: 0.5vw; padding: 0.9vw 1.2vw; background: rgba(var(--rgb-surface), 0.4); border: 1px solid rgba(148, 163, 184, 0.1); border-radius: 0.6vw; margin-top: -1vw; margin-bottom: 1.5vw; }
.meta-preview-item { display: flex; align-items: center; justify-content: space-between; font-size: 0.85vw; }
.meta-preview-label { color: #64748b; font-weight: 600; }
.meta-preview-value { font-weight: 700; }

.modal-actions { display: flex; gap: 1vw; justify-content: flex-end; margin-top: 2vw; padding-top: 1.5vw; border-top: 0.1vw solid rgba(148, 163, 184, 0.1); }
.modal-btn { padding: 0.8vw 1.8vw; border-radius: 0.6vw; font-size: 0.95vw; font-weight: 700; cursor: pointer; border: 1px solid transparent; transition: all 0.2s; font-family: inherit; }
.modal-btn-cancel { background: rgba(148, 163, 184, 0.1); color: rgb(var(--rgb-muted)); }
.modal-btn-cancel:hover { background: rgba(148, 163, 184, 0.2); color: rgb(var(--rgb-text)); }
.modal-btn-save { background: linear-gradient(135deg, #3b82f6, #2563eb); color: rgb(var(--rgb-text)); box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3); }
.modal-btn-save:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4); }
.modal-btn-save:disabled { opacity: 0.3; cursor: not-allowed; }

.text-blue { color: #60a5fa; }
.text-emerald { color: #34d399; }
.text-amber { color: #fcd34d; }
</style>
