<template>
  <div class="dashboard">
    <header class="dashboard__header">
      <div class="dashboard__container">
        <div class="dashboard__header-content">
          <div class="dashboard__logo-section">
            <img src="/logo.png" alt="Logo" class="dashboard__logo" />
            <h1 class="dashboard__title">BudgetFlowFusion</h1>
          </div>
          <nav class="dashboard__nav">
            <button
              v-for="(link, index) in navLinks"
              :key="index"
              class="dashboard__nav-link"
              :class="{ active: activeNavIndex === index }"
              @click="navigateToSection(index)"
            >
              {{ link }}
            </button>
          </nav>
          <div class="dashboard__user-section">
            <div class="dashboard__user-menu" ref="userMenuRef">
              <button
                class="dashboard__user-name"
                @click="showUserMenu = !showUserMenu"
              >
                {{ user.firstName }} {{ user.lastName }}
              </button>
              <div v-if="showUserMenu" class="dashboard__user-dropdown">
                <button class="dashboard__dropdown-item" @click="showEditProfileModal = true"> Edytuj profil </button>
                <button class="dashboard__dropdown-item" @click="handleLogout"> Wyloguj się </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>

    <main class="dashboard__main">
      <div class="dashboard__container">
        <div class="dashboard__sections-container" ref="sectionsContainer" @scroll="handleScroll">
          <section class="dashboard__section" v-if="showPulpit">
            <section class="dashboard__welcome">
              <h2 class="dashboard__welcome-title">
                Cześć {{ user.firstName }}
              </h2>
            </section>

            <div class="dashboard__user-info-card">
              <div class="dashboard__user-info-header">
                <h2 class="dashboard__user-info-title">Moje informacje</h2>
              </div>
              <div class="dashboard__user-info-content">
                <div class="dashboard__user-info-row">
                  <span class="dashboard__user-info-label">Rola</span>
                  <span class="dashboard__user-info-value">{{ user.role === 'member' ? 'Członek koła naukowego' : 'Skarbnik' }}</span>
                </div>
                <div class="dashboard__user-info-row">
                  <span class="dashboard__user-info-label">E-mail</span>
                  <span class="dashboard__user-info-value">{{ user.email }}</span>
                </div>
                <div class="dashboard__user-info-row">
                  <span class="dashboard__user-info-label">Koło naukowe</span>
                  <span class="dashboard__user-info-value">{{ user.circleName }}</span>
                </div>
                <div class="dashboard__user-info-row">
                  <span class="dashboard__user-info-label">Sekcja</span>
                  <span class="dashboard__user-info-value">{{ formatPosition(user.position) }}</span>
                </div>
                <div class="dashboard__user-info-row">
                  <span class="dashboard__user-info-label">SAP</span>
                  <span class="dashboard__user-info-value">{{ user.inSAP ? 'Jestem w SAP' : 'Nie jestem w SAP' }}</span>
                </div>
              </div>
            </div>

            <section class="dashboard__grid">
              <div v-if="user.role === 'treasurer'" class="dashboard__card budget-card">
                <div class="dashboard__card-header">
                  <h3 class="dashboard__card-title"> Przegląd budżetu </h3>
                  <span class="dashboard__card-badge">Na żywo</span>
                </div>
                <div class="dashboard__card-body">
                  <div
                    v-for="stat in budgetStats"
                    :key="stat.label"
                    class="budget-stat"
                  >
                    <p class="budget-stat__label">{{ stat.label }}</p>
                    <p class="budget-stat__value" :class="stat.class">{{ stat.value }}</p>
                  </div>
                  <div class="budget-progress">
                    <div class="budget-progress__bar">
                      <div class="budget-progress__fill" :style="{ width: `${budgetUsagePercent}%` }"></div>
                    </div>
                    <p class="budget-progress__text">{{ budgetUsagePercent.toFixed(1) }}% wykorzystane</p>
                  </div>
                </div>
              </div>
              <div class="dashboard__card actions-card">
                <div class="dashboard__card-header">
                  <h3 class="dashboard__card-title"> Szybki dostęp </h3>
                </div>
                <div class="dashboard__card-body">
                  <button
                    v-for="action in quickActions"
                    :key="action.id"
                    class="dashboard__quick-action"
                    @click="handleQuickAction(action.id)"
                  >
                    <span class="dashboard__quick-action-icon">{{ action.icon }}</span>
                    <span class="dashboard__quick-action-text">{{ action.label }}</span>
                  </button>
                </div>
              </div>
            </section>
          </section>

          <section class="dashboard__section" v-if="!showPulpit && (navLinks[activeNavIndex]?.includes('Dodane') || navLinks[activeNavIndex]?.includes('przedmioty'))">
            <AddedItems />
          </section>

          <section class="dashboard__section" v-if="!showPulpit && (navLinks[activeNavIndex]?.includes('Wnioski') || navLinks[activeNavIndex] === 'Podsumowanie budżetu')">
            <div v-if="navLinks[activeNavIndex] === 'Podsumowanie budżetu'" class="budget-overview">
              <div class="budget-overview__header">
                <div>
                  <p class="budget-overview__eyebrow">Środki koła</p>
                  <h2>Podsumowanie budżetu</h2>
                </div>
                <button class="dashboard__card-link" type="button" @click="fetchBudgetSummary">Odśwież</button>
              </div>

              <div class="budget-overview__stats">
                <div v-for="stat in budgetStats" :key="stat.label" class="budget-overview__stat">
                  <span>{{ stat.label }}</span>
                  <strong :class="stat.class">{{ stat.value }}</strong>
                </div>
              </div>

              <div v-if="budgetProjects.length" class="budget-project-tabs">
                <button
                  v-for="project in budgetProjects"
                  :key="project.project_budget_id"
                  type="button"
                  class="budget-project-tab"
                  :class="{ active: Number(activeBudgetProjectId) === Number(project.project_budget_id) }"
                  @click="activeBudgetProjectId = project.project_budget_id"
                >
                  <span>{{ project.project_name || project.project_budget_name }}</span>
                  <strong>{{ formatBudgetMoney(project.available_after_purchase_requests) }}</strong>
                </button>
              </div>

              <div v-if="activeBudgetProject" class="budget-project-detail">
                <div class="budget-project-detail__top">
                  <div>
                    <p class="budget-overview__eyebrow">Projekt</p>
                    <h3>{{ activeBudgetProject.project_name || activeBudgetProject.project_budget_name }}</h3>
                    <span>{{ activeBudgetProject.project_budget_name }}</span>
                  </div>
                  <div class="budget-project-detail__meter">
                    <div class="budget-progress__bar">
                      <div class="budget-progress__fill" :style="{ width: `${projectUsagePercent(activeBudgetProject)}%` }"></div>
                    </div>
                    <p>{{ projectUsagePercent(activeBudgetProject).toFixed(1) }}% wykorzystane</p>
                  </div>
                </div>

                <div class="budget-project-metrics">
                  <div><span>Budżet projektu</span><strong>{{ formatBudgetMoney(activeBudgetProject.total_budget) }}</strong></div>
                  <div><span>Wydane</span><strong>{{ formatBudgetMoney(activeBudgetProject.spent_money) }}</strong></div>
                  <div><span>Zarezerwowane we wnioskach</span><strong>{{ formatBudgetMoney(activeBudgetProject.purchase_requests_total_allocated) }}</strong></div>
                  <div><span>Pozostało po rezerwacjach</span><strong class="success">{{ formatBudgetMoney(activeBudgetProject.available_after_purchase_requests) }}</strong></div>
                </div>

                <div class="budget-fundings">
                  <div class="budget-fundings__header">
                    <h3>Dofinansowania projektu</h3>
                    <span>{{ activeProjectFundings.length }} pozycji</span>
                  </div>
                  <div class="budget-table-wrap">
                    <table class="budget-table">
                      <thead>
                        <tr>
                          <th>Nazwa</th>
                          <th>Budżet</th>
                          <th>Wydane</th>
                          <th>Zarezerwowane</th>
                          <th>Pozostało</th>
                          <th>Wykorzystanie</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="funding in activeProjectFundings" :key="funding.funding_id">
                          <td>{{ funding.funding_name }}</td>
                          <td>{{ formatBudgetMoney(funding.funding_price) }}</td>
                          <td>{{ formatBudgetMoney(funding.spent_money) }}</td>
                          <td>{{ formatBudgetMoney(funding.purchase_requests_total_allocated) }}</td>
                          <td class="success">{{ formatBudgetMoney(funding.available_after_purchase_requests) }}</td>
                          <td>
                            <div class="budget-table-usage">
                              <div class="budget-progress__bar">
                                <div class="budget-progress__fill" :style="{ width: `${fundingUsagePercent(funding)}%` }"></div>
                              </div>
                              <span>{{ fundingUsagePercent(funding).toFixed(1) }}%</span>
                            </div>
                          </td>
                        </tr>
                        <tr v-if="!activeProjectFundings.length">
                          <td colspan="6" class="budget-table-empty">Brak dofinansowań w tym projekcie.</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>

              <div v-else class="budget-table-empty">Brak projektów budżetowych do wyświetlenia.</div>
            </div>
            <PurchaseRequest
              v-if="navLinks[activeNavIndex]?.includes('Wnioski')"
              @budget-changed="fetchBudgetSummary"
              @open-shopping="openShoppingForRequest"
            />
          </section>

          <section class="dashboard__section" v-if="!showPulpit && navLinks[activeNavIndex] === 'Rozliczenia'">
            <Settlement />
          </section>

          <section class="dashboard__section" v-if="!showPulpit && navLinks[activeNavIndex]?.includes('Listy') && navLinks[activeNavIndex]?.includes('zakupów')">
            <AddedShopPurchaseLists :initial-purchase-request-id="selectedShoppingRequestId" />
          </section>

          <section class="dashboard__section" v-if="!showPulpit && navLinks[activeNavIndex] === 'Sklepy'">
            <Shops />
          </section>

          <section class="dashboard__section" v-if="!showPulpit && navLinks[activeNavIndex] === 'Plany publiczne'">
            <PublicPurchasePlans />
          </section>

          <section class="dashboard__section" v-if="navLinks[activeNavIndex] === 'Akceptacja CPV'">
            <TreasurerValidation />
          </section>
        </div>
      </div>
    </main>

    <div v-if="showEditProfileModal" class="modal-overlay" @click="showEditProfileModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2 class="modal-title">Edytuj profil</h2>
          <button class="modal-close" @click="showEditProfileModal = false">✕</button>
        </div>

        <form class="edit-form" @submit.prevent="handleSaveProfile">
          <div class="edit-form-group">
            <label class="edit-form-label">Imię</label>
            <input
              v-model="editFormData.firstName"
              type="text"
              placeholder="Jan"
              class="edit-form-input"
              required
            />
          </div>

          <div class="edit-form-group">
            <label class="edit-form-label">Nazwisko</label>
            <input
              v-model="editFormData.lastName"
              type="text"
              placeholder="Kowalski"
              class="edit-form-input"
              required
            />
          </div>

          <div class="edit-form-group">
            <label class="edit-form-label">E-mail</label>
            <input
              v-model="editFormData.email"
              type="email"
              placeholder="name@example.com"
              class="edit-form-input"
              required
            />
          </div>

          <div class="edit-form-group">
            <label class="edit-form-label">Sekcja</label>
            <select
              v-model="editFormData.position"
              required
              class="edit-form-select"
            >
              <option value="" disabled>Wybierz sekcję</option>
              <option value="elektronika">Elektronika</option>
              <option value="autonomia">Autonomia</option>
              <option value="mechanika">Mechanika</option>
              <option value="embedded">Embedded</option>
            </select>
          </div>

          <div v-if="user.role === 'treasurer'" class="edit-form__role-toggle">
            <span class="edit-form__role-label">Rola</span>
            <button
              class="edit-form__toggle"
              :class="{ 'is-treasurer': editFormData.role === 'treasurer' }"
              type="button"
              @click="toggleEditRole"
              :disabled="editFormData.role === 'member'"
            >
              <span class="edit-form__toggle-text">
                {{ editFormData.role === 'member' ? 'Zwykły członek koła' : 'Skarbnik' }}
              </span>
              <span class="edit-form__toggle-indicator"></span>
            </button>
            <span v-if="editFormData.role === 'member'" class="edit-form__role-info">
              Po zmianie na zwykłego członka nie będziesz mógł wrócić do roli skarbnika
            </span>
          </div>

          <div class="edit-form__role-toggle">
            <span class="edit-form__role-label">SAP</span>
            <button
              class="edit-form__toggle"
              :class="{ 'is-in-sap': editFormData.inSAP === true }"
              type="button"
              @click="toggleEditSAP"
            >
              <span class="edit-form__toggle-text">
                {{ editFormData.inSAP ? 'Jestem w SAP' : 'Nie jestem w SAP' }}
              </span>
              <span class="edit-form__toggle-indicator"></span>
            </button>
          </div>

          <div class="modal-actions">
            <button type="button" class="modal-btn modal-btn-cancel" @click="showEditProfileModal = false">Anuluj</button>
            <button type="submit" class="modal-btn modal-btn-save">Zapisz zmiany</button>
          </div>
        </form>
      </div>
    </div>
    <AddItemModal
      :isOpen="showAddItemModal"
      @close="showAddItemModal = false"
      @submit-item="handleItemAdded"
    />
    <div v-if="showMembersModal" class="modal-overlay" @click="showMembersModal = false">
      <div class="modal-content members-modal" @click.stop>
        <div class="modal-header">
          <h2 class="modal-title">Członkowie koła</h2>
          <button class="modal-close" @click="showMembersModal = false">✕</button>
        </div>

        <div class="members-list">
          <div v-if="allStudents.length === 0" class="members-empty">
            Brak członków do wyświetlenia.
          </div>
          <div
            v-for="student in allStudents"
            :key="student.id"
            class="member-item"
          >
            <div class="member-item__info">
              <p class="member-item__name">{{ student.name }} {{ student.surname }}</p>
              <p class="member-item__details">
                <span>Sekcja: {{ formatPosition(student.position) }}</span>
                <span>•</span>
                <span :class="{'text-success': student.is_in_sap, 'text-warning': !student.is_in_sap}">
                  SAP: {{ student.is_in_sap ? 'Tak' : 'Nie' }}
                </span>
              </p>
            </div>
          </div>
        </div>

        <div class="modal-actions">
          <button type="button" class="modal-btn modal-btn-cancel" @click="showMembersModal = false">Zamknij</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted, watch } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { useRouter } from 'vue-router'
import AddedItems from '@/components/items_shop_purchase_lists/AddedItems.vue'
import AddedShopPurchaseLists from '@/components/items_shop_purchase_lists/AddedShopPurchaseLists.vue'
import AddItemModal from '@/components/items_shop_purchase_lists/AddItemModal.vue'
import PurchaseRequest from '@/components/purchase_request/PurchaseRequest.vue'
import Settlement from '@/components/settlement/Settlement.vue'
import PublicPurchasePlans from '@/components/public_purchase_plans/PublicPurchasePlans.vue'
import { useToast } from '@/composables/useToast'
import TreasurerValidation from '@/components/items_shop_purchase_lists/TreasurerValidation.vue'
import Shops from '@/components/shops/Shops.vue'

const router = useRouter()
const { user, logout } = useAuth()
const showUserMenu = ref(false)
const showEditProfileModal = ref(false)
const showAddItemModal = ref(false)
const activeNavIndex = ref(0)
const selectedShoppingRequestId = ref(null)
const sectionsContainer = ref(null)
const toast = useToast()
const userMenuRef = ref(null)
const allStudents = ref([])
const showMembersModal = ref(false)
const budgetSummary = ref({
  total_budget: 0,
  spent_money: 0,
  purchase_requests_total_allocated: 0,
  available_after_purchase_requests: 0
})
const projectBudgets = ref([])
const budgetFundings = ref([])
const activeBudgetProjectId = ref(null)

const editFormData = ref({
  firstName: '',
  lastName: '',
  email: '',
  position: '',
  inSAP: false,
  role: ''
})

const baseNavLinks = computed(() => {
  if (user.value?.role === 'member') {
    return ['Pulpit', 'Dodane przedmioty', 'Listy zakupów']
  }
  return ['Pulpit', 'Dodane przedmioty', 'Listy zakupów', 'Podsumowanie budżetu', 'Plany publiczne', 'Wnioski o zamówienie publiczne', 'Rozliczenia', 'Akceptacja CPV']
})

const navLinks = computed(() => {
  const links = baseNavLinks.value
  if (links.includes('Sklepy')) return links
  const insertIndex = links.findIndex(link => link.includes('Listy'))
  if (insertIndex === -1) return [...links, 'Sklepy']
  return [
    ...links.slice(0, insertIndex + 1),
    'Sklepy',
    ...links.slice(insertIndex + 1)
  ]
})

const showPulpit = computed(() => activeNavIndex.value === 0)

const navigateToSection = (index) => {
  activeNavIndex.value = index
  if (sectionsContainer.value) {
    const sectionWidth = sectionsContainer.value.offsetWidth
    sectionsContainer.value.scrollTo({
      left: sectionWidth * index,
      behavior: 'smooth'
    })
  }
}

const openShoppingForRequest = (request) => {
  selectedShoppingRequestId.value = request?.id || null
  const listsIndex = navLinks.value.findIndex(link =>
    link.includes('Listy') && link.includes('zakup')
  )
  if (listsIndex >= 0) {
    navigateToSection(listsIndex)
  }
}

const handleScroll = () => {
  if (sectionsContainer.value) {
    const scrollLeft = sectionsContainer.value.scrollLeft
    const sectionWidth = sectionsContainer.value.offsetWidth
    const newIndex = Math.round(scrollLeft / sectionWidth)
    if (newIndex !== activeNavIndex.value && newIndex >= 0 && newIndex < navLinks.value.length) {
      activeNavIndex.value = newIndex
    }
  }
}

const handleClickOutside = (e) => {
  if (userMenuRef.value && !userMenuRef.value.contains(e.target)) {
    showUserMenu.value = false
  }
}

const resetEditFormData = () => {
  if (user.value) {
    editFormData.value = {
      firstName: user.value.firstName || '',
      lastName: user.value.lastName || '',
      email: user.value.email || '',
      position: user.value.position || '',
      inSAP: user.value.inSAP || false,
      role: user.value.role || 'member'
    }
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  resetEditFormData()
  fetchBudgetSummary()
})

watch(showEditProfileModal, (newValue) => {
  if (newValue) {
    resetEditFormData()
  }
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

const toggleEditRole = () => {
  if (user.value?.role === 'treasurer') {
    editFormData.value.role = editFormData.value.role === 'member' ? 'treasurer' : 'member'
  }
}

const toggleEditSAP = () => {
  editFormData.value.inSAP = !editFormData.value.inSAP
}

const handleSaveProfile = () => {
  if (user.value) {
    user.value.firstName = editFormData.value.firstName
    user.value.lastName = editFormData.value.lastName
    user.value.email = editFormData.value.email
    user.value.position = editFormData.value.position
    user.value.inSAP = editFormData.value.inSAP
    user.value.role = editFormData.value.role

    localStorage.setItem('user', JSON.stringify(user.value))

    showEditProfileModal.value = false
    showUserMenu.value = false
  }
}

const formatBudgetMoney = (value) => `${Number(value || 0).toLocaleString('pl-PL', {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2
})} PLN`

const usedAndReserved = computed(() => (
  Number(budgetSummary.value.spent_money || 0)
  + Number(budgetSummary.value.purchase_requests_total_allocated || 0)
))

const budgetStats = computed(() => [
  { label: 'Budżet całkowity', value: formatBudgetMoney(budgetSummary.value.total_budget), class: '' },
  { label: 'Wydane i zarezerwowane', value: formatBudgetMoney(usedAndReserved.value), class: 'warning' },
  { label: 'Pozostało', value: formatBudgetMoney(budgetSummary.value.available_after_purchase_requests), class: 'success' }
])

const budgetUsagePercent = computed(() => {
  const total = Number(budgetSummary.value.total_budget || 0)
  if (total <= 0) return 0
  return Math.min(100, Math.max(0, (usedAndReserved.value / total) * 100))
})

const budgetProjects = computed(() =>
  projectBudgets.value.map(project => ({
    ...project,
    fundings: budgetFundings.value.filter(
      funding => Number(funding.project_budget_id) === Number(project.project_budget_id)
    )
  }))
)

const activeBudgetProject = computed(() =>
  budgetProjects.value.find(
    project => Number(project.project_budget_id) === Number(activeBudgetProjectId.value)
  ) || budgetProjects.value[0] || null
)

const activeProjectFundings = computed(() =>
  activeBudgetProject.value?.fundings || []
)

const amountUsagePercent = (total, spent, reserved) => {
  const budget = Number(total || 0)
  if (budget <= 0) return 0
  return Math.min(100, Math.max(0, ((Number(spent || 0) + Number(reserved || 0)) / budget) * 100))
}

const projectUsagePercent = project =>
  amountUsagePercent(
    project?.total_budget,
    project?.spent_money,
    project?.purchase_requests_total_allocated
  )

const fundingUsagePercent = funding =>
  amountUsagePercent(
    funding?.funding_price,
    funding?.spent_money,
    funding?.purchase_requests_total_allocated
  )

const fetchBudgetSummary = async () => {
  if (user.value?.role !== 'treasurer' || !user.value?.association_id) return

  try {
    const [summaryResponse, projectsResponse, fundingsResponse] = await Promise.all([
      fetch(
        `http://localhost:8080/api/dashboard/budget_summary?association_id=${user.value.association_id}`,
        { cache: 'no-store' }
      ),
      fetch(
        `http://localhost:8080/api/project_budgets?association_id=${user.value.association_id}`,
        { cache: 'no-store' }
      ),
      fetch(
        `http://localhost:8080/api/fundings?association_id=${user.value.association_id}`,
        { cache: 'no-store' }
      )
    ])
    if (!summaryResponse.ok || !projectsResponse.ok || !fundingsResponse.ok) {
      throw new Error('Nie udalo sie pobrac podsumowania budzetu')
    }
    budgetSummary.value = await summaryResponse.json()
    projectBudgets.value = await projectsResponse.json()
    budgetFundings.value = await fundingsResponse.json()
    if (
      !projectBudgets.value.some(
        project => Number(project.project_budget_id) === Number(activeBudgetProjectId.value)
      )
    ) {
      activeBudgetProjectId.value = projectBudgets.value[0]?.project_budget_id || null
    }
  } catch (error) {
    console.error('Błąd pobierania podsumowania budżetu:', error)
    toast.error('Nie udało się odświeżyć budżetu na pulpicie.')
  }
}

const quickActions = [
  { id: 1, label: 'Dodaj przedmiot' },
  { id: 2, label: 'Dodaj listę zakupów' },
  { id: 3, label: 'Członkowie koła' }
]

const handleQuickAction = (actionId) => {
  if (actionId === 1) {
    showAddItemModal.value = true
  }
  if (actionId === 3) {
    handleCheckMembers()
  }
}

const handleItemAdded = async (itemData) => {
  try {
    const response = await fetch('http://localhost:8080/api/items', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: itemData.name,
        link: itemData.link,
        price: itemData.price,
        currency: itemData.currency,
        product_subcategory_id: itemData.subcategoryId,
        student_id: user.value.id
      })
    })

    if (!response.ok) {
      throw new Error('Nie udało się wysłać przedmiotu do akceptacji')
    }

    if (user.value.role === 'treasurer') {
      toast.success('Przedmiot został automatycznie dodany do katalogu!')
    } else {
      toast.success('Przedmiot został wysłany do akceptacji!')
    }
  } catch (error) {
    console.error('Błąd podczas dodawania przedmiotu:', error)
    toast.error("Wystąpił błąd podczas zapisywania w bazie.")
    alert('Błąd: ' + error.message)
  }
}


const handleCheckMembers = async () => {
  try {
    const response = await fetch(`http://localhost:8080/api/students/`)
    if (!response.ok) {
      throw new Error('Błąd pobierania danych')
    }

    const data = await response.json()
    allStudents.value = data.map(req => ({
      id: req.student_id,
      name: req.name,
      surname: req.surname,
      login: req.login,
      password_hash: req.password_hash,
      position: req.position,
      is_in_sap: req.is_in_sap,
      project_finance_manager_id: req.project_finance_manager_id,
      association_id: req.association_id
    }))
    
    showMembersModal.value = true
  } catch (error) {
    console.error("Wystąpił błąd podczas sprawdzania członków: ", error);
    toast.error("Wystąpił błąd podczas sprawdzania członków")
  }
}


const formatPosition = (position) => {
  if (!position) return 'Nie wybrana'
  const positionNames = {
    'elektronika': 'Elektronika',
    'autonomia': 'Autonomia',
    'mechanika': 'Mechanika',
    'embedded': 'Embedded'
  }
  return positionNames[position] || position
}

const handleLogout = () => {
  logout()
  router.push('/login')
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;500;600;700;800&display=swap');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.dashboard {
  min-height: 100dvh;
  background: #050816;
  color: #ffffff;
  font-family: 'Nunito', system-ui, sans-serif;
}

.dashboard__container {
  max-width: 85vw;
  margin: 0 auto;
  padding: 0 1.5vw;
}

.dashboard__header {
  background: rgba(9, 14, 32, 0.5);
  border-bottom: 0.08vw solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(0.7vw);
  position: sticky;
  top: 0;
  z-index: 100;
  padding: 0.8vh 0;
}

.dashboard__header-content {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 2vw;
}

.dashboard__logo-section {
  display: flex;
  align-items: center;
  gap: 1.5vw;
}

.dashboard__logo {
  width: 3.5vw;
  height: 3.5vw;
  border-radius: 0.5vw;
  object-fit: contain;
}

.dashboard__title {
  font-size: 1.8vw;
  font-weight: 800;
  background: linear-gradient(135deg, #3b82f6, #60a5fa);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.dashboard__nav {
  display: flex;
  gap: 0.5vw;
  justify-content: center;
}

.dashboard__nav-link {
  background: none;
  border: none;
  color: rgba(226, 232, 240, 0.6);
  font-size: 1vw;
  font-weight: 600;
  padding: 0.5vw 1.2vw;
  cursor: pointer;
  border-radius: 0.5vw;
  transition: all 0.2s ease;
  font-family: 'Nunito', system-ui, sans-serif;
}

.dashboard__nav-link:hover {
  color: rgba(226, 232, 240, 0.9);
  background: rgba(59, 130, 246, 0.1);
}

.dashboard__nav-link.active {
  color: #93c5fd;
  background: rgba(59, 130, 246, 0.2);
}

.dashboard__user-section {
  display: flex;
  align-items: center;
  gap: 2vw;
  justify-self: end;
}

.dashboard__user-menu {
  position: relative;
  margin-left: 6vw;
}

.dashboard__user-name {
  background: none;
  border: none;
  font-weight: 600;
  font-size: 1vw;
  color: rgba(226, 232, 240, 0.8);
  cursor: pointer;
  padding: 0.6vw 1.2vw;
  border-radius: 0.5vw;
  transition: all 0.2s ease;
  font-family: 'Nunito', system-ui, sans-serif;
}

.dashboard__user-name:hover {
  color: rgba(226, 232, 240, 0.9);
  background: rgba(59, 130, 246, 0.1);
}

.dashboard__user-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  background: rgba(15, 23, 42, 0.95);
  border: 0.08vw solid rgba(255, 255, 255, 0.1);
  border-radius: 0.5vw;
  min-width: 12vw;
  margin-top: 0.8vw;
  backdrop-filter: blur(0.7vw);
  z-index: 1000;
  overflow: hidden;
}

.dashboard__dropdown-item {
  display: block;
  width: 100%;
  padding: 0.8vw 1.2vw;
  background: none;
  border: none;
  color: rgba(226, 232, 240, 0.8);
  font-size: 0.95vw;
  font-weight: 500;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: 'Nunito', system-ui, sans-serif;
}

.dashboard__dropdown-item:hover {
  background: rgba(59, 130, 246, 0.2);
  color: rgba(226, 232, 240, 1);
}

.dashboard__logout-btn {
  background: rgba(239, 68, 68, 0.15);
  border: 0.08vw solid rgba(239, 68, 68, 0.3);
  color: #fca5a5;
  padding: 0.6vw 1.5vw;
  border-radius: 0.5vw;
  font-weight: 600;
  font-size: 0.95vw;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: 'Nunito', system-ui, sans-serif;
}

.dashboard__logout-btn:hover {
  background: rgba(239, 68, 68, 0.25);
  border-color: rgba(239, 68, 68, 0.5);
}

.dashboard__main {
  padding: 6vh 0 2vh 0;
}

.dashboard__welcome {
  margin-bottom: 1vh;
  margin-top: 3vh;
}

.dashboard__welcome-title {
  font-size: 2.5vw;
  font-weight: 800;
  margin-bottom: 6vh;
  color: #bfdbfe;
}

.highlight {
  color: #93c5fd;
  font-weight: 700;
}

.dashboard__info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(18vw, 1fr));
  gap: 1.5vw;
  margin-bottom: 3vh;
}

.dashboard__info-card {
  display: flex;
  gap: 1.5vw;
  padding: 1.8vw;
  background: rgba(15, 23, 42, 0.6);
  border: 0.08vw solid rgba(148, 163, 184, 0.15);
  border-radius: 1vw;
  transition: all 0.3s ease;
}

.dashboard__info-card:hover {
  background: rgba(15, 23, 42, 0.8);
  border-color: rgba(59, 130, 246, 0.3);
}

.dashboard__user-info-card {
  padding: 2.5vw;
  background: rgba(15, 23, 42, 0.6);
  border: 0.08vw solid rgba(148, 163, 184, 0.15);
  border-radius: 1.2vw;
  margin-bottom: 3vh;
  transition: all 0.3s ease;
}

.dashboard__user-info-card:hover {
  background: rgba(15, 23, 42, 0.8);
  border-color: rgba(59, 130, 246, 0.3);
}

.dashboard__user-info-header {
  margin-bottom: 2vw;
  padding-bottom: 1.5vw;
  border-bottom: 0.08vw solid rgba(148, 163, 184, 0.2);
}

.dashboard__user-info-title {
  font-size: 1.3vw;
  font-weight: 700;
  color: #bfdbfe;
  margin: 0;
}

.dashboard__user-info-content {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.2vw;
}

.dashboard__user-info-row {
  display: flex;
  align-items: center;
  gap: 1.2vw;
  padding: 1vw;
  background: rgba(59, 130, 246, 0.08);
  border-radius: 0.8vw;
  transition: all 0.2s ease;
}

.dashboard__user-info-row:hover {
  background: rgba(59, 130, 246, 0.15);
}

.dashboard__user-info-label {
  font-weight: 600;
  color: rgba(226, 232, 240, 0.7);
  font-size: 1vw;
  min-width: 8vw;
}

.dashboard__user-info-value {
  color: #ffffff;
  font-weight: 500;
  font-size: 1vw;
}

.dashboard__card-icon {
  font-size: 2.5vw;
}

.dashboard__card-content {
  flex: 1;
}

.dashboard__card-label {
  font-size: 0.8vw;
  color: rgba(226, 232, 240, 0.6);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.4vh;
}

.dashboard__card-value {
  font-size: 1.1vw;
  font-weight: 600;
  color: #bfdbfe;
}

.dashboard__grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(25vw, 1fr));
  gap: 2vw;
  margin-bottom: 3vh;
}

.dashboard__grid .actions-card:only-child {
  max-width: 26.4vw;
}

.dashboard__card {
  background: rgba(15, 23, 42, 0.5);
  border: 0.08vw solid rgba(148, 163, 184, 0.15);
  border-radius: 1.2vw;
  overflow: hidden;
  transition: all 0.3s ease;
}

.dashboard__card:hover {
  background: rgba(15, 23, 42, 0.7);
  border-color: rgba(59, 130, 246, 0.3);
}

.dashboard__card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5vw;
  border-bottom: 0.08vw solid rgba(148, 163, 184, 0.1);
}

.dashboard__card-title {
  font-size: 1.3vw;
  font-weight: 700;
  color: #bfdbfe;
}

.dashboard__card-badge {
  background: rgba(59, 130, 246, 0.2);
  color: #93c5fd;
  padding: 0.4vw 0.8vw;
  border-radius: 0.4vw;
  font-size: 0.7vw;
  font-weight: 600;
  text-transform: uppercase;
}

.dashboard__card-link {
  background: none;
  border: none;
  color: #93c5fd;
  font-weight: 600;
  font-size: 0.95vw;
  cursor: pointer;
  transition: color 0.2s ease;
  font-family: 'Nunito', system-ui, sans-serif;
}

.dashboard__card-link:hover {
  color: #bfdbfe;
}

.dashboard__card-body {
  padding: 1.5vw;
}

.budget-stat {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.2vw 0;
  border-bottom: 0.08vw solid rgba(148, 163, 184, 0.1);
}

.budget-stat:last-of-type {
  border-bottom: none;
}

.budget-stat__label {
  color: rgba(226, 232, 240, 0.7);
  font-size: 1vw;
}

.budget-stat__value {
  font-size: 1.6vw;
  font-weight: 700;
  color: #bfdbfe;
}

.budget-stat__value.warning {
  color: #fbbf24;
}

.budget-stat__value.success {
  color: #86efac;
}

.budget-progress {
  margin-top: 1.5vw;
}

.budget-progress__bar {
  width: 100%;
  height: 0.6vh;
  background: rgba(148, 163, 184, 0.2);
  border-radius: 9999vw;
  overflow: hidden;
  margin-bottom: 0.5vh;
}

.budget-progress__fill {
  height: 100%;
  background: linear-gradient(90deg, #fbbf24, #f59e0b);
  border-radius: 9999vw;
  transition: width 0.3s ease;
}

.budget-progress__text {
  font-size: 0.9vw;
  color: rgba(226, 232, 240, 0.6);
}

.budget-overview {
  display: grid;
  gap: 1.4vw;
  color: #e2e8f0;
}

.budget-overview__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1.5vw;
  padding: 1.4vw 0 1.2vw;
  border-bottom: 0.08vw solid rgba(148, 163, 184, 0.16);
}

.budget-overview__header h2,
.budget-project-detail__top h3,
.budget-fundings__header h3 {
  margin: 0;
  color: #ffffff;
  font-size: 1.45vw;
  font-weight: 800;
}

.budget-overview__eyebrow {
  margin: 0 0 0.35vw 0;
  color: #93c5fd;
  font-size: 0.78vw;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.budget-overview__stats,
.budget-project-metrics {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1vw;
}

.budget-overview__stat,
.budget-project-metrics > div {
  display: grid;
  gap: 0.45vw;
  padding: 1vw;
  border: 0.08vw solid rgba(148, 163, 184, 0.16);
  border-radius: 0.8vw;
  background: rgba(15, 23, 42, 0.58);
}

.budget-overview__stat span,
.budget-project-metrics span {
  color: rgba(226, 232, 240, 0.66);
  font-size: 0.85vw;
}

.budget-overview__stat strong,
.budget-project-metrics strong {
  color: #bfdbfe;
  font-size: 1.12vw;
}

.budget-overview .warning {
  color: #fbbf24;
}

.budget-overview .success {
  color: #86efac;
}

.budget-project-tabs {
  display: flex;
  gap: 0.7vw;
  overflow-x: auto;
  padding-bottom: 0.3vw;
}

.budget-project-tab {
  flex: 0 0 16vw;
  display: grid;
  gap: 0.4vw;
  text-align: left;
  padding: 0.9vw 1vw;
  border: 0.08vw solid rgba(148, 163, 184, 0.18);
  border-radius: 0.7vw;
  background: rgba(15, 23, 42, 0.56);
  color: #e2e8f0;
  cursor: pointer;
  font-family: 'Nunito', system-ui, sans-serif;
}

.budget-project-tab.active {
  border-color: rgba(96, 165, 250, 0.65);
  background: rgba(59, 130, 246, 0.18);
}

.budget-project-tab span {
  font-size: 0.9vw;
  font-weight: 800;
}

.budget-project-tab strong {
  color: #86efac;
  font-size: 0.88vw;
}

.budget-project-detail {
  display: grid;
  gap: 1.2vw;
}

.budget-project-detail__top {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 22vw;
  gap: 2vw;
  align-items: end;
  padding: 1.2vw;
  border: 0.08vw solid rgba(148, 163, 184, 0.16);
  border-radius: 0.9vw;
  background: rgba(15, 23, 42, 0.54);
}

.budget-project-detail__top span,
.budget-project-detail__meter p,
.budget-fundings__header span {
  margin: 0;
  color: rgba(226, 232, 240, 0.62);
  font-size: 0.88vw;
}

.budget-fundings {
  display: grid;
  gap: 0.8vw;
}

.budget-fundings__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.budget-table-wrap {
  overflow-x: auto;
  border: 0.08vw solid rgba(148, 163, 184, 0.16);
  border-radius: 0.8vw;
}

.budget-table {
  width: 100%;
  min-width: 860px;
  border-collapse: collapse;
  background: rgba(15, 23, 42, 0.5);
}

.budget-table th,
.budget-table td {
  padding: 0.85vw 1vw;
  border-bottom: 0.08vw solid rgba(148, 163, 184, 0.12);
  text-align: left;
  font-size: 0.9vw;
}

.budget-table th {
  color: #93c5fd;
  font-size: 0.78vw;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  background: rgba(30, 41, 59, 0.72);
}

.budget-table-usage {
  display: grid;
  grid-template-columns: minmax(8vw, 1fr) 4vw;
  gap: 0.7vw;
  align-items: center;
}

.budget-table-empty {
  padding: 1.2vw;
  color: rgba(226, 232, 240, 0.65);
  text-align: center;
}

.transaction-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.2vw 0;
  border-bottom: 0.08vw solid rgba(148, 163, 184, 0.1);
}

.transaction-item:last-of-type {
  border-bottom: none;
}

.transaction-item__info {
  flex: 1;
}

.transaction-item__title {
  font-weight: 600;
  font-size: 1vw;
  color: #bfdbfe;
  margin-bottom: 0.3vh;
}

.transaction-item__date {
  font-size: 0.85vw;
  color: rgba(226, 232, 240, 0.6);
}

.transaction-item__amount {
  font-weight: 700;
  color: #fca5a5;
  font-size: 1.1vw;
}

.transaction-item__amount.success-text {
  color: #86efac;
}

.dashboard__btn-secondary {
  width: 100%;
  margin-top: 1.2vw;
  padding: 1vw;
  background: rgba(59, 130, 246, 0.15);
  border: 0.08vw solid rgba(59, 130, 246, 0.3);
  color: #93c5fd;
  border-radius: 0.8vw;
  font-weight: 600;
  font-size: 0.95vw;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: 'Nunito', system-ui, sans-serif;
}

.dashboard__btn-secondary:hover {
  background: rgba(59, 130, 246, 0.25);
  border-color: rgba(59, 130, 246, 0.5);
}

.dashboard__quick-action {
  display: flex;
  align-items: center;
  gap: 1vw;
  width: 100%;
  padding: 1.3vw;
  background: rgba(59, 130, 246, 0.1);
  border: 0.08vw solid rgba(59, 130, 246, 0.2);
  color: #bfdbfe;
  border-radius: 0.8vw;
  font-weight: 600;
  font-size: 1vw;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: 'Nunito', system-ui, sans-serif;
  margin-bottom: 0.9vw;
}

.dashboard__quick-action:last-child {
  margin-bottom: 0;
}

.dashboard__quick-action:hover {
  background: rgba(59, 130, 246, 0.2);
  border-color: rgba(59, 130, 246, 0.4);
}

.dashboard__quick-action-icon {
  font-size: 1.4vw;
}

.dashboard__quick-action-text {
  font-size: 1vw;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.2vw 0;
  border-bottom: 0.08vw solid rgba(148, 163, 184, 0.1);
}

.stat-row:last-child {
  border-bottom: none;
}

.stat-row__label {
  color: rgba(226, 232, 240, 0.7);
  font-size: 1vw;
}

.stat-row__value {
  font-size: 1.4vw;
  font-weight: 700;
  color: #bfdbfe;
}

@media (max-width: 1024px) {
  .dashboard__header-content {
    grid-template-columns: 1fr;
    gap: 1.5vw;
  }

  .dashboard__nav {
    order: 3;
    grid-column: 1 / -1;
    justify-content: flex-start;
    overflow-x: auto;
  }

  .dashboard__user-section {
    justify-self: auto;
  }

  .dashboard__grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .dashboard__container {
    padding: 0 1.5vw;
  }

  .dashboard__header {
    padding: 0.6vh 0;
  }

  .dashboard__header-content {
    gap: 1vw;
  }

  .dashboard__title {
    font-size: 1.8vw;
  }

  .dashboard__nav {
    overflow-x: auto;
    gap: 0.3vw;
  }

  .dashboard__nav-link {
    font-size: 0.8vw;
    padding: 0.4vw 0.8vw;
    white-space: nowrap;
  }

  .dashboard__welcome-title {
    font-size: 2vw;
  }

  .dashboard__info-grid {
    grid-template-columns: 1fr;
    gap: 1vw;
    margin-bottom: 2vh;
  }

  .dashboard__card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1vw;
  }

  .dashboard__user-name {
    display: none;
  }
}

.dashboard__sections-container {
  display: flex;
  overflow-x: auto;
  scroll-behavior: smooth;
  gap: 0;
  width: 100%;
  scrollbar-width: none;
  -ms-overflow-style: none;
  margin: 0;
  padding: 0;
}

.dashboard__sections-container::-webkit-scrollbar {
  display: none;
}

.dashboard__section {
  flex: 0 0 100%;
  width: 100%;
  max-width: 100%;
  min-width: 100%;
  padding: 0;
  overflow-y: auto;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: #1e293b;
  border: 0.1vw solid rgba(59, 130, 246, 0.2);
  border-radius: 1.2vw;
  padding: 2.5vw;
  max-width: 45vw;
  width: 90%;
  max-height: 85vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.modal-content::-webkit-scrollbar {
  display: none;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2vw;
  padding-bottom: 1.5vw;
  border-bottom: 0.1vw solid rgba(59, 130, 246, 0.2);
}

.modal-title {
  font-size: 1.6vw;
  font-weight: 700;
  color: #e2e8f0;
}

.modal-close {
  background: none;
  border: none;
  color: rgba(226, 232, 240, 0.7);
  font-size: 1.6vw;
  cursor: pointer;
  padding: 0;
  width: 2vw;
  height: 2vw;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s ease;
}

.modal-close:hover {
  color: #e2e8f0;
}

.edit-form-group {
  margin-bottom: 1.5vw;
}

.edit-form-label {
  display: block;
  margin-bottom: 0.6vw;
  color: #bfdbfe;
  font-size: 0.95vw;
  font-weight: 600;
}

.edit-form-input {
  width: 100%;
  padding: 0.8vw;
  background: rgba(30, 41, 59, 0.8);
  border: 0.08vw solid rgba(59, 130, 246, 0.3);
  border-radius: 0.6vw;
  color: #e2e8f0;
  font-size: 0.95vw;
  font-family: 'Nunito', system-ui, sans-serif;
  transition: all 0.2s ease;
}

.edit-form-input:focus {
  outline: none;
  border-color: rgba(59, 130, 246, 0.6);
  background: rgba(30, 41, 59, 0.95);
}

.edit-form-select {
  width: 100%;
  padding: 0.8vw;
  background: rgba(30, 41, 59, 0.8);
  border: 0.08vw solid rgba(59, 130, 246, 0.3);
  border-radius: 0.6vw;
  color: #e2e8f0;
  font-size: 0.95vw;
  font-family: 'Nunito', system-ui, sans-serif;
  transition: all 0.2s ease;
}

.edit-form-select:focus {
  outline: none;
  border-color: rgba(59, 130, 246, 0.6);
  background: rgba(30, 41, 59, 0.95);
}

.edit-form-checkbox {
  display: flex;
  align-items: center;
  gap: 0.8vw;
}

.edit-form-checkbox input {
  width: 1.2vw;
  height: 1.2vw;
  cursor: pointer;
  accent-color: #3b82f6;
}

.edit-form-checkbox label {
  margin: 0;
  cursor: pointer;
  color: #bfdbfe;
}

.edit-form__role-toggle {
  display: flex;
  flex-direction: column;
  gap: 0.6vw;
  margin-bottom: 1.5vw;
}

.edit-form__role-label {
  font-weight: 700;
  font-size: 0.95vw;
  color: #e2e8f0;
  font-family: 'Nunito', system-ui, sans-serif;
}

.edit-form__toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 0.9vw 1.2vw;
  border: 1px solid rgba(148, 163, 184, 0.22);
  border-radius: 0.9vw;
  background: rgba(15, 23, 42, 0.68);
  color: #ffffff;
  font-family: 'Nunito', system-ui, sans-serif;
  font-size: 0.95vw;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.edit-form__toggle:hover {
  border-color: rgba(96, 165, 250, 0.5);
  background: rgba(15, 23, 42, 0.85);
}

.edit-form__toggle.is-treasurer {
  border-color: rgba(96, 165, 250, 0.9);
  background: rgba(59, 130, 246, 0.15);
}

.edit-form__toggle.is-in-sap {
  border-color: rgba(34, 197, 94, 0.9);
  background: rgba(34, 197, 94, 0.15);
}

.edit-form__toggle.is-in-sap .edit-form__toggle-indicator {
  background: linear-gradient(135deg, #22c55e, #16a34a);
}

.edit-form__toggle-text {
  flex: 1;
  text-align: left;
}

.edit-form__toggle-indicator {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.5vw;
  height: 1.5vw;
  margin-left: 0.8vw;
  border-radius: 0.4vw;
  background: rgba(96, 165, 250, 0.3);
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.edit-form__toggle.is-treasurer .edit-form__toggle-indicator {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
}

.edit-form__toggle-indicator::after {
  content: '↔';
  color: #ffffff;
  font-size: 0.95vw;
  font-weight: bold;
}

.edit-form__toggle:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.edit-form__role-info {
  display: block;
  margin-top: 0.5vw;
  font-size: 0.85vw;
  color: #fbbf24;
  font-style: italic;
}

.modal-actions {
  display: flex;
  gap: 1vw;
  justify-content: flex-end;
  margin-top: 2.5vw;
  padding-top: 1.5vw;
  border-top: 0.1vw solid rgba(59, 130, 246, 0.2);
}

.modal-btn {
  padding: 0.8vw 1.6vw;
  border: 0.1vw solid rgba(59, 130, 246, 0.3);
  border-radius: 0.6vw;
  font-size: 0.95vw;
  font-weight: 600;
  cursor: pointer;
  font-family: 'Nunito', system-ui, sans-serif;
  transition: all 0.2s ease;
}

.modal-btn-cancel {
  background: rgba(59, 130, 246, 0.1);
  color: #bfdbfe;
}

.modal-btn-cancel:hover {
  background: rgba(59, 130, 246, 0.2);
  border-color: rgba(59, 130, 246, 0.5);
}


.members-modal {
  max-width: 35vw;
}

.members-list {
  display: flex;
  flex-direction: column;
  gap: 1vw;
  max-height: 50vh;
  overflow-y: auto;
  padding-right: 0.5vw;
  scrollbar-width: thin;
  scrollbar-color: rgba(59, 130, 246, 0.5) rgba(15, 23, 42, 0.5);
}

.members-list::-webkit-scrollbar {
  width: 0.4vw;
}

.members-list::-webkit-scrollbar-track {
  background: rgba(15, 23, 42, 0.5);
  border-radius: 0.2vw;
}

.members-list::-webkit-scrollbar-thumb {
  background: rgba(59, 130, 246, 0.5);
  border-radius: 0.2vw;
}

.members-empty {
  text-align: center;
  color: rgba(226, 232, 240, 0.6);
  padding: 2vw;
  font-size: 0.95vw;
}

.member-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1vw 1.2vw;
  background: rgba(30, 41, 59, 0.8);
  border: 0.08vw solid rgba(59, 130, 246, 0.2);
  border-radius: 0.8vw;
  transition: all 0.2s ease;
}

.member-item:hover {
  background: rgba(30, 41, 59, 0.95);
  border-color: rgba(59, 130, 246, 0.4);
}

.member-item__name {
  font-weight: 700;
  font-size: 1.05vw;
  color: #e2e8f0;
  margin-bottom: 0.3vh;
}

.member-item__details {
  font-size: 0.85vw;
  color: rgba(226, 232, 240, 0.6);
  display: flex;
  gap: 0.5vw;
  align-items: center;
}

.text-success {
  color: #86efac;
}

.text-warning {
  color: #fbbf24;
}

@media (max-width: 1024px) {
  .members-modal {
    max-width: 55vw;
  }
}

@media (max-width: 640px) {
  .members-modal {
    max-width: 90vw;
  }
  
  .member-item__name {
    font-size: 1.2vw;
  }
  
  .member-item__details {
    font-size: 1vw;
  }
}

.modal-btn-save {
  background: #3b82f6;
  color: #fff;
  border-color: #3b82f6;
}

.modal-btn-save:hover {
  background: #60a5fa;
  border-color: #60a5fa;
}

@media (max-width: 1024px) {
  .modal-content {
    max-width: 55vw;
  }
}

@media (max-width: 640px) {
  .modal-content {
    max-width: 90vw;
    padding: 1.5vw;
  }

  .modal-title {
    font-size: 1.4vw;
  }

  .edit-form-group {
    margin-bottom: 1.2vw;
  }

  .edit-form-label {
    font-size: 0.9vw;
  }

  .edit-form-input,
  .edit-form-select {
    font-size: 0.9vw;
    padding: 0.7vw;
  }

  .modal-actions {
    flex-direction: column;
  }

  .modal-btn {
    width: 100%;
  }
}

@media (min-width: 1280px) {
  .dashboard__container {
    width: min(100% - 48px, 1480px);
    max-width: 1480px;
    padding: 0;
  }

  .dashboard__header {
    padding: 10px 0;
    border-bottom-width: 1px;
    backdrop-filter: blur(12px);
  }

  .dashboard__header-content {
    gap: 28px;
  }

  .dashboard__logo-section {
    gap: 18px;
  }

  .dashboard__logo {
    width: 48px;
    height: 48px;
    border-radius: 8px;
  }

  .dashboard__title {
    font-size: clamp(24px, 1.25vw, 32px);
  }

  .dashboard__nav {
    gap: 8px;
  }

  .dashboard__nav-link,
  .dashboard__user-name,
  .dashboard__dropdown-item,
  .dashboard__card-link {
    font-size: 15px;
  }

  .dashboard__nav-link {
    padding: 9px 16px;
    border-radius: 8px;
  }

  .dashboard__main {
    padding: 48px 0 32px;
  }

  .dashboard__welcome {
    margin: 24px 0 28px;
  }

  .dashboard__welcome-title {
    font-size: clamp(32px, 2vw, 42px);
    margin-bottom: 28px;
  }

  .dashboard__user-info-card,
  .dashboard__card,
  .budget-project-detail__top {
    border-radius: 14px;
    border-width: 1px;
  }

  .dashboard__user-info-card {
    padding: 30px;
    margin-bottom: 28px;
  }

  .dashboard__user-info-title,
  .dashboard__card-title,
  .budget-overview__header h2,
  .budget-project-detail__top h3,
  .budget-fundings__header h3 {
    font-size: 22px;
  }

  .dashboard__user-info-content {
    gap: 14px;
  }

  .dashboard__user-info-row {
    gap: 16px;
    padding: 14px 16px;
    border-radius: 10px;
  }

  .dashboard__user-info-label,
  .dashboard__user-info-value,
  .budget-stat__label {
    font-size: 16px;
  }

  .dashboard__grid {
    grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
    gap: 24px;
  }

  .dashboard__card-header,
  .dashboard__card-body {
    padding: 22px;
  }

  .dashboard__card-badge {
    padding: 6px 10px;
    border-radius: 6px;
    font-size: 11px;
  }

  .budget-stat {
    padding: 16px 0;
  }

  .budget-stat__value {
    font-size: 26px;
  }

  .budget-progress {
    margin-top: 20px;
  }

  .budget-progress__bar {
    height: 7px;
    margin-bottom: 8px;
  }

  .budget-progress__text,
  .budget-overview__stat span,
  .budget-project-metrics span,
  .budget-project-detail__top span,
  .budget-project-detail__meter p,
  .budget-fundings__header span,
  .budget-table th,
  .budget-table td {
    font-size: 14px;
  }

  .budget-overview {
    gap: 22px;
  }

  .budget-overview__header {
    padding: 22px 0 18px;
  }

  .budget-overview__stats,
  .budget-project-metrics {
    gap: 16px;
  }

  .budget-overview__stat,
  .budget-project-metrics > div {
    gap: 8px;
    padding: 18px;
    border-radius: 10px;
    border-width: 1px;
  }

  .budget-overview__stat strong,
  .budget-project-metrics strong {
    font-size: 18px;
  }

  .budget-project-tabs {
    gap: 10px;
  }

  .budget-project-tab {
    flex-basis: 240px;
    gap: 8px;
    padding: 16px;
    border-radius: 10px;
    border-width: 1px;
  }

  .budget-project-tab span,
  .budget-project-tab strong {
    font-size: 14px;
  }

  .budget-project-detail {
    gap: 18px;
  }

  .budget-project-detail__top {
    grid-template-columns: minmax(0, 1fr) 320px;
    gap: 28px;
    padding: 22px;
  }

  .budget-table th,
  .budget-table td {
    padding: 14px 16px;
  }

  .modal-content {
    max-width: min(720px, 90vw);
    padding: 32px;
    border-radius: 16px;
    border-width: 1px;
  }

  .members-modal {
    max-width: min(560px, 90vw);
  }
}

@media (min-width: 1800px) {
  .dashboard__container {
    max-width: 1540px;
  }
}

@media (max-width: 900px) {
  .dashboard__container {
    width: min(100% - 28px, 100%);
    max-width: none;
    padding: 0;
  }

  .dashboard__header {
    padding: 10px 0;
  }

  .dashboard__header-content {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .dashboard__logo-section {
    gap: 12px;
  }

  .dashboard__logo {
    width: 42px;
    height: 42px;
    border-radius: 8px;
  }

  .dashboard__title {
    font-size: 24px;
  }

  .dashboard__nav {
    width: 100%;
    justify-content: flex-start;
    overflow-x: auto;
    gap: 8px;
    padding-bottom: 4px;
  }

  .dashboard__nav-link {
    flex: 0 0 auto;
    font-size: 14px;
    padding: 9px 12px;
    border-radius: 8px;
  }

  .dashboard__user-section {
    justify-content: flex-start;
  }

  .dashboard__user-name {
    display: inline-flex;
    font-size: 14px;
    padding: 8px 12px;
    border-radius: 8px;
  }

  .dashboard__main {
    padding: 18px 0 26px;
  }

  .dashboard__welcome {
    margin: 14px 0 16px;
  }

  .dashboard__welcome-title {
    font-size: 28px;
    margin-bottom: 18px;
  }

  .dashboard__user-info-card,
  .dashboard__card {
    padding: 18px;
    border-radius: 12px;
  }

  .dashboard__user-info-card {
    margin-bottom: 18px;
  }

  .dashboard__user-info-header {
    margin-bottom: 16px;
    padding-bottom: 14px;
  }

  .dashboard__user-info-title,
  .dashboard__card-title,
  .budget-overview__header h2,
  .budget-project-detail__top h3,
  .budget-fundings__header h3 {
    font-size: 20px;
  }

  .dashboard__user-info-row {
    display: grid;
    gap: 5px;
    padding: 12px;
    border-radius: 10px;
  }

  .dashboard__user-info-label,
  .dashboard__user-info-value,
  .budget-stat__label {
    min-width: 0;
    font-size: 15px;
  }

  .dashboard__grid,
  .budget-overview__stats,
  .budget-project-metrics {
    grid-template-columns: 1fr;
    gap: 14px;
  }

  .dashboard__card-header,
  .dashboard__card-body {
    padding: 0;
  }

  .dashboard__card-header {
    margin-bottom: 14px;
    border-bottom: 0;
  }

  .budget-stat {
    padding: 12px 0;
  }

  .budget-stat__value {
    font-size: 22px;
  }

  .budget-overview {
    gap: 16px;
  }

  .budget-overview__header {
    display: grid;
    gap: 12px;
    padding: 14px 0;
  }

  .budget-overview__eyebrow {
    font-size: 12px;
  }

  .budget-overview__stat,
  .budget-project-metrics > div,
  .budget-project-detail__top {
    padding: 14px;
    border-radius: 10px;
  }

  .budget-overview__stat span,
  .budget-project-metrics span,
  .budget-project-detail__top span,
  .budget-project-detail__meter p {
    font-size: 14px;
  }

  .budget-overview__stat strong,
  .budget-project-metrics strong {
    font-size: 17px;
  }

  .budget-project-tab {
    flex-basis: 220px;
    padding: 13px;
    border-radius: 9px;
  }

  .budget-project-tab span,
  .budget-project-tab strong,
  .budget-table th,
  .budget-table td {
    font-size: 14px;
  }

  .budget-project-detail__top {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .budget-table {
    min-width: 760px;
  }

  .budget-table th,
  .budget-table td {
    padding: 12px;
  }

  .modal-content,
  .members-modal {
    width: min(100% - 28px, 720px);
    max-width: none;
    padding: 22px;
    border-radius: 14px;
  }

  .modal-title {
    font-size: 22px;
  }
}

@media (max-width: 520px) {
  .dashboard__container {
    width: min(100% - 20px, 100%);
  }

  .dashboard__header {
    position: sticky;
  }

  .dashboard__logo {
    width: 36px;
    height: 36px;
  }

  .dashboard__title {
    font-size: 20px;
  }

  .dashboard__nav-link,
  .dashboard__user-name,
  .dashboard__card-link {
    font-size: 13px;
  }

  .dashboard__welcome-title {
    font-size: 24px;
  }

  .dashboard__user-info-card,
  .dashboard__card {
    padding: 14px;
  }

  .dashboard__user-info-title,
  .dashboard__card-title,
  .budget-overview__header h2,
  .budget-project-detail__top h3,
  .budget-fundings__header h3 {
    font-size: 18px;
  }

  .budget-stat__value {
    font-size: 20px;
  }

  .budget-fundings__header {
    display: grid;
    gap: 4px;
  }

  .budget-project-tab {
    flex-basis: 190px;
  }

  .modal-content,
  .members-modal {
    width: calc(100vw - 20px);
    max-height: 88dvh;
    padding: 18px;
  }

  .modal-actions {
    flex-direction: column;
  }

  .modal-btn,
  .modal-btn-save,
  .modal-btn-cancel {
    width: 100%;
    min-height: 42px;
    font-size: 14px;
  }

  .edit-form-label,
  .edit-form-input,
  .edit-form-select,
  .member-item__name,
  .member-item__details {
    font-size: 14px;
  }

  .edit-form-input,
  .edit-form-select {
    padding: 10px;
    border-radius: 8px;
  }

  .dashboard__section :deep(.modal-content),
  .dashboard__section :deep(.cpv-modal-content) {
    width: calc(100vw - 20px);
    max-width: none;
    max-height: 88dvh;
    padding: 18px;
    border-radius: 14px;
  }

  .dashboard__section :deep(.modal-title),
  .dashboard__section :deep(h2),
  .dashboard__section :deep(h3) {
    font-size: 18px;
  }

  .dashboard__section :deep(.modal-form__input),
  .dashboard__section :deep(input),
  .dashboard__section :deep(select),
  .dashboard__section :deep(textarea),
  .dashboard__section :deep(button) {
    font-size: 14px;
  }

  .dashboard__section :deep(.excel-table-wrapper),
  .dashboard__section :deep(.budget-table-wrap) {
    overflow-x: auto;
  }

  .dashboard__section :deep(.excel-list-table),
  .dashboard__section :deep(table) {
    min-width: 720px;
  }
}
</style>
