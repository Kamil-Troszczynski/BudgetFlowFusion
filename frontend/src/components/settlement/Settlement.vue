<template>
  <div class="requests-container">
    <template v-if="!activeSettlement">
      <div class="requests-section">
        <div class="requests-header">
          <div class="requests-title-section">
            <h2 class="requests-title">Moje rozliczenia</h2>
            <p class="requests-subtitle">Rozliczenia przypisane do Ciebie</p>
          </div>
          <button class="requests-add-button" @click="showAddSettlementModal = true">+ Dodaj rozliczenie</button>
        </div>

        <div v-if="userSettlements.length === 0" class="requests-empty">
          <p class="lists-empty-icon">🧾</p>
          <p class="requests-empty-text">Nie masz jeszcze żadnych rozliczeń</p>
          <p class="requests-empty-subtext">Dodaj pierwsze rozliczenie opłaconego wniosku</p>
        </div>

        <div v-else class="requests-grid">
          <div
            v-for="settlement in userSettlements"
            :key="settlement.id"
            class="request-card"
          >
            <div class="request-card__header">
              <h3 class="request-card__title">
                {{ settlement.purchaseRequest?.purchase_request_name ?? `Rozliczenie #${settlement.id}` }}
              </h3>
              <span class="request-card__badge" :class="getStatusClass(settlement)">
                {{ formatStatus(settlement) }}
              </span>
            </div>

            <div class="request-card__content">
              <p class="request-card__detail">
                <span class="request-card__label">Faktury:</span>
                <span class="request-card__value">{{ settlement.invoices.length }}</span>
              </p>
              <p class="request-card__detail">
                <span class="request-card__label">Listy zakupów:</span>
                <span class="request-card__value">{{ settlement.shopPurchaseLists.length }}</span>
              </p>
              <p class="request-card__detail">
                <span class="request-card__label">Data utworzenia:</span>
                <span class="request-card__value">{{ formatDate(settlement.created_at) }}</span>
              </p>
            </div>

            <div class="settlement-card__progress">
              <div class="settlement-card__progress-bar">
                <div
                  class="settlement-card__progress-fill"
                  :style="{ width: calcProgress(settlement) + '%' }"
                ></div>
              </div>
              <p class="settlement-card__progress-text">Rozliczono {{ calcProgress(settlement) }}%</p>
            </div>

            <div class="request-card__actions">
              <button class="request-card__button view" @click="activeSettlement = settlement">
                Szczegóły
              </button>
            </div>
          </div>
        </div>
      </div>
      <div class="requests-section">
        <div class="requests-header">
          <div class="requests-title-section">
            <h2 class="requests-title">Wszystkie rozliczenia</h2>
            <p class="requests-subtitle">Rozliczenia wszystkich skarbników w organizacji</p>
          </div>
        </div>

        <div v-if="allSettlements.length === 0" class="requests-empty">
          <p class="lists-empty-icon">📦</p>
          <p class="requests-empty-text">Brak rozliczeń w organizacji</p>
          <p class="requests-empty-subtext">Rozliczenia pojawią się tutaj</p>
        </div>

        <div v-else class="requests-grid">
          <div
            v-for="settlement in allSettlements"
            :key="settlement.id"
            class="request-card"
          >
            <div class="request-card__header">
              <h3 class="request-card__title">
                {{ settlement.purchaseRequest?.purchase_request_name ?? `Rozliczenie #${settlement.id}` }}
              </h3>
              <span class="request-card__badge" :class="getStatusClass(settlement)">
                {{ formatStatus(settlement) }}
              </span>
            </div>

            <div class="request-card__content">
              <p class="request-card__detail">
                <span class="request-card__label">Budżet:</span>
                <span class="request-card__value">
                  {{ settlement.purchaseRequest?.budget_allocated_for_the_order ?? '—' }} PLN
                </span>
              </p>
              <p class="request-card__detail">
                <span class="request-card__label">Wydano:</span>
                <span class="request-card__value">
                  {{ settlement.totalSpent !== null ? settlement.totalSpent + ' PLN' : '—' }}
                </span>
              </p>
              <p class="request-card__detail">
                <span class="request-card__label">Faktury:</span>
                <span class="request-card__value">{{ settlement.invoices.length }}</span>
              </p>
              <p class="request-card__detail">
                <span class="request-card__label">Typ wniosku:</span>
                <span class="request-card__value">
                  {{ settlement.purchaseRequest?.if_service ? 'Usługa' : 'Produkt' }}
                </span>
              </p>
              <p class="request-card__detail">
                <span class="request-card__label">Data utworzenia:</span>
                <span class="request-card__value">{{ formatDate(settlement.created_at) }}</span>
              </p>
            </div>

            <div class="settlement-card__progress">
              <div class="settlement-card__progress-bar">
                <div
                  class="settlement-card__progress-fill"
                  :style="{ width: calcProgress(settlement) + '%' }"
                ></div>
              </div>
              <p class="settlement-card__progress-text">Rozliczono {{ calcProgress(settlement) }}%</p>
            </div>

            <div class="request-card__actions">
              <button class="request-card__button view" @click="activeSettlement = settlement">
                Szczegóły
              </button>
            </div>
          </div>
        </div>
      </div>

    </template>
    
    <div v-else class="requests-section">
      <button class="settlement-details__back" @click="activeSettlement = null">
        ← Powrót
      </button>

      <div class="settlement-details__card">
        <div class="settlement-details__top">
          <div>
            <h2 class="settlement-details__title">
              {{ activeSettlement.purchaseRequest?.purchase_request_name ?? `Rozliczenie #${activeSettlement.id}` }}
            </h2>
            <p class="settlement-details__subtitle">Rozliczenie opłaconego wniosku</p>
          </div>
          <span class="request-card__badge" :class="getStatusClass(activeSettlement)">
            {{ formatStatus(activeSettlement) }}
          </span>
        </div>

        <div class="settlement-details__grid">
          <div class="settlement-info">
            <p>Faktury</p>
            <strong>{{ activeSettlement.invoices.length }}</strong>
          </div>
          <div class="settlement-info">
            <p>Listy zakupów</p>
            <strong>{{ activeSettlement.shopPurchaseLists.length }}</strong>
          </div>
          <div class="settlement-info">
            <p>Data utworzenia</p>
            <strong>{{ formatDate(activeSettlement.created_at) }}</strong>
          </div>
          <div class="settlement-info">
            <p>Wydano</p>
            <strong>{{ activeSettlement.totalSpent !== null ? activeSettlement.totalSpent + ' PLN' : '—' }}</strong>
          </div>
        </div>

        <div class="settlement-details__invoices">
          <h3>Załączone faktury</h3>

          <div v-if="activeSettlement.invoices.length === 0">
            <p style="color: rgba(226,232,240,0.5)">Brak załączonych faktur</p>
          </div>

          <div
            v-for="invoice in activeSettlement.invoices"
            :key="invoice.invoice_id"
            class="invoice-card"
          >
            <div>
              <p class="invoice-title">{{ invoice.invoice_name ?? `Faktura #${invoice.invoice_id}` }}</p>
              <p class="invoice-date">{{ formatDate(invoice.created_at) }}</p>
            </div>
            <div class="invoice-price">{{ invoice.amount ?? '—' }} PLN</div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showAddSettlementModal" class="modal-overlay" @click="showAddSettlementModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2 class="modal-title">Nowe rozliczenie</h2>
          <button class="modal-close" @click="showAddSettlementModal = false">✕</button>
        </div>
        <form class="modal-form" @submit.prevent="handleNewSettlement">
          <div class="modal-form__group">
            <label class="modal-form__label">Powiązany wniosek (ID)</label>
            <input
              v-model="newSettlementData.purchase_request_id"
              type="number"
              placeholder="Wpisz ID wniosku (np. 1)"
              class="modal-form__input"
              required
            />
          </div>
          <div class="modal-actions">
            <button type="button" class="modal-btn modal-btn-cancel" @click="showAddSettlementModal = false">Anuluj</button>
            <button type="submit" class="modal-btn modal-btn-save">Utwórz rozliczenie</button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useAuth } from '@/composables/useAuth'

const API_URL = 'http://localhost:8080/api'

const { user } = useAuth()

const activeSettlement = ref(null)

const userSettlements = ref([])
const allSettlements = ref([])

const loading = ref(false)
const error = ref(null)

const showAddSettlementModal = ref(false)
const newSettlementData = ref({
  purchase_request_id: null
})

const mapSettlements = (data = []) =>
  data.map((req) => ({
    id: req.settlement_id,
    purchaseRequestId: req.purchase_request_id,
    paidByProjectFinanceManagerId:
      req.paid_by_project_finance_manager_id,

    created_at: req.created_at,

    invoices: req.invoices ?? [],
    shopPurchaseLists: req.shop_purchase_lists ?? [],

    purchaseRequest: req.purchase_request ?? null,

    totalSpent: Number(req.total_spent ?? 0),
  }))

const fetchAllSettlements = async () => {
  const response = await fetch(`${API_URL}/settlements`)

  if (!response.ok) {
    throw new Error('Nie udało się pobrać wszystkich rozliczeń')
  }

  const data = await response.json()
  allSettlements.value = mapSettlements(data)
}

const fetchUserSettlements = async () => {
  if (!user.value?.id) return

  const response = await fetch(
    `${API_URL}/settlements/manager/${user.value.id}`
  )

  if (!response.ok) {
    throw new Error('Nie udało się pobrać rozliczeń użytkownika')
  }

  const data = await response.json()
  userSettlements.value = mapSettlements(data)
}

const loadData = async () => {
  try {
    loading.value = true
    error.value = null

    await Promise.all([
      fetchAllSettlements(),
      fetchUserSettlements(),
    ])
  } catch (err) {
    console.error(err)
    error.value = err.message
  } finally {
    loading.value = false
  }
}


const handleNewSettlement = async () => {
  if (!user.value?.id) {
    alert("Błąd: Brak ID użytkownika.")
    return
  }

  try {
    const payload = {
      purchase_request_id: newSettlementData.value.purchase_request_id,
      paid_by_project_finance_manager_id: user.value.id,
      created_at: new Date().toISOString()
    }

    const response = await fetch(`${API_URL}/settlements`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })

    if (!response.ok) {
      const err = await response.json()
      alert(`Błąd przy tworzeniu rozliczenia: ${err.detail || 'Nieznany błąd'}`)
      return
    }

    newSettlementData.value.purchase_request_id = null
    showAddSettlementModal.value = false

    loadData()

  } catch (err) {
    console.error('Błąd zapisu rozliczenia:', err)
  }
}

const calcProgress = (settlement) => {
  const invoices = settlement?.invoices?.length ?? 0
  const lists = settlement?.shopPurchaseLists?.length ?? 0

  if (lists === 0) {
    return invoices > 0 ? 100 : 0
  }

  return Math.min(
    Math.round((invoices / lists) * 100),
    100
  )
}

const getStatusClass = (settlement) => {
  const progress = calcProgress(settlement)

  if (progress >= 100) return 'completed'
  if (progress > 0) return 'partial'

  return 'pending'
}

const formatStatus = (settlement) => {
  const progress = calcProgress(settlement)

  if (progress >= 100) return 'Rozliczony'
  if (progress > 0) return 'Częściowo'

  return 'Oczekuje'
}

const formatDate = (date) => {
  if (!date) return '—'

  return new Intl.DateTimeFormat('pl-PL').format(
    new Date(date)
  )
}

onMounted(() => {
  fetchAllSettlements()
})

watch(
  () => user.value?.id,
  (newId) => {
    if (newId) {
      fetchUserSettlements()
    }
  },
  { immediate: true }
)
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;500;600;700;800&display=swap');

.requests-container {
  display: flex;
  flex-direction: column;
  gap: 4vh;
}

.requests-section {
  width: 100%;
  padding: 3vh 0;
  font-family: 'Nunito', system-ui, sans-serif;
}

.requests-header {
  margin-bottom: 3vh;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 2vw;
}

.requests-title-section {
  display: flex;
  flex-direction: column;
  gap: 0.5vw;
}

.requests-title {
  font-size: 2vw;
  font-weight: 800;
  color: #bfdbfe;
  margin: 0;
}

.requests-subtitle {
  font-size: 1vw;
  color: rgba(226, 232, 240, 0.6);
  margin: 0;
}

.requests-add-button {
  padding: 0.8vw 1.5vw;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: #ffffff;
  border: none;
  border-radius: 0.8vw;
  font-size: 1vw;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: 'Nunito', system-ui, sans-serif;
  box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3);
}

.requests-add-button:hover {
  transform: translateY(-0.2vh);
  box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4);
}

.requests-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 6vh;
  background: rgba(15, 23, 42, 0.4);
  border: 0.08vw dashed rgba(148, 163, 184, 0.3);
  border-radius: 1vw;
  text-align: center;
}

.lists-empty-icon {
  font-size: 4vw;
  margin: 0 0 1.5vh 0;
}

.requests-empty-text {
  font-size: 1.2vw;
  font-weight: 600;
  color: rgba(226, 232, 240, 0.8);
  margin: 0 0 0.5vh 0;
}

.requests-empty-subtext {
  font-size: 0.95vw;
  color: rgba(226, 232, 240, 0.5);
  margin: 0;
}

.requests-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(26vw, 1fr));
  gap: 2vw;
}

.request-card {
  display: flex;
  flex-direction: column;
  padding: 2vw;
  background: rgba(15, 23, 42, 0.6);
  border: 0.08vw solid rgba(148, 163, 184, 0.15);
  border-radius: 1vw;
  transition: all 0.3s ease;
}

.request-card:hover {
  background: rgba(15, 23, 42, 0.8);
  border-color: rgba(59, 130, 246, 0.3);
  transform: translateY(-0.4vh);
}

.request-card__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5vw;
  gap: 1vw;
}

.request-card__title {
  font-size: 1.2vw;
  font-weight: 700;
  color: #ffffff;
  margin: 0;
  flex: 1;
}

.request-card__badge {
  padding: 0.4vw 0.8vw;
  border-radius: 0.4vw;
  font-size: 0.85vw;
  font-weight: 600;
  white-space: nowrap;
}

.request-card__badge.pending {
  background: rgba(59, 130, 246, 0.2);
  color: #93c5fd;
}

.request-card__badge.partial {
  background: rgba(251, 191, 36, 0.2);
  color: #fde68a;
}

.request-card__badge.completed {
  background: rgba(34, 197, 94, 0.2);
  color: #86efac;
}

.request-card__content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.8vw;
  margin-bottom: 1.5vw;
}

.request-card__detail {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.95vw;
  margin: 0;
}

.request-card__label {
  color: rgba(226, 232, 240, 0.6);
  font-weight: 600;
}

.request-card__value {
  color: #ffffff;
  font-weight: 500;
}

.settlement-card__progress-bar {
  width: 100%;
  height: 0.6vw;
  background: rgba(148, 163, 184, 0.2);
  border-radius: 999px;
  overflow: hidden;
  margin-bottom: 0.6vh;
}

.settlement-card__progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #60a5fa);
  transition: width 0.4s ease;
}

.settlement-card__progress-text {
  color: rgba(226, 232, 240, 0.6);
  font-size: 0.85vw;
  margin: 0 0 1.5vw 0;
}

.request-card__actions {
  display: flex;
  gap: 0.8vw;
}

.request-card__button {
  flex: 1;
  padding: 0.8vw;
  border: none;
  border-radius: 0.6vw;
  font-size: 0.9vw;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: 'Nunito', system-ui, sans-serif;
}

.request-card__button.view {
  background: rgba(59, 130, 246, 0.2);
  color: #93c5fd;
}

.request-card__button.view:hover {
  background: rgba(59, 130, 246, 0.35);
}

.request-card__button.upload {
  background: rgba(34, 197, 94, 0.2);
  color: #86efac;
}

.request-card__button.upload:hover {
  background: rgba(34, 197, 94, 0.35);
}

.settlement-details__back {
  margin-bottom: 2vh;
  background: none;
  border: none;
  color: #93c5fd;
  cursor: pointer;
  font-size: 1vw;
  font-family: 'Nunito', system-ui, sans-serif;
}

.settlement-details__card {
  background: rgba(15, 23, 42, 0.6);
  border: 0.08vw solid rgba(148, 163, 184, 0.15);
  border-radius: 1vw;
  padding: 2vw;
}

.settlement-details__top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2vw;
}

.settlement-details__title {
  color: white;
  margin: 0;
  font-size: 1.6vw;
  font-weight: 800;
}

.settlement-details__subtitle {
  color: rgba(226, 232, 240, 0.5);
  margin: 0.5vh 0 0 0;
}

.settlement-details__grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1vw;
  margin-bottom: 2vw;
}

.settlement-info {
  background: rgba(30, 41, 59, 0.6);
  padding: 1vw;
  border-radius: 0.8vw;
}

.settlement-info p {
  color: rgba(226, 232, 240, 0.5);
  margin: 0 0 0.5vh 0;
  font-size: 0.9vw;
}

.settlement-info strong {
  color: white;
  font-size: 1vw;
}

.settlement-details__invoices h3 {
  color: #bfdbfe;
  margin: 0 0 1.5vh 0;
  font-size: 1.2vw;
}

.invoice-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(30, 41, 59, 0.5);
  padding: 1vw;
  border-radius: 0.8vw;
  margin-top: 1vh;
}

.invoice-title {
  color: white;
  margin: 0 0 0.3vh 0;
  font-weight: 600;
}

.invoice-date {
  color: rgba(226, 232, 240, 0.5);
  font-size: 0.85vw;
  margin: 0;
}

.invoice-price {
  color: #86efac;
  font-weight: 700;
  font-size: 1vw;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  width: 100%;
  max-width: 35vw;
  background: #111827;
  border: 0.08vw solid rgba(148,163,184,0.15);
  border-radius: 1vw;
  padding: 2vw;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2vh;
}

.modal-title {
  font-size: 1.5vw;
  color: #fff;
  font-weight: 700;
}

.modal-close {
  background: transparent;
  border: none;
  color: #fff;
  font-size: 1.2vw;
  cursor: pointer;
}

.modal-form {
  display: flex;
  flex-direction: column;
  gap: 1.2vw;
}

.modal-form__group {
  display: flex;
  flex-direction: column;
  gap: 0.5vw;
}

.modal-form__label {
  color: #cbd5e1;
  font-size: 0.9vw;
  font-weight: 600;
}

.modal-form__input {
  padding: 0.9vw 1vw;
  border-radius: 0.7vw;
  border: 0.08vw solid rgba(148,163,184,0.2);
  background: rgba(15,23,42,0.7);
  color: white;
  font-size: 0.95vw;
}

.modal-form__input:focus {
  outline: none;
  border-color: rgba(59,130,246,0.7);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1vw;
  margin-top: 1vw;
}

.modal-btn {
  padding: 0.8vw 1.4vw;
  border-radius: 0.7vw;
  border: none;
  cursor: pointer;
  font-weight: 700;
  font-family: 'Nunito', system-ui, sans-serif;
  font-size: 0.95vw;
}

.modal-btn-cancel {
  background: rgba(148,163,184,0.15);
  color: #e2e8f0;
}

.modal-btn-save {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
}
</style>