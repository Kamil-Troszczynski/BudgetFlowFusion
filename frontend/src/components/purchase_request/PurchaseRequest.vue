<template>
  <div class="requests-container">
    <template v-if="!activeRequest">
      <div class="requests-section">
        
        <div class="requests-filter-bar">
          <div class="filter-group-item">
            <label class="sort-label">Sekcja Koła:</label>
            <select v-model="selectedSectionFilter" class="excel-sort-select section-filter-dropdown">
              <option value="">Wszystkie sekcje</option>
              <option v-for="section in uniqueSections" :key="section" :value="section">
                {{ section }}
              </option>
            </select>
          </div>

          <div class="filter-group-item">
            <label class="sort-label">Sortuj:</label>
            <select v-model="sortBy" class="excel-sort-select">
              <option value="date-created-desc">Data utworzenia: od najnowszych</option>
              <option value="date-created-asc">Data utworzenia: od najstarszych</option>
              <option value="date-modified-desc">Ostatnia edycja: od najnowszych</option>
              <option value="budget-desc">Budżet wniosku: malejąco</option>
              <option value="budget-asc">Budżet wniosku: rosnąco</option>
              <option value="gross-desc">Suma koszyka brutto: malejąco</option>
              <option value="gross-asc">Suma koszyka brutto: rosnąco</option>
            </select>
          </div>

          <div class="view-toggle-container">
            <button 
              class="toggle-view-btn" 
              :class="{ 'toggle-view-btn--active': currentLayout === 'grid' }"
              @click="currentLayout = 'grid'"
            >
              Kafelki
            </button>
            <button 
              class="toggle-view-btn" 
              :class="{ 'toggle-view-btn--active': currentLayout === 'list' }"
              @click="currentLayout = 'list'"
            >
              Lista
            </button>
          </div>
        </div>

        <div class="requests-header">
          <div class="requests-title-section">
            <h2 class="requests-title">Wnioski o zamówienie</h2>
            <p class="requests-subtitle">Wykaz wszystkich wniosków zakupowych w organizacji</p>
          </div>
          <button class="requests-add-button" @click="openAddRequestModal">+ Nowy wniosek</button>
        </div>

        <div v-for="group in aggregatedRequestGroups" :key="group.key" class="request-status-group">
          <h3 class="status-group-title">{{ group.title }} ({{ group.items.length }})</h3>
          
          <div v-if="group.items.length === 0" class="requests-empty requests-empty--compact">
            <p class="requests-empty-subtext">Brak wniosków w tej sekcji statusu</p>
          </div>

          <template v-else>
            <div v-if="currentLayout === 'grid'" class="requests-grid">
              <div v-for="request in group.items" :key="request.id" class="request-card">
                <div class="request-card__header">
                  <div>
                    <h3 class="request-card__title">{{ request.name }}</h3>
                    <span v-if="request.sectionName" class="request-card__section-badge">{{ request.sectionName }}</span>
                  </div>
                  <span class="request-card__badge" :class="request.status">
                    {{ formatStatus(request.status) }}
                  </span>
                </div>
                <div class="request-card__content">
                  <p class="request-card__detail">
                    <span class="request-card__label">Budżet wniosku:</span>
                    <span class="request-card__value text-blue font-bold">{{ formatMoney(request.budget) }} PLN</span>
                  </p>
                  <p class="request-card__detail">
                    <span class="request-card__label">Suma koszyka Brutto:</span>
                    <span class="request-card__value text-blue font-bold">{{ formatMoney(request.sourceList__totalPrice || request.budget) }} PLN</span>
                  </p>
                  <p class="request-card__detail">
                    <span class="request-card__label">Sklepy:</span>
                    <span class="request-card__value text-white">{{ request.sourceList__shopCount || 1 }}</span>
                  </p>
                  <p class="request-card__detail">
                    <span class="request-card__label">Utworzył (Skarbnik):</span>
                    <span class="request-card__value text-white font-bold">{{ request.creatorName || 'Nieznany' }}</span>
                  </p>
                  <p class="request-card__detail">
                    <span class="request-card__label">Utworzono:</span>
                    <span class="request-card__value text-white">{{ formatRelativeTime(request.created_at) }}</span>
                  </p>
                  <p class="request-card__detail">
                    <span class="request-card__label">Ostatnia edycja:</span>
                    <span class="request-card__value text-emerald font-bold">{{ formatRelativeTime(request.updated_at || request.created_at) }}</span>
                  </p>
                </div>
                <div class="request-card__actions">
                  <button class="request-card__button view" @click="emit('open-shopping', request)">Lista</button>
                  <button v-if="isOwner(request)" class="request-card__button view" @click="openEditRequestModal(request)">Edytuj</button>
                  <button class="request-card__button view" @click="activeRequest = request">Podsumowanie</button>
                  <button v-if="isOwner(request)" class="request-card__button delete" @click="deleteRequest(request.id)">Usuń</button>
                </div>
              </div>
            </div>

            <div v-else class="excel-table-wrapper custom-scrollbar">
              <table class="excel-list-table">
                <thead>
                  <tr>
                    <th>Nazwa wniosku</th>
                    <th>Sekcja koła</th>
                    <th>Status</th>
                    <th>Budżet</th>
                    <th>Suma Brutto</th>
                    <th>Sklepy</th>
                    <th>Utworzył (Skarbnik)</th>
                    <th>Utworzono</th>
                    <th>Ostatnia edycja</th>
                    <th>Akcje</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="request in group.items" :key="request.id">
                    <td class="font-bold text-white">{{ request.name }}</td>
                    <td><span class="table-section-badge">{{ request.sectionName || '-' }}</span></td>
                    <td><span class="request-card__badge text-badge-only" :class="request.status">{{ formatStatus(request.status) }}</span></td>
                    <td class="font-mono text-blue font-bold">{{ formatMoney(request.budget) }} PLN</td>
                    <td class="font-mono text-blue font-bold">{{ formatMoney(request.sourceList__totalPrice || request.budget) }} PLN</td>
                    <td>{{ request.sourceList__shopCount || 1 }}</td>
                    <td class="font-bold text-white">{{ request.creatorName || 'Nieznany' }}</td>
                    <td>{{ formatDate(request.created_at) }}</td>
                    <td>{{ formatRelativeTime(request.updated_at || request.created_at) }}</td>
                    <td>
                      <div class="table-row-actions">
                        <button class="table-btn view" @click="emit('open-shopping', request)">Lista</button>
                        <button v-if="isOwner(request)" class="table-btn view" @click="openEditRequestModal(request)">Edytuj</button>
                        <button class="table-btn view" @click="activeRequest = request">Podsumowanie</button>
                        <button v-if="isOwner(request)" class="table-btn delete" @click="deleteRequest(request.id)">Usuń</button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </template>
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
            <strong class="text-blue">{{ formatMoney(activeRequest.budget) }} PLN</strong>
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
            <p>Sekcja Koła</p>
            <strong class="text-amber">{{ activeRequest.sectionName || 'Brak przypisania' }}</strong>
          </div>
          <div class="request-info">
            <p>Utworzył (Skarbnik)</p>
            <strong>{{ activeRequest.creatorName || 'Nieznany' }}</strong>
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
            <strong class="font-mono">{{ activeRequest.used_cpv_id ?? 'Brak' }}</strong>
          </div>
          <div class="request-info">
            <p>Zgodność z planem ZP</p>
            <strong>{{ formatPlanStatus(activeRequest.planComplianceStatus) }}</strong>
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
            <label class="modal-form__label">Sekcja koła</label>
            <select
              v-model="newRequestData.section_name"
              class="modal-form__input"
              required
            >
              <option value="" disabled>Wybierz sekcję koła...</option>
              <option v-for="section in uniqueSections" :key="section" :value="section">
                {{ section }}
              </option>
            </select>
          </div>

          <div v-if="editingRequestId" class="modal-form__group">
            <label class="modal-form__label">Finansowanie</label>
            <div class="funding-allocation-row">
              <select v-model.number="allocationDraft.funding_id" class="modal-form__input">
                <option value="" disabled>Wybierz dofinansowanie...</option>
                <option
                  v-for="funding in fundings"
                  :key="funding.funding_id"
                  :value="funding.funding_id"
                >
                  {{ funding.funding_name }} (dostepne: {{ formatMoney(funding.available_after_purchase_requests) }} PLN)
                </option>
              </select>
              <input
                v-model.number="allocationDraft.allocated_amount"
                type="number"
                min="0.01"
                step="0.01"
                placeholder="Kwota"
                class="modal-form__input"
              />
              <button type="button" class="modal-btn modal-btn-save-add" @click="addFundingAllocation">Dodaj</button>
            </div>
            <div v-if="newRequestData.funding_allocations.length > 0" class="funding-allocation-list">
              <div
                v-for="allocation in newRequestData.funding_allocations"
                :key="allocation.funding_id"
                class="funding-allocation-item"
              >
                <span>{{ fundingName(allocation.funding_id) }}</span>
                <strong>{{ formatMoney(allocation.allocated_amount) }} PLN</strong>
                <button type="button" class="delete-inline-btn" @click="removeFundingAllocation(allocation.funding_id)">Usun</button>
              </div>
              <div class="funding-allocation-total">
                <span>Razem</span>
                <strong>{{ formatMoney(allocationTotal) }} PLN</strong>
              </div>
            </div>
            <p v-else class="modal-form__hint">Dodaj przynajmniej jedno zrodlo finansowania.</p>
          </div>
          <div v-if="editingRequestId" class="modal-form__group">
            <label class="modal-form__label">Kod CPV</label>
            <input
              v-model.number="newRequestData.used_cpv_id"
              type="number"
              placeholder="np. 42000000"
              class="modal-form__input"
              required
            />
          </div>
          <div v-if="editingRequestId" class="modal-form__group">
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
                {{ position.funding_name }} - CPV {{ position.cpv_code }} - pozostalo {{ formatMoney(position.remaining_amount) }} PLN
              </option>
            </select>
          </div>
          <div v-if="editingRequestId && requiresPlanException" class="modal-form__group">
            <label class="modal-form__label">Uzasadnienie odstępstwa od planu</label>
            <textarea
              v-model="newRequestData.plan_exception_justification"
              class="modal-form__input modal-form__textarea"
              placeholder="Wyjaśnij brak pozycji w planie lub przekroczenie zaplanowanej kwoty"
              required
            ></textarea>
          </div>
          <div class="modal-actions">
            <button type="button" class="modal-btn modal-btn-cancel" @click="showAddRequestModal = false">Anuluj</button>
            <button type="submit" class="modal-btn modal-btn-save" :disabled="editingRequestId && !selectedFunding">Złóż wniosek</button>
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
const emit = defineEmits(['budget-changed', 'open-shopping'])
const activeRequest = ref(null)
const showAddRequestModal = ref(false)
const editingRequestId = ref(null)
const sortBy = ref('date-created-desc')
const currentLayout = ref('grid')
const selectedSectionFilter = ref('')

const allRequests = ref([])
const closedOrders = ref([])
const fundings = ref([])
const fundingPlans = ref([])
const allocationDraft = ref({ funding_id: '', allocated_amount: null })
const studentsMap = ref({})

const currentFinanceManagerId = computed(() => {
  return user.value?.projectFinanceManagerId || user.value?.id
})

const newRequestData = ref({
  purchase_request_name: '',
  section_name: '',
  budget_allocated_for_the_order: null,
  if_service: false,
  used_cpv_id: 1,
  can_add: true,
  shop_purchase_list_id: '',
  funding_id: '',
  project_budget_id: null,
  funding_allocations: [],
  public_purchase_plan_id: null,
  plan_exception_justification: ''
})

const uniqueSections = computed(() => {
  const sectionsSet = new Set()
  fundings.value.forEach(f => {
    if (f.project_budget_name) sectionsSet.add(f.project_budget_name)
  })
  if (sectionsSet.size === 0) {
    return ['Elektronika', 'Konstrukcja', 'Software', 'Aero', 'Marketing']
  }
  return Array.from(sectionsSet)
})

const selectedFunding = computed(() =>
  fundings.value.find(funding => Number(funding.funding_id) === Number(newRequestData.value.funding_id)) || null
)

const allocationTotal = computed(() =>
  newRequestData.value.funding_allocations.reduce(
    (sum, allocation) => sum + Number(allocation.allocated_amount || 0),
    0
  )
)

const matchingPlanPositions = computed(() => {
  const cpv = Number(newRequestData.value.used_cpv_id)
  return fundingPlans.value.flatMap(plan =>
    (plan.public_purchase_plans || []).map(position => ({
      ...position,
      funding_name: plan.funding_name || fundingName(plan.funding_id)
    }))
  ).filter( position => Number(position.cpv_code) === cpv )
})

const selectedPlanPosition = computed(() =>
  matchingPlanPositions.value.find(
    position => Number(position.public_purchase_plan_id) === Number(newRequestData.value.public_purchase_plan_id)
  ) || null
)

const requiresPlanException = computed(() => {
  if (!selectedFunding.value) return false
  if (!selectedPlanPosition.value) return true
  return Number(allocationTotal.value || newRequestData.value.budget_allocated_for_the_order || 0) > Number(selectedPlanPosition.value.remaining_amount || 0)
})

const isOwner = (request) => {
  return Number(request.project_finance_manager_id) === Number(currentFinanceManagerId.value)
}

const filterAndSortList = (itemsList) => {
  let filtered = [...itemsList]
  if (selectedSectionFilter.value) {
    filtered = filtered.filter(item => item.sectionName === selectedSectionFilter.value)
  }
  
  if (sortBy.value === 'date-created-desc') return filtered.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
  if (sortBy.value === 'date-created-asc') return filtered.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
  if (sortBy.value === 'date-modified-desc') return filtered.sort((a, b) => new Date(b.updated_at || b.created_at).getTime() - new Date(a.updated_at || a.created_at).getTime())
  if (sortBy.value === 'budget-desc') return filtered.sort((a, b) => Number(b.budget || 0) - Number(a.budget || 0))
  if (sortBy.value === 'budget-asc') return filtered.sort((a, b) => Number(a.budget || 0) - Number(b.budget || 0))
  if (sortBy.value === 'gross-desc') return filtered.sort((a, b) => Number(b.sourceList__totalPrice || b.budget || 0) - Number(a.sourceList__totalPrice || a.budget || 0))
  if (sortBy.value === 'gross-asc') return filtered.sort((a, b) => Number(a.sourceList__totalPrice || a.budget || 0) - Number(b.sourceList__totalPrice || b.budget || 0))
  return filtered
}

const aggregatedRequestGroups = computed(() => {
  const processed = filterAndSortList(allRequests.value)
  return [
    { key: 'open', title: 'Otwarte wnioski', items: processed.filter(r => r.status === 'pending') },
    { key: 'closed', title: 'Zamknięte wnioski', items: processed.filter(r => r.status !== 'pending') }
  ]
})

const formatRelativeTime = (dateInput) => {
  if (!dateInput) return '—'
  const dateStr = String(dateInput).endsWith('Z') || String(dateInput).includes('+') ? dateInput : `${dateInput}Z`
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  if (diffMs < 0 && diffMs > -60000) return 'przed chwilą'
  const diffSec = Math.floor(diffMs / 1000)
  const diffMin = Math.floor(diffSec / 60)
  const diffHour = Math.floor(diffMin / 60)
  if (diffSec < 60) return 'przed chwilą'
  if (diffMin < 60) return `${diffMin} min temu`
  if (diffHour < 24) return `${diffHour} godz. temu`
  return new Intl.DateTimeFormat('pl-PL').format(date)
}

const mapRequest = (req) => {
  const pfmId = req.project_finance_manager_id
  return {
    id: req.purchase_request_id,
    name: req.purchase_request_name,
    sectionName: req.section_name || req.project_budget_name,
    budget: req.budget_allocated_for_the_order,
    ifService: req.if_service,
    status: req.can_add ? 'pending' : 'approved',
    created_at: req.created_at,
    updated_at: req.updated_at,
    used_cpv_id: req.used_cpv_id,
    projectBudgetId: req.project_budget_id,
    projectBudgetName: req.project_budget_name,
    fundingId: req.funding_id,
    fundingName: req.funding_name,
    fundingAllocations: req.funding_allocations || [],
    project_finance_manager_id: pfmId,
    creatorName: pfmId ? (studentsMap.value[pfmId] || `Skarbnik #${pfmId}`) : 'Nieznany',
    sourceList: req.source_shop_purchase_list,
    sourceList__shopCount: req.source_shop_purchase_list?.shop_count,
    sourceList__totalNet: req.source_shop_purchase_list?.total_net,
    sourceList__totalPrice: req.source_shop_purchase_list?.total_price,
    planPosition: req.plan_position,
    planExceptionJustification: req.plan_exception_justification,
    planComplianceStatus: req.plan_compliance_status
  }
}

const fetchStudentsMap = async () => {
  try {
    const response = await fetch(`${API_URL}/students`, { cache: 'no-store' })
    if (!response.ok) return
    const data = await response.json()
    const map = {}
    ;(data || []).forEach(s => {
      const id = s.student_id ?? s.id
      const fullName = [s.name, s.surname].filter(Boolean).join(' ')
      if (id) map[id] = fullName || `Student #${id}`
    })
    studentsMap.value = map
  } catch (e) {
    console.error(e)
  }
}

const fetchRequests = async () => {
  try {
    const response = await fetch(`${API_URL}/purchase_requests`)
    if (!response.ok) throw new Error('Błąd pobierania danych')
    const data = await response.json()
    allRequests.value = data.map(mapRequest)
  } catch (error) {
    console.error(error)
  }
}

const fetchClosedOrdersForRequests = async () => {
  if (!currentFinanceManagerId.value) return
  try {
    const response = await fetch(`${API_URL}/lists/closed_for_purchase_requests?project_finance_manager_id=${currentFinanceManagerId.value}`)
    closedOrders.value = await response.json()
  } catch (error) {
    console.error(error)
  }
}

const fetchFundings = async () => {
  if (!user.value?.association_id) return
  try {
    const response = await fetch(`${API_URL}/fundings?association_id=${user.value.association_id}`)
    fundings.value = await response.json()
  } catch (error) {
    console.error(error)
  }
}

const fetchFundingPlan = async fundingId => {
  fundingPlans.value = []
  if (!fundingId) return
  const response = await fetch(`${API_URL}/public_purchase_plan_lists?funding_id=${fundingId}`)
  if (!response.ok) return
  const plans = await response.json()
  const plan = plans[0] || null
  fundingPlans.value = plan ? [plan] : []
}

const fetchFundingPlansForAllocations = async () => {
  const fundingIds = [...new Set(newRequestData.value.funding_allocations.map(a => Number(a.funding_id)).filter(Boolean))]
  if (fundingIds.length === 0) { fundingPlans.value = []; return; }
  const plans = await Promise.all(fundingIds.map(async fundingId => {
    const response = await fetch(`${API_URL}/public_purchase_plan_lists?funding_id=${fundingId}`)
    if (!response.ok) return null
    const data = await response.json()
    return data[0] || null
  }))
  fundingPlans.value = plans.filter(Boolean)
}

const fundingName = fundingId => {
  const funding = fundings.value.find(item => Number(item.funding_id) === Number(fundingId))
  return funding?.funding_name || `Dofinansowanie #${fundingId}`
}

const addFundingAllocation = () => {
  const fundingId = Number(allocationDraft.value.funding_id)
  const amount = Number(allocationDraft.value.allocated_amount || 0)
  if (!fundingId || amount <= 0) return
  const existing = newRequestData.value.funding_allocations.find(a => Number(a.funding_id) === fundingId)
  if (existing) { existing.allocated_amount = Number(existing.allocated_amount) + amount } 
  else { newRequestData.value.funding_allocations.push({ funding_id: fundingId, allocated_amount: amount }) }
  if (!newRequestData.value.funding_id) {
    newRequestData.value.funding_id = fundingId
    const funding = fundings.value.find(item => Number(item.funding_id) === fundingId)
    newRequestData.value.project_budget_id = funding?.project_budget_id || null
  }
  fetchFundingPlansForAllocations()
  allocationDraft.value = { funding_id: '', allocated_amount: null }
}

const removeFundingAllocation = fundingId => {
  newRequestData.value.funding_allocations = newRequestData.value.funding_allocations.filter(a => Number(a.funding_id) !== Number(fundingId))
  if (Number(newRequestData.value.funding_id) === Number(fundingId)) {
    const first = newRequestData.value.funding_allocations[0]
    newRequestData.value.funding_id = first?.funding_id || ''
    const funding = fundings.value.find(item => Number(item.funding_id) === Number(newRequestData.value.funding_id))
    newRequestData.value.project_budget_id = funding?.project_budget_id || null
  }
  fetchFundingPlansForAllocations()
}

const resetRequestForm = () => {
  newRequestData.value.purchase_request_name = ''
  newRequestData.value.section_name = ''
  newRequestData.value.budget_allocated_for_the_order = null
  newRequestData.value.if_service = false
  newRequestData.value.used_cpv_id = 1
  newRequestData.value.can_add = true
  newRequestData.value.shop_purchase_list_id = ''
  newRequestData.value.funding_id = ''
  newRequestData.value.project_budget_id = null
  newRequestData.value.funding_allocations = []
  newRequestData.value.public_purchase_plan_id = null
  newRequestData.value.plan_exception_justification = ''
  allocationDraft.value = { funding_id: '', allocated_amount: null }
  fundingPlans.value = []
}

const openAddRequestModal = async () => {
  await fetchFundings()
  resetRequestForm()
  editingRequestId.value = null
  showAddRequestModal.value = true
}

const openEditRequestModal = async (request) => {
  await fetchFundings()
  editingRequestId.value = request.id
  newRequestData.value.purchase_request_name = request.name
  newRequestData.value.section_name = request.sectionName || ''
  newRequestData.value.budget_allocated_for_the_order = request.budget
  newRequestData.value.if_service = request.ifService
  newRequestData.value.used_cpv_id = request.used_cpv_id || 1
  newRequestData.value.can_add = request.status === 'pending'
  newRequestData.value.shop_purchase_list_id = ''
  newRequestData.value.funding_id = request.fundingId
  newRequestData.value.project_budget_id = request.projectBudgetId
  newRequestData.value.funding_allocations = request.fundingAllocations?.length
    ? request.fundingAllocations.map(allocation => ({
        funding_id: allocation.funding_id,
        allocated_amount: allocation.allocated_amount
      }))
    : [{
        funding_id: request.fundingId,
        allocated_amount: request.budget
      }]
  newRequestData.value.public_purchase_plan_id = request.planPosition?.public_purchase_plan_id || null
  newRequestData.value.plan_exception_justification = request.planExceptionJustification || ''
  await fetchFundingPlansForAllocations()
  showAddRequestModal.value = true
}

const handleNewRequest = async () => {
  if (!currentFinanceManagerId.value) return
  try {
    const payload = {
      purchase_request_name: newRequestData.value.purchase_request_name,
      section_name: newRequestData.value.section_name,
      budget_allocated_for_the_order: editingRequestId.value ? allocationTotal.value : 0,
      if_service: newRequestData.value.if_service,
      used_cpv_id: editingRequestId.value ? newRequestData.value.used_cpv_id : null,
      created_at: new Date().toISOString(),
      can_add: newRequestData.value.can_add,
      project_finance_manager_id: currentFinanceManagerId.value,
      funding_allocations: newRequestData.value.funding_allocations,
      public_purchase_plan_id: newRequestData.value.public_purchase_plan_id,
      plan_exception_justification: newRequestData.value.plan_exception_justification
    }
    const requestUrl = editingRequestId.value ? `${API_URL}/purchase_requests/${editingRequestId.value}` : `${API_URL}/create_purchase_requests`
    await fetch(requestUrl, { method: editingRequestId.value ? 'PATCH' : 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
    resetRequestForm()
    showAddRequestModal.value = false
    editingRequestId.value = null
    await Promise.all([fetchRequests(), fetchClosedOrdersForRequests()])
    emit('budget-changed')
  } catch (error) { console.error(error) }
}

const deleteRequest = async (id) => {
  if (!confirm('Czy na pewno chcesz usunąć ten wniosek?')) return
  try {
    const response = await fetch(`${API_URL}/purchase_requests/${id}`, { method: 'DELETE' })
    if (response.ok) {
      allRequests.value = allRequests.value.filter(r => r.id !== id)
      if (activeRequest.value?.id === id) activeRequest.value = null
    }
  } catch (error) { console.error(error) }
}

const formatStatus = (status) => {
  const map = { pending: 'Oczekujący', approved: 'Zatwierdzony', rejected: 'Odrzucony' }
  return map[status] || status
}
const formatPlanStatus = status => status === 'compliant' ? 'Zgodny z planem' : (status === 'requires_approval' ? 'Wymaga zgody' : status || 'Brak danych')
const formatDate = (dateStr) => dateStr ? new Intl.DateTimeFormat('pl-PL').format(new Date(dateStr)) : '—'
const formatMoney = (value) => Number(value || 0).toLocaleString('pl-PL', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

onMounted(async () => {
  await fetchStudentsMap()
  await fetchRequests()
  await fetchClosedOrdersForRequests()
  await fetchFundings()
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;500;600;700;800&display=swap');

.requests-container { display: flex; flex-direction: column; gap: 2vh; }
.requests-section { width: 100%; padding: 2vh 0; font-family: 'Nunito', system-ui, sans-serif; }

.requests-filter-bar { display: flex; justify-content: space-between; align-items: center; gap: 1.5vw; margin-bottom: 3vh; padding: 1vw; background: rgba(15, 23, 42, 0.5); border: 0.08vw solid rgba(148, 163, 184, 0.15); border-radius: 0.8vw; flex-wrap: wrap; }
.filter-group-item { display: flex; align-items: center; gap: 0.5vw; }
.section-filter-dropdown { min-width: 14vw; }

.view-toggle-container { display: flex; background: rgba(30, 41, 59, 0.8); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 0.6vw; padding: 0.2vw; margin-left: auto; }
.toggle-view-btn { background: transparent; border: none; color: #94a3b8; padding: 0.5vw 1.2vw; font-size: 0.85vw; font-weight: 700; border-radius: 0.4vw; cursor: pointer; transition: all 0.2s ease; font-family: inherit; }
.toggle-view-btn--active { background: rgba(59, 130, 246, 0.2); color: #60a5fa; }

.requests-header { margin-bottom: 3vh; display: flex; justify-content: space-between; align-items: center; gap: 2vw; }
.requests-title-section { display: flex; flex-direction: column; gap: 0.5vw; }
.requests-title { font-size: 1.8vw; font-weight: 800; color: #bfdbfe; margin: 0; }
.requests-subtitle { font-size: 0.95vw; color: rgba(226, 232, 240, 0.6); margin: 0; }

.requests-add-button { padding: 0.8vw 1.5vw; background: linear-gradient(135deg, #3b82f6, #2563eb); color: #ffffff; border: none; border-radius: 0.8vw; font-size: 1vw; font-weight: 700; cursor: pointer; transition: all 0.2s ease; box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3); }
.requests-add-button:hover { transform: translateY(-0.2vh); box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4); }

.request-status-group { margin-bottom: 4vh; }
.status-group-title { font-size: 1.2vw; color: #94a3b8; font-weight: 800; text-transform: uppercase; letter-spacing: 0.04em; margin: 0 0 1.5vw 0; border-left: 3px solid #3b82f6; padding-left: 0.6vw; }

.requests-empty { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 5vh; background: rgba(15, 23, 42, 0.4); border: 0.08vw dashed rgba(148, 163, 184, 0.25); border-radius: 1vw; text-align: center; }
.requests-empty--compact { padding: 2.5vh; border-style: solid; background: rgba(15, 23, 42, 0.2); }
.requests-empty-subtext { font-size: 0.9vw; color: rgba(226, 232, 240, 0.4); margin: 0; font-style: italic; }

.requests-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(26vw, 1fr)); gap: 2vw; }
.request-card { display: flex; flex-direction: column; padding: 1.8vw; background: rgba(15, 23, 42, 0.6); border: 0.08vw solid rgba(148, 163, 184, 0.15); border-radius: 1vw; transition: all 0.3s ease; }
.request-card:hover { background: rgba(15, 23, 42, 0.8); border-color: rgba(59, 130, 246, 0.3); transform: translateY(-0.4vh); }
.request-card__header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.5vw; gap: 1vw; }
.request-card__title { font-size: 1.15vw; font-weight: 700; color: #ffffff; margin: 0; flex: 1; }
.request-card__section-badge { display: inline-block; padding: 0.15vw 0.5vw; background: rgba(59, 130, 246, 0.12); color: #60a5fa; border-radius: 0.3vw; font-size: 0.7vw; font-weight: 700; border: 1px solid rgba(59, 130, 246, 0.2); margin-top: 0.4vw; text-transform: uppercase; }

.request-card__badge { padding: 0.4vw 0.8vw; border-radius: 0.4vw; font-size: 0.8vw; font-weight: 700; white-space: nowrap; text-transform: uppercase; text-align: center; }
.request-card__badge.pending { background: rgba(251, 191, 36, 0.15); color: #fcd34d; border: 1px solid rgba(251, 191, 36, 0.25); }
.request-card__badge.approved { background: rgba(34, 197, 94, 0.15); color: #86efac; border: 1px solid rgba(34, 197, 94, 0.25); }
.request-card__badge.rejected { background: rgba(239, 68, 68, 0.15); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.25); }

.request-card__content { flex: 1; display: flex; flex-direction: column; gap: 0.6vw; margin-bottom: 1.5vw; }
.request-card__detail { display: flex; align-items: center; justify-content: space-between; font-size: 0.9vw; margin: 0; }
.request-card__label { color: rgba(226, 232, 240, 0.55); font-weight: 600; }
.request-card__value { color: #ffffff; font-weight: 500; }

.request-card__actions { display: flex; gap: 0.5vw; flex-wrap: wrap; }
.request-card__button { flex: 1; min-width: 5.5vw; padding: 0.6vw; border: none; border-radius: 0.5vw; font-size: 0.85vw; font-weight: 700; cursor: pointer; transition: all 0.2s ease; font-family: inherit; }
.request-card__button.view { background: rgba(59, 130, 246, 0.15); color: #93c5fd; border: 1px solid rgba(59, 130, 246, 0.2); }
.request-card__button.view:hover { background: #2563eb; color: white; border-color: #2563eb; }
.request-card__button.delete { background: rgba(239, 68, 68, 0.12); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.2); }
.request-card__button.delete:hover { background: #dc2626; color: white; border-color: #dc2626; }

.excel-table-wrapper { background: rgba(15, 23, 42, 0.4); border: 1px solid rgba(148, 163, 184, 0.15); border-radius: 0.8vw; overflow-x: auto; width: 100%; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2); margin-bottom: 1vw; }
.excel-list-table { width: 100%; border-collapse: collapse; text-align: left; font-size: 0.85vw; min-width: 1050px; }
.excel-list-table th, .excel-list-table td { padding: 0.9vw 1.2vw; border-bottom: 1px solid rgba(148, 163, 184, 0.1); vertical-align: middle; }
.excel-list-table th { background: rgba(30, 41, 59, 0.8); color: #94a3b8; font-weight: 700; text-transform: uppercase; font-size: 0.75vw; letter-spacing: 0.05em; border-bottom: 2px solid rgba(148, 163, 184, 0.2); }
.excel-list-table tr:hover { background: rgba(59, 130, 246, 0.02); }

.table-section-badge { padding: 0.2vw 0.5vw; background: rgba(245, 158, 11, 0.12); color: #fcd34d; border-radius: 0.4vw; font-weight: 700; font-size: 0.75vw; text-transform: uppercase; }
.text-badge-only { padding: 0.2vw 0.5vw; font-size: 0.75vw; display: inline-block; border-radius: 0.3vw; }
.table-row-actions { display: flex; gap: 0.4vw; }
.table-btn { padding: 0.4vw 0.8vw; border: none; border-radius: 0.4vw; font-size: 0.78vw; font-weight: 700; cursor: pointer; transition: all 0.2s ease; font-family: inherit; }
.table-btn.view { background: rgba(59, 130, 246, 0.15); color: #93c5fd; border: 1px solid rgba(59, 130, 246, 0.2); }
.table-btn.view:hover { background: #2563eb; color: white; }
.table-btn.delete { background: rgba(239, 68, 68, 0.12); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.2); }
.table-btn.delete:hover { background: #dc2626; color: white; }

.sort-label { font-size: 0.8vw; color: #94a3b8; font-weight: 700; text-transform: uppercase; }
.excel-sort-select { background: transparent; border: none; color: #60a5fa; font-size: 0.85vw; font-weight: 700; cursor: pointer; outline: none; font-family: inherit; }
.excel-sort-select option { background: #0f172a; color: #ffffff; }

.request-details__back { margin-bottom: 2vh; background: none; border: none; color: #93c5fd; cursor: pointer; font-size: 1vw; font-family: inherit; font-weight: 700; }
.request-details__card { background: rgba(15, 23, 42, 0.6); border: 0.08vw solid rgba(148, 163, 184, 0.15); border-radius: 1vw; padding: 2vw; }
.request-details__top { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 2vw; }
.request-details__title { color: white; margin: 0; font-size: 1.6vw; font-weight: 800; }
.request-details__subtitle { color: rgba(226, 232, 240, 0.5); margin: 0.5vh 0 0 0; }
.request-details__grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1vw; margin-bottom: 2vw; }
.request-info { background: rgba(30, 41, 59, 0.6); padding: 1vw; border-radius: 0.8vw; }
.request-info p { color: rgba(226, 232, 240, 0.5); margin: 0 0 0.5vh 0; font-size: 0.9vw; }
.request-info strong { color: white; font-size: 1vw; }

.text-blue { color: #60a5fa !important; }
.text-amber { color: #fbbf24 !important; }
.text-white { color: #ffffff !important; }
.text-emerald { color: #34d399 !important; }
.text-muted { color: #64748b !important; }
.font-bold { font-weight: 700; }
.font-mono { font-family: monospace; }

.modal-overlay { position: fixed; inset: 0; background: rgba(5, 8, 22, 0.85); display: flex; justify-content: center; align-items: center; z-index: 1000; backdrop-filter: blur(8px); }
.modal-content { width: 90%; max-width: 35vw; max-height: 85vh; background: #0f172a; border: 0.08vw solid rgba(148, 163, 184, 0.15); border-radius: 1.2vw; padding: 2.2vw; box-sizing: border-box; overflow: hidden; display: flex; flex-direction: column; }
.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2.5vh; flex-shrink: 0; }
.modal-title { font-size: 1.5vw; color: #fff; font-weight: 800; }
.modal-close { background: transparent; border: none; color: rgba(226, 232, 240, 0.6); font-size: 1.4vw; cursor: pointer; transition: color 0.2s; }
.modal-close:hover { color: #ffffff; }

.modal-form { display: flex; flex-direction: column; gap: 1.2vw; overflow-y: auto; flex: 1; padding-right: 0.4vw; }
.modal-form__group { display: flex; flex-direction: column; gap: 0.5vw; }
.modal-form__label { color: #94a3b8; font-size: 0.8vw; font-weight: 700; text-transform: uppercase; letter-spacing: 0.03em; }
.modal-form__input { box-sizing: border-box; padding: 0.8vw 1vw; border-radius: 0.6vw; border: 0.08vw solid rgba(148,163,184,0.2); background: rgba(15,23,42,0.7); color: white; font-size: 0.95vw; outline: none; transition: border-color 0.2s; }
.modal-form__input:focus { border-color: #3b82f6; }

.funding-allocation-row { display: grid; grid-template-columns: 1fr 8vw auto; gap: 0.7vw; align-items: center; }
.funding-allocation-list { display: grid; gap: 0.5vw; margin-top: 0.8vw; }
.funding-allocation-item, .funding-allocation-total { display: grid; grid-template-columns: 1fr auto auto; gap: 0.8vw; align-items: center; padding: 0.75vw; border-radius: 0.6vw; background: rgba(30, 41, 59, 0.62); color: #e2e8f0; }
.funding-allocation-total { grid-template-columns: 1fr auto; background: rgba(59, 130, 246, 0.16); }
.delete-inline-btn { border: 0; background: transparent; color: #fca5a5; cursor: pointer; font-weight: 700; }

.modal-actions { display: flex; justify-content: flex-end; gap: 1vw; margin-top: 2vh; padding-top: 1.5vh; border-top: 0.08vw solid rgba(148,163,184,0.15); flex-shrink: 0; }
.modal-btn { padding: 0.8vw 1.6vw; border-radius: 0.6vw; border: none; cursor: pointer; font-weight: 700; font-family: inherit; }
.modal-btn-cancel { background: rgba(148, 163, 184, 0.12); color: #e2e8f0; }
.modal-btn-cancel:hover { background: rgba(148, 163, 184, 0.25); color: #ffffff; }
.modal-btn-save-add { padding: 0.8vw 1.2vw; border-radius: 0.6vw; background: #1e293b; border: 1px solid #3b82f6; color: #60a5fa; font-weight: 700; cursor: pointer; }
.modal-btn-save { background: linear-gradient(135deg, #3b82f6, #2563eb); color: white; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2); }
.modal-btn-save:not(:disabled):hover { transform: translateY(-1px); box-shadow: 0 66px 16px rgba(37, 99, 235, 0.35); }

.custom-scrollbar::-webkit-scrollbar { height: 7px; width: 6px; background: rgba(30, 41, 59, 0.5); border-radius: 10px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(148, 163, 184, 0.25); border-radius: 10px; }
</style>