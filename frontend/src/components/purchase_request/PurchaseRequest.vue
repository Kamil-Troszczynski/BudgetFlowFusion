<template>
  <div class="requests-container">
    <template v-if="!activeRequest">
      <div class="requests-section">
        <div class="requests-header">
          <div class="requests-title-section">
            <h2 class="requests-title">Moje wnioski o zamówienie</h2>
            <p class="requests-subtitle">Wnioski zakupowe, które utworzyłeś</p>
          </div>
          <button class="requests-add-button" @click="openAddRequestModal">+ Nowy wniosek</button>
        </div>

        <div v-if="userRequests.length === 0" class="requests-empty">
          <p class="lists-empty-icon">📄</p>
          <p class="requests-empty-text">Nie utworzyłeś jeszcze żadnego wniosku</p>
          <p class="requests-empty-subtext">
            Stwórz nowy wniosek klikając przycisk powyżej
          </p>
        </div>

        <div v-else class="requests-grid">
          <div
            v-for="request in userRequests"
            :key="request.id"
            class="request-card"
          >
            <div class="request-card__header">
              <h3 class="request-card__title">{{ request.name }}</h3>
              <span class="request-card__badge" :class="request.status">
                {{ formatStatus(request.status) }}
              </span>
            </div>
            <div class="request-card__content">
              <p class="request-card__detail">
                <span class="request-card__label">Budżet:</span>
                <span class="request-card__value">{{ formatMoney(request.budget) }} PLN</span>
              </p>
              <p class="request-card__detail">
                <span class="request-card__label">Dofinansowanie:</span>
                <span class="request-card__value">{{ request.fundingName || 'Brak' }}</span>
              </p>
              <p v-if="request.sourceList" class="request-card__detail">
                <span class="request-card__label">Zamówienie:</span>
                <span class="request-card__value">{{ request.sourceList.name }}</span>
              </p>
              <p class="request-card__detail">
                <span class="request-card__label">Typ:</span>
                <span class="request-card__value">{{ request.ifService ? 'Usługa' : 'Produkt' }}</span>
              </p>
              <p class="request-card__detail">
                <span class="request-card__label">Plan ZP:</span>
                <span class="request-card__value">{{ formatPlanStatus(request.planComplianceStatus) }}</span>
              </p>
              <p class="request-card__detail">
                <span class="request-card__label">Data:</span>
                <span class="request-card__value">{{ formatDate(request.created_at) }}</span>
              </p>
            </div>
            <div class="request-card__actions">
              <button class="request-card__button view" @click="activeRequest = request">Otwórz wniosek</button>
              <button class="request-card__button delete" @click="deleteRequest(request.id)">Usuń</button>
            </div>
          </div>
        </div>
      </div>

      <div class="requests-section">
        <div class="requests-header">
          <div class="requests-title-section">
            <h2 class="requests-title">Wszystkie wnioski skarbników</h2>
            <p class="requests-subtitle">Wnioski wszystkich skarbników w Twojej organizacji</p>
          </div>
        </div>

        <div v-if="allRequests.length === 0" class="requests-empty">
          <p class="lists-empty-icon">📦</p>
          <p class="requests-empty-text">Brak wniosków w organizacji</p>
          <p class="requests-empty-subtext">
            Wnioski pojawią się tutaj
          </p>
        </div>

        <div v-else class="requests-grid">
          <div
            v-for="request in allRequests"
            :key="request.id"
            class="request-card"
          >
            <div class="request-card__header">
              <h3 class="request-card__title">{{ request.name }}</h3>
              <span class="request-card__badge" :class="request.status">
                {{ formatStatus(request.status) }}
              </span>
            </div>
            <div class="request-card__content">
              <p class="request-card__detail">
                <span class="request-card__label">Budżet:</span>
                <span class="request-card__value">{{ formatMoney(request.budget) }} PLN</span>
              </p>
              <p class="request-card__detail">
                <span class="request-card__label">Dofinansowanie:</span>
                <span class="request-card__value">{{ request.fundingName || 'Brak' }}</span>
              </p>
              <p v-if="request.sourceList" class="request-card__detail">
                <span class="request-card__label">Zamówienie:</span>
                <span class="request-card__value">{{ request.sourceList.name }}</span>
              </p>
              <p class="request-card__detail">
                <span class="request-card__label">Typ:</span>
                <span class="request-card__value">{{ request.ifService ? 'Usługa' : 'Produkt' }}</span>
              </p>
              <p class="request-card__detail">
                <span class="request-card__label">Plan ZP:</span>
                <span class="request-card__value">{{ formatPlanStatus(request.planComplianceStatus) }}</span>
              </p>
              <p class="request-card__detail">
                <span class="request-card__label">Data:</span>
                <span class="request-card__value">{{ formatDate(request.created_at) }}</span>
              </p>
            </div>
            <div class="request-card__actions">
              <button class="request-card__button view" @click="activeRequest = request">Otwórz wniosek</button>
            </div>
          </div>
        </div>
      </div>
    </template>

    <div v-else class="requests-section">
      <button class="request-details__back" @click="activeRequest = null">
        ← Powrót
      </button>

      <div class="request-details__card">
        <div class="request-details__top">
          <div>
            <h2 class="request-details__title">{{ activeRequest.name }}</h2>
            <p class="request-details__subtitle">Wniosek o zamówienie #{{ activeRequest.id }}</p>
          </div>
          <span class="request-card__badge" :class="activeRequest.status">
            {{ formatStatus(activeRequest.status) }}
          </span>
        </div>

        <div class="request-details__grid">
          <div class="request-info">
            <p>Kwota wniosku</p>
            <strong>{{ formatMoney(activeRequest.budget) }} PLN</strong>
          </div>
          <div v-if="activeRequest.sourceList" class="request-info">
            <p>Utworzony z zamówienia</p>
            <strong>{{ activeRequest.sourceList.name }}</strong>
          </div>
          <div class="request-info">
            <p>Dofinansowanie</p>
            <strong>{{ activeRequest.fundingName || 'Brak' }}</strong>
          </div>
          <div class="request-info">
            <p>Typ wniosku</p>
            <strong>{{ activeRequest.ifService ? 'Usługa' : 'Produkt' }}</strong>
          </div>
          <div class="request-info">
            <p>Data utworzenia</p>
            <strong>{{ formatDate(activeRequest.created_at) }}</strong>
          </div>
          <div class="request-info">
            <p>Kod CPV</p>
            <strong>{{ activeRequest.used_cpv_id ?? 'Brak' }}</strong>
          </div>
          <div class="request-info">
            <p>Zgodność z planem ZP</p>
            <strong>{{ formatPlanStatus(activeRequest.planComplianceStatus) }}</strong>
          </div>
          <div v-if="activeRequest.planPosition" class="request-info">
            <p>Pozycja planu</p>
            <strong>
              CPV {{ activeRequest.planPosition.cpv_code }},
              {{ formatMoney(activeRequest.planPosition.remaining_amount) }} PLN pozostało
            </strong>
          </div>
          <div v-if="activeRequest.planExceptionJustification" class="request-info request-info--wide">
            <p>Uzasadnienie odstępstwa</p>
            <strong>{{ activeRequest.planExceptionJustification }}</strong>
          </div>
          <div class="request-info">
            <p>Kwota dofinansowania</p>
            <strong>{{ formatMoney(activeRequest.budgetInfo?.funding_total) }} PLN</strong>
          </div>
          <div class="request-info">
            <p>Zarezerwowane z dofinansowania</p>
            <strong>{{ formatMoney(activeRequest.budgetInfo?.funding_purchase_requests_total_allocated) }} PLN</strong>
          </div>
          <div class="request-info">
            <p>Pozostało z dofinansowania</p>
            <strong>{{ formatMoney(activeRequest.budgetInfo?.funding_available_after_purchase_requests) }} PLN</strong>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showAddRequestModal" class="modal-overlay" @click="showAddRequestModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2 class="modal-title">Nowy wniosek o zamówienie</h2>
          <button class="modal-close" @click="showAddRequestModal = false">✕</button>
        </div>
        <form class="modal-form" @submit.prevent="handleNewRequest">
          <div class="modal-form__group">
            <label class="modal-form__label">Zamknięte zamówienie</label>
            <select
              v-model.number="newRequestData.shop_purchase_list_id"
              class="modal-form__input"
              required
              @change="applySelectedClosedOrder"
            >
              <option value="" disabled>Wybierz własne zamknięte zamówienie</option>
              <option
                v-for="order in availableClosedOrders"
                :key="order.shop_purchase_list_id"
                :value="order.shop_purchase_list_id"
              >
                {{ orderLabel(order) }}
              </option>
            </select>
            <p v-if="availableClosedOrders.length === 0" class="modal-form__hint">
              Nie masz zamkniętych zamówień bez utworzonego wniosku.
            </p>
          </div>
          <div class="modal-form__group">
            <label class="modal-form__label">Nazwa wniosku</label>
            <input
              v-model="newRequestData.purchase_request_name"
              type="text"
              placeholder="np. Zakup elektroniki"
              class="modal-form__input"
              required
            />
          </div>
          <div class="modal-form__group">
            <label class="modal-form__label">Budżet (PLN)</label>
            <input
              v-model="newRequestData.budget_allocated_for_the_order"
              type="number"
              min="0.01"
              step="0.01"
              placeholder="0.00"
              class="modal-form__input"
              readonly
              required
            />
          </div>
          <div class="modal-form__group">
            <label class="modal-form__label">Dofinansowanie zamówienia</label>
            <input
              :value="selectedClosedOrder?.funding_name || ''"
              type="text"
              class="modal-form__input"
              readonly
              required
              placeholder="Najpierw wybierz zamówienie"
            />
          </div>
          <div v-if="selectedClosedOrder" class="budget-preview">
            <p>
              <span>Kwota dofinansowania</span>
              <strong>{{ formatMoney(selectedClosedOrder.funding_total) }} PLN</strong>
            </p>
            <p>
              <span>Wydane</span>
              <strong>{{ formatMoney(selectedClosedOrder.funding_spent_money) }} PLN</strong>
            </p>
            <p>
              <span>Zarezerwowane z dofinansowania</span>
              <strong>{{ formatMoney(selectedClosedOrder.funding_purchase_requests_total_allocated) }} PLN</strong>
            </p>
            <p>
              <span>Dostępne po wnioskach</span>
              <strong>{{ formatMoney(projectedFundingAfterRequest) }} PLN</strong>
            </p>
          </div>
          <div class="modal-form__group">
            <label class="modal-form__label">Kod CPV</label>
            <input
              v-model.number="newRequestData.used_cpv_id"
              type="number"
              placeholder="np. 42000000"
              class="modal-form__input"
              required
            />
          </div>
          <div class="modal-form__group">
            <label class="modal-form__label">Pozycja planu zamówień publicznych</label>
            <select
              v-model="newRequestData.public_purchase_plan_id"
              class="modal-form__input"
            >
              <option :value="null">Brak pozycji w planie</option>
              <option
                v-for="position in matchingPlanPositions"
                :key="position.public_purchase_plan_id"
                :value="position.public_purchase_plan_id"
              >
                CPV {{ position.cpv_code }} - pozostało {{ formatMoney(position.remaining_amount) }} PLN
              </option>
            </select>
            <p v-if="selectedClosedOrder && matchingPlanPositions.length === 0" class="modal-form__hint">
              To dofinansowanie nie ma pozycji z podanym kodem CPV.
            </p>
          </div>
          <div v-if="requiresPlanException" class="modal-form__group">
            <label class="modal-form__label">Uzasadnienie odstępstwa od planu</label>
            <textarea
              v-model="newRequestData.plan_exception_justification"
              class="modal-form__input modal-form__textarea"
              placeholder="Wyjaśnij brak pozycji w planie lub przekroczenie zaplanowanej kwoty"
              required
            ></textarea>
            <p class="modal-form__hint">
              Wniosek będzie wymagał wyjątkowego zatwierdzenia.
            </p>
          </div>
          <div class="modal-form__group">
            <label class="modal-form__label">Czy to usługa?</label>
            <button
              type="button"
              class="modal-form__toggle"
              :class="{ active: newRequestData.if_service }"
              @click="newRequestData.if_service = !newRequestData.if_service"
            >
              {{ newRequestData.if_service ? 'Tak – usługa' : 'Nie – produkt' }}
            </button>
          </div>
          <div class="modal-actions">
            <button type="button" class="modal-btn modal-btn-cancel" @click="showAddRequestModal = false">Anuluj</button>
            <button type="submit" class="modal-btn modal-btn-save" :disabled="!selectedClosedOrder">Złóż wniosek</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, watch } from 'vue'
import { useAuth } from '@/composables/useAuth'

const API_URL = 'http://localhost:8080/api'
const { user } = useAuth()
const emit = defineEmits(['budget-changed'])
const activeRequest = ref(null)
const showAddRequestModal = ref(false)

const userRequests = ref([])
const allRequests = ref([])
const closedOrders = ref([])
const fundingPlan = ref(null)

const currentFinanceManagerId = computed(() => {
  return user.value?.projectFinanceManagerId || user.value?.id
})

const newRequestData = ref({
  purchase_request_name: '',
  budget_allocated_for_the_order: null,
  if_service: false,
  used_cpv_id: 1,
  can_add: true,
  shop_purchase_list_id: '',
  public_purchase_plan_id: null,
  plan_exception_justification: ''
})

const availableClosedOrders = computed(() => {
  return closedOrders.value.filter(order => !order.purchase_request_id)
})

const selectedClosedOrder = computed(() => {
  return availableClosedOrders.value.find(
    order => order.shop_purchase_list_id === newRequestData.value.shop_purchase_list_id
  )
})

const projectedFundingAfterRequest = computed(() => {
  const available = selectedClosedOrder.value?.funding_available_after_purchase_requests || 0
  const requested = Number(newRequestData.value.budget_allocated_for_the_order || 0)
  return available - requested
})

const matchingPlanPositions = computed(() => {
  const cpv = Number(newRequestData.value.used_cpv_id)
  return (fundingPlan.value?.public_purchase_plans || []).filter(
    position => Number(position.cpv_code) === cpv
  )
})

const selectedPlanPosition = computed(() =>
  matchingPlanPositions.value.find(
    position => position.public_purchase_plan_id === newRequestData.value.public_purchase_plan_id
  ) || null
)

const requiresPlanException = computed(() => {
  if (!selectedClosedOrder.value) return false
  if (!selectedPlanPosition.value) return true
  return Number(newRequestData.value.budget_allocated_for_the_order || 0)
    > Number(selectedPlanPosition.value.remaining_amount || 0)
})

const mapRequest = (req) => ({
  id: req.purchase_request_id,
  name: req.purchase_request_name,
  budget: req.budget_allocated_for_the_order,
  ifService: req.if_service,
  status: req.can_add ? 'pending' : 'approved',
  created_at: req.created_at,
  used_cpv_id: req.used_cpv_id,
  projectBudgetId: req.project_budget_id,
  projectBudgetName: req.project_budget_name,
  fundingId: req.funding_id,
  fundingName: req.funding_name,
  associationBudgetId: req.association_budget_id,
  associationBudgetName: req.association_budget_name,
  budgetInfo: req.budget_info,
  sourceList: req.source_shop_purchase_list
    ? {
        id: req.source_shop_purchase_list.shop_purchase_list_id,
        name: req.source_shop_purchase_list.name || `Zamówienie #${req.source_shop_purchase_list.shop_purchase_list_id}`,
        shopName: req.source_shop_purchase_list.shop_name,
        totalPrice: req.source_shop_purchase_list.total_price,
        settlementId: req.source_shop_purchase_list.settlement_id,
        fundingId: req.source_shop_purchase_list.funding_id,
        fundingName: req.source_shop_purchase_list.funding_name
      }
    : null,
  planPosition: req.plan_position,
  planExceptionJustification: req.plan_exception_justification,
  planComplianceStatus: req.plan_compliance_status,
  itemCount: 0
})

const fetchRequests = async () => {
  try {
    const response = await fetch(`${API_URL}/purchase_requests`)
    if (!response.ok) throw new Error('Błąd pobierania danych')

    const data = await response.json()
    allRequests.value = data.map(mapRequest)
  } catch (error) {
    console.error('Błąd pobierania wniosków:', error)
  }
}

const fetchRequestsBySpecificProjectFinanceManager = async () => {
  if (!currentFinanceManagerId.value) return

  try {
    const response = await fetch(`${API_URL}/purchase_requests/${currentFinanceManagerId.value}`)
    if (!response.ok) throw new Error('Błąd pobierania danych')

    const data = await response.json()
    userRequests.value = data.map(mapRequest)
  } catch (error) {
    console.error('Błąd pobierania wniosków dla managera:', error)
  }
}

const fetchClosedOrdersForRequests = async () => {
  if (!currentFinanceManagerId.value) return

  try {
    const response = await fetch(
      `${API_URL}/lists/closed_for_purchase_requests?project_finance_manager_id=${currentFinanceManagerId.value}`
    )
    if (!response.ok) throw new Error('Błąd pobierania zamkniętych zamówień')

    closedOrders.value = await response.json()
  } catch (error) {
    console.error('Błąd pobierania zamkniętych zamówień:', error)
  }
}

const fetchFundingPlan = async fundingId => {
  fundingPlan.value = null
  if (!fundingId) return
  const response = await fetch(`${API_URL}/public_purchase_plan_lists?funding_id=${fundingId}`)
  if (!response.ok) return
  const plans = await response.json()
  fundingPlan.value = plans[0] || null
}

const applySelectedClosedOrder = async () => {
  const order = selectedClosedOrder.value
  if (!order) return

  const orderName = order.name?.trim() || `Zamówienie #${order.shop_purchase_list_id}`
  const total = Number(order.total_price || order.cost || 0)
  newRequestData.value.purchase_request_name = `Wniosek: ${orderName}`
  newRequestData.value.budget_allocated_for_the_order = Math.round(total * 100) / 100
  newRequestData.value.used_cpv_id = order.suggested_cpv_id || newRequestData.value.used_cpv_id || 1
  newRequestData.value.public_purchase_plan_id = null
  newRequestData.value.plan_exception_justification = ''
  await fetchFundingPlan(order.funding_id)
  const match = matchingPlanPositions.value[0]
  if (match) newRequestData.value.public_purchase_plan_id = match.public_purchase_plan_id
}

const resetRequestForm = () => {
  newRequestData.value.purchase_request_name = ''
  newRequestData.value.budget_allocated_for_the_order = null
  newRequestData.value.if_service = false
  newRequestData.value.used_cpv_id = 1
  newRequestData.value.can_add = true
  newRequestData.value.shop_purchase_list_id = ''
  newRequestData.value.public_purchase_plan_id = null
  newRequestData.value.plan_exception_justification = ''
  fundingPlan.value = null
}

const openAddRequestModal = async () => {
  await fetchClosedOrdersForRequests()
  resetRequestForm()
  showAddRequestModal.value = true
}

const handleNewRequest = async () => {
  if (!currentFinanceManagerId.value) {
    alert("Błąd: Nie można utworzyć wniosku, brak ID skarbnika.")
    return
  }
  if (!selectedClosedOrder.value) {
    alert("Wybierz zamknięte zamówienie, z którego ma powstać wniosek.")
    return
  }

  try {
    const payload = {
      purchase_request_name: newRequestData.value.purchase_request_name,
      budget_allocated_for_the_order: newRequestData.value.budget_allocated_for_the_order,
      if_service: newRequestData.value.if_service,
      used_cpv_id: newRequestData.value.used_cpv_id,
      created_at: new Date().toISOString(),
      can_add: newRequestData.value.can_add,
      project_finance_manager_id: currentFinanceManagerId.value,
      shop_purchase_list_id: newRequestData.value.shop_purchase_list_id,
      public_purchase_plan_id: newRequestData.value.public_purchase_plan_id,
      plan_exception_justification: newRequestData.value.plan_exception_justification
    }

    const response = await fetch(`${API_URL}/create_purchase_requests`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })

    if (!response.ok) {
      const error = await response.json()
      alert(`Błąd przy dodawaniu wniosku: ${error.detail || 'Nieznany błąd'}`)
      return
    }

    resetRequestForm()
    showAddRequestModal.value = false

    await Promise.all([
      fetchRequests(),
      fetchRequestsBySpecificProjectFinanceManager(),
      fetchClosedOrdersForRequests()
    ])
    emit('budget-changed')

  } catch (error) {
    console.error('Błąd przy dodawaniu wniosku:', error)
  }
}

const deleteRequest = async (id) => {
  if (!confirm('Czy na pewno chcesz usunąć ten wniosek?')) return

  try {
    const response = await fetch(`${API_URL}/purchase_requests/${id}`, { method: 'DELETE' })
    if (response.ok) {
      userRequests.value = userRequests.value.filter(r => r.id !== id)
      allRequests.value = allRequests.value.filter(r => r.id !== id)
      await fetchClosedOrdersForRequests()
      emit('budget-changed')
      
      // Jeśli usunięty wniosek był aktualnie otwarty, zamknij go
      if (activeRequest.value?.id === id) {
        activeRequest.value = null
      }
    }
  } catch (error) {
    console.error('Błąd usuwania wniosku:', error)
  }
}

const formatStatus = (status) => {
  const map = { pending: 'Oczekujący', approved: 'Zatwierdzony', rejected: 'Odrzucony' }
  return map[status] || status
}

const formatPlanStatus = status => {
  if (status === 'compliant') return 'Zgodny z planem'
  if (status === 'requires_approval') return 'Wymaga zgody'
  return status || 'Brak danych'
}

const formatDate = (dateStr) => {
  if (!dateStr) return '—'
  return new Intl.DateTimeFormat('pl-PL').format(new Date(dateStr))
}

const formatMoney = (value) => {
  return Number(value || 0).toLocaleString('pl-PL', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

const orderLabel = (order) => {
  const name = order.name?.trim() || `Zamówienie #${order.shop_purchase_list_id}`
  const shop = order.shop_name || 'Brak sklepu'
  const total = formatMoney(order.total_price || order.cost)
  return `${name} - ${shop} - ${total} PLN`
}

onMounted(() => {
  fetchRequests()
  fetchClosedOrdersForRequests()
})

// Obserwujemy ID użytkownika i pobieramy dane, gdy jest dostępne
watch(
  () => currentFinanceManagerId.value,
  (newId) => {
    if (newId) {
      fetchRequestsBySpecificProjectFinanceManager()
      fetchClosedOrdersForRequests()
    }
  },
  { immediate: true }
)

watch(
  () => newRequestData.value.used_cpv_id,
  () => {
    if (!selectedPlanPosition.value) {
      newRequestData.value.public_purchase_plan_id = null
    }
  }
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
  background: rgba(251, 191, 36, 0.2);
  color: #fcd34d;
}

.request-card__badge.approved {
  background: rgba(34, 197, 94, 0.2);
  color: #86efac;
}

.request-card__badge.rejected {
  background: rgba(239, 68, 68, 0.2);
  color: #fca5a5;
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

.request-card__button.delete {
  background: rgba(239, 68, 68, 0.2);
  color: #fca5a5;
}

.request-card__button.delete:hover {
  background: rgba(239, 68, 68, 0.35);
}

/* WIDOK SZCZEGÓŁÓW (Zaadaptowany z rozliczeń) */
.request-details__back {
  margin-bottom: 2vh;
  background: none;
  border: none;
  color: #93c5fd;
  cursor: pointer;
  font-size: 1vw;
  font-family: 'Nunito', system-ui, sans-serif;
}

.request-details__card {
  background: rgba(15, 23, 42, 0.6);
  border: 0.08vw solid rgba(148, 163, 184, 0.15);
  border-radius: 1vw;
  padding: 2vw;
}

.request-details__top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2vw;
}

.request-details__title {
  color: white;
  margin: 0;
  font-size: 1.6vw;
  font-weight: 800;
}

.request-details__subtitle {
  color: rgba(226, 232, 240, 0.5);
  margin: 0.5vh 0 0 0;
}

.request-details__grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1vw;
  margin-bottom: 2vw;
}

.request-info {
  background: rgba(30, 41, 59, 0.6);
  padding: 1vw;
  border-radius: 0.8vw;
}

.request-info p {
  color: rgba(226, 232, 240, 0.5);
  margin: 0 0 0.5vh 0;
  font-size: 0.9vw;
}

.request-info strong {
  color: white;
  font-size: 1vw;
}

.request-info--wide {
  grid-column: 1 / -1;
}

.request-details__items h3 {
  color: #bfdbfe;
  margin: 0;
  font-size: 1.2vw;
}

.items-empty {
  background: rgba(30, 41, 59, 0.5);
  padding: 2vw;
  border-radius: 0.8vw;
  text-align: center;
  border: 0.08vw dashed rgba(148, 163, 184, 0.3);
}

/* MODAL */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.7);
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 5vh 0;
  z-index: 1000;
  overflow-y: auto;
}

.modal-content {
  width: 100%;
  max-width: 35vw;
  max-height: 90vh;
  overflow-y: auto;
  background: #111827;
  border: 0.08vw solid rgba(148,163,184,0.15);
  border-radius: 1vw;
  padding: 2vw;
}

.modal-content::-webkit-scrollbar {
  width: 0.45vw;
}

.modal-content::-webkit-scrollbar-thumb {
  background: rgba(148, 163, 184, 0.35);
  border-radius: 1vw;
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

.modal-form__input:disabled,
.modal-form__input[readonly] {
  opacity: 0.78;
  cursor: not-allowed;
}

.modal-form__hint {
  margin: 0;
  color: #fcd34d;
  font-size: 0.85vw;
  line-height: 1.4;
}

.modal-form__textarea {
  min-height: 110px;
  resize: vertical;
}

.budget-preview {
  display: grid;
  gap: 0.6vw;
  padding: 1vw;
  border: 0.08vw solid rgba(59, 130, 246, 0.22);
  border-radius: 0.8vw;
  background: rgba(30, 41, 59, 0.55);
}

.budget-preview p {
  display: flex;
  justify-content: space-between;
  gap: 1vw;
  margin: 0;
  color: rgba(226, 232, 240, 0.72);
  font-size: 0.9vw;
}

.budget-preview strong {
  color: #ffffff;
}

.modal-form__toggle {
  padding: 0.9vw;
  border-radius: 0.7vw;
  border: none;
  background: rgba(59,130,246,0.15);
  color: #bfdbfe;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.modal-form__toggle.active {
  background: rgba(34,197,94,0.2);
  color: #86efac;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1vw;
  position: sticky;
  bottom: -2vw;
  margin: 1vw -2vw -2vw;
  padding: 1vw 2vw 2vw;
  background: #111827;
  border-top: 0.08vw solid rgba(148,163,184,0.15);
  z-index: 2;
}

.modal-btn {
  padding: 0.8vw 1.4vw;
  border-radius: 0.7vw;
  border: none;
  cursor: pointer;
  font-weight: 700;
}

.modal-btn-cancel {
  background: rgba(148,163,184,0.15);
  color: #e2e8f0;
}

.lists-empty-icon {
  font-size: 4vw;
  margin: 0 0 1.5vh 0;
}

.modal-btn-save {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
}

.modal-btn-save:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}
</style>
