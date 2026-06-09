<template>
  <div class="public-plans-section">
    <div class="public-plans-header">
      <div>
        <h2 class="public-plans-title">Listy planów publicznych</h2>
        <p class="public-plans-subtitle">
          Spinaj listy planów publicznych z budżetami koła i dofinansowaniami.
        </p>
      </div>
      <button class="public-plans-refresh" type="button" @click="loadBudgets">
        Odśwież
      </button>
    </div>

    <div v-if="loading" class="public-plans-empty">
      Ładowanie budżetów...
    </div>

    <div v-else-if="error" class="public-plans-empty error">
      {{ error }}
    </div>

    <div v-else-if="budgets.length === 0" class="public-plans-empty">
      Brak budżetów koła z dofinansowaniami.
    </div>

    <div v-else class="public-plans-layout">
      <aside class="public-plans-budget-list">
        <button
          v-for="budget in budgets"
          :key="budget.association_budget_id"
          type="button"
          class="budget-option"
          :class="{ active: activeBudgetId === budget.association_budget_id }"
          @click="activeBudgetId = budget.association_budget_id"
        >
          <span class="budget-option__name">{{ budget.association_budget_name }}</span>
          <span class="budget-option__meta">
            {{ budget.fundings.length }} dofinansowań
          </span>
          <span class="budget-option__amount">
            {{ formatMoney(budget.available_money) }} PLN dostępne
          </span>
        </button>
      </aside>

      <section v-if="selectedBudget" class="public-plans-details">
        <div class="budget-summary">
          <div>
            <h3 class="budget-summary__title">{{ selectedBudget.association_budget_name }}</h3>
            <p class="budget-summary__subtitle">
              Budżet koła: {{ formatMoney(selectedBudget.total_budget) }} PLN
            </p>
          </div>
          <div class="budget-summary__numbers">
            <div>
              <span>Wydane</span>
              <strong>{{ formatMoney(selectedBudget.spent_money) }} PLN</strong>
            </div>
            <div>
              <span>Planowane</span>
              <strong>{{ formatMoney(planTotal) }} PLN</strong>
            </div>
          </div>
        </div>

        <div class="fundings-panel">
          <div class="panel-heading">
            <h3>Dofinansowania w budżecie</h3>
          </div>

          <div v-if="selectedBudget.fundings.length === 0" class="panel-empty">
            Ten budżet nie ma dostępnych dofinansowań.
          </div>

          <div v-else class="fundings-grid">
            <div
              v-for="funding in selectedBudget.fundings"
              :key="funding.funding_id"
              class="funding-row"
            >
              <span class="funding-row__name">{{ funding.funding_name }}</span>
              <span>{{ formatMoney(funding.funding_price) }} PLN</span>
              <span class="funding-row__available">
                {{ formatMoney(funding.available_money) }} PLN dostępne
              </span>
            </div>
          </div>
        </div>

        <div v-if="!selectedBudget.public_purchase_plan_list" class="attach-panel">
          <div>
            <h3>Brak listy planów publicznych</h3>
            <p>Utwórz i przypnij listę planów do tego budżetu koła.</p>
          </div>
          <form class="attach-form" @submit.prevent="createPlanList">
            <input
              v-model="newListName"
              type="text"
              placeholder="Nazwa listy planów publicznych"
              class="public-input"
            />
            <button class="public-primary-btn" type="submit">
              Przypnij listę
            </button>
          </form>
        </div>

        <div v-else class="plans-panel">
          <div class="panel-heading">
            <div>
              <h3>{{ selectedBudget.public_purchase_plan_list.public_plan_list_name }}</h3>
              <p>
                Łączna wartość planów:
                {{ formatMoney(selectedBudget.public_purchase_plan_list.total_cost) }} PLN
              </p>
            </div>
            <button
              class="public-primary-btn"
              type="button"
              :disabled="selectedBudget.fundings.length === 0"
              @click="openPlanModal"
            >
              + Dodaj plan
            </button>
          </div>

          <div
            v-if="selectedBudget.public_purchase_plan_list.public_purchase_plans.length === 0"
            class="panel-empty"
          >
            Lista jest pusta. Dodaj pierwszy plan publiczny.
          </div>

          <div v-else class="plans-table-wrapper">
            <table class="plans-table">
              <thead>
                <tr>
                  <th>Nazwa planu</th>
                  <th>Dofinansowanie</th>
                  <th>Koszt</th>
                  <th>Akcje</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="plan in selectedBudget.public_purchase_plan_list.public_purchase_plans"
                  :key="plan.public_purchase_plan_id"
                >
                  <td>{{ plan.public_purchase_plan_name }}</td>
                  <td>{{ plan.funding_name || 'Brak' }}</td>
                  <td>{{ formatMoney(plan.cost) }} PLN</td>
                  <td>
                    <button
                      class="public-danger-btn"
                      type="button"
                      @click="deletePlan(plan.public_purchase_plan_id)"
                    >
                      Usuń
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </div>

    <div v-if="showPlanModal" class="modal-overlay" @click="closePlanModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2 class="modal-title">Nowy plan publiczny</h2>
          <button class="modal-close" type="button" @click="closePlanModal">✕</button>
        </div>

        <form class="modal-form" @submit.prevent="createPlan">
          <label class="modal-field">
            <span>Nazwa planu</span>
            <input
              v-model="newPlan.public_purchase_plan_name"
              type="text"
              placeholder="np. Zakup podzespołów elektronicznych"
              class="public-input"
              required
            />
          </label>

          <label class="modal-field">
            <span>Dofinansowanie</span>
            <select
              v-model.number="newPlan.funding_id"
              class="public-input"
              required
            >
              <option value="" disabled>Wybierz dofinansowanie</option>
              <option
                v-for="funding in selectedBudget?.fundings || []"
                :key="funding.funding_id"
                :value="funding.funding_id"
              >
                {{ funding.funding_name }} - {{ formatMoney(funding.available_money) }} PLN dostępne
              </option>
            </select>
          </label>

          <label class="modal-field">
            <span>Koszt planu</span>
            <input
              v-model.number="newPlan.cost"
              type="number"
              min="0.01"
              step="0.01"
              placeholder="0.00"
              class="public-input"
              required
            />
          </label>

          <div class="modal-actions">
            <button class="modal-btn modal-btn-cancel" type="button" @click="closePlanModal">
              Anuluj
            </button>
            <button class="modal-btn modal-btn-save" type="submit">
              Dodaj plan
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { useToast } from '@/composables/useToast'

const API_URL = 'http://localhost:8080/api'

const { user } = useAuth()
const toast = useToast()

const budgets = ref([])
const activeBudgetId = ref(null)
const loading = ref(false)
const error = ref(null)
const newListName = ref('')
const showPlanModal = ref(false)
const newPlan = ref({
  public_purchase_plan_name: '',
  cost: null,
  funding_id: ''
})

const selectedBudget = computed(() => {
  return budgets.value.find(
    budget => budget.association_budget_id === activeBudgetId.value
  ) || budgets.value[0] || null
})

const planTotal = computed(() => {
  return selectedBudget.value?.public_purchase_plan_list?.total_cost || 0
})

const formatMoney = (value) => {
  return Number(value || 0).toLocaleString('pl-PL', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

const defaultListName = () => {
  const budgetName = selectedBudget.value?.association_budget_name || 'budżetu koła'
  return `Plan zamówień publicznych dla ${budgetName}`
}

const loadBudgets = async () => {
  if (!user.value?.association_id) {
    error.value = 'Brak informacji o kole naukowym użytkownika.'
    return
  }

  try {
    loading.value = true
    error.value = null

    const response = await fetch(
      `${API_URL}/association_budgets?association_id=${user.value.association_id}`
    )
    if (!response.ok) throw new Error('Nie udało się pobrać budżetów koła.')

    const data = await response.json()
    budgets.value = data

    const activeStillExists = data.some(
      budget => budget.association_budget_id === activeBudgetId.value
    )
    if (!activeStillExists) {
      activeBudgetId.value = data[0]?.association_budget_id || null
    }
  } catch (err) {
    console.error('Błąd pobierania planów publicznych:', err)
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const createPlanList = async () => {
  if (!selectedBudget.value) return

  try {
    const response = await fetch(`${API_URL}/public_purchase_plan_lists`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        association_budget_id: selectedBudget.value.association_budget_id,
        public_plan_list_name: newListName.value.trim() || defaultListName()
      })
    })

    if (!response.ok) {
      const err = await response.json()
      throw new Error(err.detail || 'Nie udało się przypiąć listy planów.')
    }

    newListName.value = ''
    toast.success('Lista planów publicznych została przypięta do budżetu.')
    await loadBudgets()
  } catch (err) {
    console.error('Błąd tworzenia listy planów:', err)
    toast.error(err.message)
  }
}

const openPlanModal = () => {
  if (!selectedBudget.value?.public_purchase_plan_list) {
    toast.error('Najpierw przypnij listę planów publicznych do budżetu.')
    return
  }

  const firstFunding = selectedBudget.value.fundings[0]
  newPlan.value = {
    public_purchase_plan_name: '',
    cost: null,
    funding_id: firstFunding?.funding_id || ''
  }
  showPlanModal.value = true
}

const closePlanModal = () => {
  showPlanModal.value = false
}

const createPlan = async () => {
  if (!selectedBudget.value?.public_purchase_plan_list) return

  try {
    const response = await fetch(`${API_URL}/public_purchase_plans`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        public_purchase_plan_list_id:
          selectedBudget.value.public_purchase_plan_list.public_purchase_plan_list_id,
        public_purchase_plan_name: newPlan.value.public_purchase_plan_name,
        cost: Number(newPlan.value.cost),
        funding_id: Number(newPlan.value.funding_id)
      })
    })

    if (!response.ok) {
      const err = await response.json()
      throw new Error(err.detail || 'Nie udało się dodać planu publicznego.')
    }

    showPlanModal.value = false
    toast.success('Plan publiczny został dodany.')
    await loadBudgets()
  } catch (err) {
    console.error('Błąd dodawania planu publicznego:', err)
    toast.error(err.message)
  }
}

const deletePlan = async (planId) => {
  if (!confirm('Czy na pewno chcesz usunąć ten plan publiczny?')) return

  try {
    const response = await fetch(`${API_URL}/public_purchase_plans/${planId}`, {
      method: 'DELETE'
    })
    if (!response.ok) {
      const err = await response.json()
      throw new Error(err.detail || 'Nie udało się usunąć planu publicznego.')
    }

    toast.info('Plan publiczny został usunięty.')
    await loadBudgets()
  } catch (err) {
    console.error('Błąd usuwania planu publicznego:', err)
    toast.error(err.message)
  }
}

onMounted(() => {
  loadBudgets()
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;500;600;700;800&display=swap');

.public-plans-section {
  width: 100%;
  padding: 3vh 0;
  color: #ffffff;
  font-family: 'Nunito', system-ui, sans-serif;
}

.public-plans-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 2vw;
  margin-bottom: 3vh;
}

.public-plans-title {
  margin: 0 0 0.8vh 0;
  color: #bfdbfe;
  font-size: 2vw;
  font-weight: 800;
}

.public-plans-subtitle {
  margin: 0;
  color: rgba(226, 232, 240, 0.6);
  font-size: 1vw;
}

.public-plans-refresh,
.public-primary-btn {
  padding: 0.8vw 1.4vw;
  border: none;
  border-radius: 0.7vw;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: #ffffff;
  font-family: 'Nunito', system-ui, sans-serif;
  font-size: 0.95vw;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.2s ease;
}

.public-plans-refresh:hover,
.public-primary-btn:hover {
  transform: translateY(-0.2vh);
  box-shadow: 0 6px 18px rgba(37, 99, 235, 0.36);
}

.public-primary-btn:disabled {
  cursor: not-allowed;
  opacity: 0.55;
  transform: none;
  box-shadow: none;
}

.public-plans-empty {
  padding: 5vh;
  border: 0.08vw dashed rgba(148, 163, 184, 0.3);
  border-radius: 1vw;
  background: rgba(15, 23, 42, 0.45);
  color: rgba(226, 232, 240, 0.75);
  text-align: center;
  font-size: 1.05vw;
  font-weight: 700;
}

.public-plans-empty.error {
  color: #fca5a5;
  border-color: rgba(239, 68, 68, 0.35);
}

.public-plans-layout {
  display: grid;
  grid-template-columns: minmax(18vw, 24vw) 1fr;
  gap: 2vw;
}

.public-plans-budget-list {
  display: flex;
  flex-direction: column;
  gap: 1vw;
}

.budget-option {
  display: grid;
  gap: 0.5vw;
  width: 100%;
  padding: 1.2vw;
  border: 0.08vw solid rgba(148, 163, 184, 0.16);
  border-radius: 0.9vw;
  background: rgba(15, 23, 42, 0.58);
  color: #ffffff;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s ease;
}

.budget-option:hover,
.budget-option.active {
  border-color: rgba(96, 165, 250, 0.55);
  background: rgba(30, 41, 59, 0.86);
}

.budget-option__name {
  font-size: 1.02vw;
  font-weight: 800;
}

.budget-option__meta,
.budget-option__amount {
  color: rgba(226, 232, 240, 0.62);
  font-size: 0.86vw;
  font-weight: 600;
}

.public-plans-details,
.fundings-panel,
.attach-panel,
.plans-panel {
  border: 0.08vw solid rgba(148, 163, 184, 0.15);
  border-radius: 1vw;
  background: rgba(15, 23, 42, 0.58);
}

.public-plans-details {
  display: grid;
  gap: 1.5vw;
  padding: 1.6vw;
}

.budget-summary,
.panel-heading,
.attach-panel {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 2vw;
}

.budget-summary {
  padding-bottom: 1.2vw;
  border-bottom: 0.08vw solid rgba(148, 163, 184, 0.12);
}

.budget-summary__title,
.panel-heading h3,
.attach-panel h3 {
  margin: 0;
  color: #bfdbfe;
  font-size: 1.35vw;
  font-weight: 800;
}

.budget-summary__subtitle,
.panel-heading p,
.attach-panel p {
  margin: 0.5vh 0 0 0;
  color: rgba(226, 232, 240, 0.58);
  font-size: 0.92vw;
}

.budget-summary__numbers {
  display: flex;
  gap: 1vw;
}

.budget-summary__numbers div {
  display: grid;
  gap: 0.35vw;
  min-width: 9vw;
  padding: 0.8vw 1vw;
  border-radius: 0.7vw;
  background: rgba(30, 41, 59, 0.62);
}

.budget-summary__numbers span {
  color: rgba(226, 232, 240, 0.58);
  font-size: 0.8vw;
  font-weight: 700;
}

.budget-summary__numbers strong {
  color: #ffffff;
  font-size: 0.98vw;
}

.fundings-panel,
.plans-panel,
.attach-panel {
  padding: 1.3vw;
}

.fundings-grid {
  display: grid;
  gap: 0.7vw;
  margin-top: 1vw;
}

.funding-row {
  display: grid;
  grid-template-columns: 1.5fr 1fr 1fr;
  gap: 1vw;
  padding: 0.8vw 1vw;
  border-radius: 0.65vw;
  background: rgba(30, 41, 59, 0.58);
  color: rgba(226, 232, 240, 0.78);
  font-size: 0.9vw;
  font-weight: 700;
}

.funding-row__name {
  color: #ffffff;
}

.funding-row__available {
  color: #86efac;
  text-align: right;
}

.attach-form {
  display: flex;
  align-items: center;
  gap: 0.8vw;
  min-width: 34vw;
}

.public-input {
  width: 100%;
  padding: 0.85vw 1vw;
  border: 0.08vw solid rgba(148, 163, 184, 0.22);
  border-radius: 0.65vw;
  background: rgba(30, 41, 59, 0.72);
  color: #ffffff;
  font-family: 'Nunito', system-ui, sans-serif;
  font-size: 0.95vw;
  outline: none;
  transition: all 0.2s ease;
}

.public-input:focus {
  border-color: rgba(96, 165, 250, 0.9);
  box-shadow: 0 0 0 0.3vw rgba(59, 130, 246, 0.2);
}

.panel-empty {
  margin-top: 1vw;
  padding: 2vw;
  border: 0.08vw dashed rgba(148, 163, 184, 0.25);
  border-radius: 0.8vw;
  color: rgba(226, 232, 240, 0.58);
  text-align: center;
  font-size: 0.95vw;
  font-weight: 700;
}

.plans-table-wrapper {
  margin-top: 1vw;
  overflow: hidden;
  border-radius: 0.8vw;
  border: 0.08vw solid rgba(148, 163, 184, 0.12);
}

.plans-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.92vw;
}

.plans-table th,
.plans-table td {
  padding: 1vw;
  border-bottom: 0.08vw solid rgba(148, 163, 184, 0.1);
}

.plans-table th {
  background: rgba(30, 41, 59, 0.82);
  color: #93c5fd;
  font-size: 0.78vw;
  font-weight: 800;
  text-transform: uppercase;
}

.plans-table td {
  color: #e2e8f0;
  font-weight: 600;
}

.public-danger-btn {
  padding: 0.45vw 0.8vw;
  border: 0.08vw solid rgba(239, 68, 68, 0.32);
  border-radius: 0.45vw;
  background: rgba(239, 68, 68, 0.14);
  color: #fca5a5;
  font-family: 'Nunito', system-ui, sans-serif;
  font-size: 0.8vw;
  font-weight: 800;
  cursor: pointer;
}

.public-danger-btn:hover {
  background: rgba(239, 68, 68, 0.28);
}

.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(5, 8, 22, 0.78);
  backdrop-filter: blur(6px);
}

.modal-content {
  width: min(90vw, 38vw);
  padding: 2vw;
  border: 0.08vw solid rgba(148, 163, 184, 0.18);
  border-radius: 1vw;
  background: #0f172a;
  box-shadow: 0 24px 55px rgba(0, 0, 0, 0.55);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5vw;
}

.modal-title {
  margin: 0;
  color: #bfdbfe;
  font-size: 1.45vw;
  font-weight: 800;
}

.modal-close {
  border: none;
  background: transparent;
  color: rgba(226, 232, 240, 0.68);
  font-size: 1.4vw;
  cursor: pointer;
}

.modal-form {
  display: grid;
  gap: 1vw;
}

.modal-field {
  display: grid;
  gap: 0.5vw;
  color: rgba(226, 232, 240, 0.88);
  font-size: 0.95vw;
  font-weight: 700;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1vw;
  margin-top: 1vw;
  padding-top: 1.2vw;
  border-top: 0.08vw solid rgba(148, 163, 184, 0.15);
}

.modal-btn {
  padding: 0.8vw 1.4vw;
  border: none;
  border-radius: 0.65vw;
  font-family: 'Nunito', system-ui, sans-serif;
  font-size: 0.95vw;
  font-weight: 800;
  cursor: pointer;
}

.modal-btn-cancel {
  background: rgba(148, 163, 184, 0.14);
  color: #e2e8f0;
}

.modal-btn-save {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: #ffffff;
}

@media (max-width: 1024px) {
  .public-plans-layout {
    grid-template-columns: 1fr;
  }

  .public-plans-budget-list {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
  }

  .attach-panel,
  .budget-summary,
  .panel-heading {
    flex-direction: column;
  }

  .attach-form {
    min-width: 100%;
  }

  .modal-content {
    width: min(92vw, 60vw);
  }
}

@media (max-width: 640px) {
  .public-plans-budget-list,
  .funding-row {
    grid-template-columns: 1fr;
  }

  .budget-summary__numbers,
  .attach-form {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
