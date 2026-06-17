<template>
  <section class="plans">
    <header class="plans__header">
      <div>
        <h2>Dofinansowania i plany publiczne</h2>
        <p>Twórz dofinansowania, zadania budżetowe i roczne plany CPV.</p>
      </div>
      <div class="header-actions">
        <button type="button" class="button" @click="openFundingModal">Nowe dofinansowanie</button>
        <button type="button" class="button button--secondary" @click="loadData">Odśwież</button>
      </div>
    </header>

    <div v-if="loading" class="state">Ładowanie planów...</div>
    <div v-else-if="error" class="state state--error">{{ error }}</div>
    <div v-else-if="fundings.length === 0" class="state">Brak dofinansowań w kole.</div>

    <div v-else class="plans__layout">
      <nav class="funding-list" aria-label="Dofinansowania">
        <button
          v-for="funding in fundings"
          :key="funding.funding_id"
          type="button"
          class="funding"
          :class="{ 'funding--active': funding.funding_id === activeFundingId }"
          @click="activeFundingId = funding.funding_id"
        >
          <strong>{{ funding.funding_name }}</strong>
          <span>{{ funding.project_budget_name }}</span>
          <span v-if="funding.organizer">Organizator: {{ funding.organizer }}</span>
          <span>{{ formatMoney(funding.funding_price) }} PLN</span>
        </button>
      </nav>

      <div v-if="selectedFunding" class="workspace">
        <header class="workspace__header">
          <div>
            <h3>{{ selectedFunding.funding_name }}</h3>
            <p>{{ selectedFunding.project_budget_name }}<span v-if="selectedFunding.organizer"> | {{ selectedFunding.organizer }}</span></p>
          </div>
          <dl>
            <div><dt>Dofinansowanie</dt><dd>{{ formatMoney(selectedFunding.funding_price) }} PLN</dd></div>
            <div><dt>Zaplanowano</dt><dd>{{ formatMoney(selectedPlan?.total_cost) }} PLN</dd></div>
            <div><dt>Podpisuje</dt><dd>{{ selectedFunding.signing_person || '-' }}</dd></div>
          </dl>
          <button type="button" class="button button--secondary" @click="openFundingModal(selectedFunding)">Edytuj dofinansowanie</button>
        </header>

        <div v-if="selectedFunding.tasks?.length" class="tasks-summary">
          <div v-for="task in selectedFunding.tasks" :key="task.funding_task_id" class="task-chip">
            <span>{{ task.task_name }}</span>
            <strong>{{ formatMoney(task.task_budget) }} PLN</strong>
          </div>
        </div>

        <form v-if="!selectedPlan" class="create-plan" @submit.prevent="createPlanList">
          <div>
            <h3>Utwórz plan dla dofinansowania</h3>
            <p>Plan będzie zawierał wyłącznie kody CPV i planowane kwoty.</p>
          </div>
          <label>
            <span>Rok planu</span>
            <input v-model.number="planYear" type="number" min="2000" max="2100" required />
          </label>
          <label>
            <span>Kod planu</span>
            <input v-model="planNumber" type="text" placeholder="np. ZP/2026/01" />
          </label>
          <label>
            <span>Osoba odpowiedzialna</span>
            <input v-model="fundResponsiblePerson" type="text" :placeholder="selectedFunding.signing_person || 'Imie i nazwisko'" />
          </label>
          <button class="button" type="submit">Utwórz plan</button>
        </form>

        <template v-else>
          <div class="table-header">
            <div>
              <h3>{{ selectedPlan.public_plan_list_name }}</h3>
              <p>
                Rok {{ selectedPlan.plan_year }}
                <span v-if="selectedPlan.plan_number"> | Kod planu {{ selectedPlan.plan_number }}</span>
                <span v-if="selectedPlan.fund_responsible_person"> | Odp. {{ selectedPlan.fund_responsible_person }}</span>
              </p>
            </div>
            <button class="button" type="button" @click="openPositionModal">Dodaj pozycję CPV</button>
          </div>

          <div v-if="selectedPlan.public_purchase_plans.length === 0" class="state">
            Plan nie ma jeszcze pozycji CPV.
          </div>
          <div v-else class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Kod CPV</th>
                  <th>Pozycja planu</th>
                  <th>Opis</th>
                  <th>Kategoria</th>
                  <th>Planowana kwota netto</th>
                  <th>Wykorzystano</th>
                  <th>Pozostało</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="position in selectedPlan.public_purchase_plans" :key="position.public_purchase_plan_id">
                  <td><strong>{{ position.cpv_code }}</strong></td>
                  <td>{{ position.plan_position_number || '-' }}</td>
                  <td>{{ position.description || position.public_purchase_plan_name || '-' }}</td>
                  <td>{{ position.product_category_name || '-' }}</td>
                  <td>{{ formatMoney(position.cost) }} PLN</td>
                  <td>{{ formatMoney(position.used_amount) }} PLN</td>
                  <td :class="{ negative: position.remaining_amount < 0 }">
                    {{ formatMoney(position.remaining_amount) }} PLN
                  </td>
                  <td>
                    <button
                      type="button"
                      class="delete edit"
                      title="Edytuj pozycje"
                      @click="openPositionModal(position)"
                    >
                      Edytuj
                    </button>
                    <button
                      type="button"
                      class="delete"
                      title="Usuń pozycję"
                      @click="deletePosition(position.public_purchase_plan_id)"
                    >
                      Usuń
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </template>
      </div>
    </div>

    <div v-if="showPositionModal" class="modal-overlay" @click="closePositionModal">
      <div class="modal" @click.stop>
        <header>
          <h3>{{ editingPositionId ? 'Edycja pozycji planu' : 'Nowa pozycja planu' }}</h3>
          <button type="button" title="Zamknij" @click="closePositionModal">×</button>
        </header>
        <form @submit.prevent="savePosition">
          <label>
            <span>Kod CPV</span>
            <input v-model="newPosition.cpv_code" type="text" placeholder="np. 42000000-6" required />
          </label>
          <label>
            <span>Numer pozycji w planie</span>
            <input v-model="newPosition.plan_position_number" type="text" placeholder="np. 1.2.3" />
          </label>
          <label>
            <span>Krotki opis</span>
            <textarea v-model="newPosition.description" rows="3" placeholder="np. sprzet elektroniczny, narzedzia, materialy"></textarea>
          </label>
          <label>
            <span>Kategoria produktu</span>
            <select v-model.number="newPosition.product_category_id">
              <option :value="null">Bez kategorii</option>
              <option
                v-for="category in categories"
                :key="category.product_category_id"
                :value="category.product_category_id"
              >
                {{ category.product_category_name }}
              </option>
            </select>
          </label>
          <label>
            <span>Planowana kwota netto</span>
            <input v-model.number="newPosition.cost" type="number" min="0.01" step="0.01" required />
          </label>
          <footer>
            <button class="button button--secondary" type="button" @click="closePositionModal">Anuluj</button>
            <button class="button" type="submit">{{ editingPositionId ? 'Zapisz' : 'Dodaj' }}</button>
          </footer>
        </form>
      </div>
    </div>

    <div v-if="showFundingModal" class="modal-overlay" @click="closeFundingModal">
      <div class="modal modal--wide" @click.stop>
        <header>
          <h3>{{ editingFundingId ? 'Edycja dofinansowania' : 'Nowe dofinansowanie' }}</h3>
          <button type="button" title="Zamknij" @click="closeFundingModal">x</button>
        </header>
        <form @submit.prevent="saveFunding">
          <label>
            <span>Sekcja/projekt</span>
            <select v-model.number="newFunding.project_budget_id" required>
              <option :value="null" disabled>Wybierz sekcję...</option>
              <option v-for="budget in projectBudgets" :key="budget.project_budget_id" :value="budget.project_budget_id">
                {{ budget.project_budget_name }} - {{ budget.project_name || budget.association_budget_name }}
              </option>
            </select>
          </label>
          <label>
            <span>Nazwa dofinansowania</span>
            <input v-model="newFunding.funding_name" type="text" required />
          </label>
          <label>
            <span>Organizator</span>
            <input v-model="newFunding.organizer" type="text" required />
          </label>
          <label>
            <span>Osoba podpisująca wnioski</span>
            <input v-model="newFunding.signing_person" type="text" required />
          </label>
          <label>
            <span>Kwota dofinansowania</span>
            <input v-model.number="newFunding.funding_price" type="number" min="0.01" step="0.01" required />
          </label>

          <div class="funding-tasks">
            <div class="tasks-header">
              <strong>Zadania w dofinansowaniu</strong>
              <button class="button button--secondary" type="button" @click="addFundingTask">Dodaj zadanie</button>
            </div>
            <div v-for="(task, index) in newFunding.tasks" :key="index" class="task-row">
              <input v-model="task.task_name" type="text" placeholder="Nazwa zadania" />
              <input v-model.number="task.task_budget" type="number" min="0.01" step="0.01" placeholder="Budżet" />
              <button type="button" class="delete" @click="removeFundingTask(index)">Usuń</button>
            </div>
            <p :class="{ negative: fundingTasksTotal > Number(newFunding.funding_price || 0) }">
              Suma zadań: {{ formatMoney(fundingTasksTotal) }} PLN
            </p>
          </div>

          <footer>
            <button class="button button--secondary" type="button" @click="closeFundingModal">Anuluj</button>
            <button class="button" type="submit">{{ editingFundingId ? 'Zapisz dofinansowanie' : 'Utwórz dofinansowanie' }}</button>
          </footer>
        </form>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { useToast } from '@/composables/useToast'

const API_URL = 'http://localhost:8080/api'
const { user } = useAuth()
const toast = useToast()

const fundings = ref([])
const planLists = ref([])
const categories = ref([])
const projectBudgets = ref([])
const activeFundingId = ref(null)
const loading = ref(false)
const error = ref('')
const planYear = ref(new Date().getFullYear())
const planNumber = ref('')
const fundResponsiblePerson = ref('')
const showPositionModal = ref(false)
const showFundingModal = ref(false)
const editingPositionId = ref(null)
const editingFundingId = ref(null)
const newFunding = ref({
  project_budget_id: null,
  funding_name: '',
  organizer: '',
  signing_person: '',
  funding_price: null,
  tasks: []
})
const newPosition = ref({
  cpv_code: '',
  plan_position_number: '',
  cost: null,
  description: '',
  product_category_id: null
})

const selectedFunding = computed(() =>
  fundings.value.find(funding => funding.funding_id === activeFundingId.value) || fundings.value[0]
)
const selectedPlan = computed(() =>
  planLists.value.find(plan => plan.funding_id === selectedFunding.value?.funding_id) || null
)
const fundingTasksTotal = computed(() =>
  newFunding.value.tasks.reduce((sum, task) => sum + Number(task.task_budget || 0), 0)
)

const formatMoney = value => Number(value || 0).toLocaleString('pl-PL', {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2
})

const loadData = async () => {
  if (!user.value?.association_id) return
  loading.value = true
  error.value = ''
  try {
    const [fundingsResponse, plansResponse, categoriesResponse, budgetsResponse] = await Promise.all([
      fetch(`${API_URL}/fundings?association_id=${user.value.association_id}`),
      fetch(`${API_URL}/public_purchase_plan_lists?association_id=${user.value.association_id}`),
      fetch(`${API_URL}/categories`),
      fetch(`${API_URL}/project_budgets?association_id=${user.value.association_id}`)
    ])
    if (!fundingsResponse.ok || !plansResponse.ok) throw new Error('Nie udało się pobrać planów.')
    fundings.value = await fundingsResponse.json()
    planLists.value = await plansResponse.json()
    categories.value = categoriesResponse.ok ? await categoriesResponse.json() : []
    projectBudgets.value = budgetsResponse.ok ? await budgetsResponse.json() : []
    if (!fundings.value.some(funding => funding.funding_id === activeFundingId.value)) {
      activeFundingId.value = fundings.value[0]?.funding_id || null
    }
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const createPlanList = async () => {
  const funding = selectedFunding.value
  if (!funding) return
  const response = await fetch(`${API_URL}/public_purchase_plan_lists`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      funding_id: funding.funding_id,
      plan_year: Number(planYear.value),
      plan_number: planNumber.value.trim(),
      fund_responsible_person: (fundResponsiblePerson.value || funding.signing_person || '').trim(),
      public_plan_list_name: `Plan ZP - ${funding.funding_name}`
    })
  })
  const data = await response.json()
  if (!response.ok) return toast.error(data.detail || 'Nie udało się utworzyć planu.')
  toast.success('Plan dofinansowania został utworzony.')
  await loadData()
}

const resetFundingForm = () => {
  editingFundingId.value = null
  newFunding.value = {
    project_budget_id: projectBudgets.value[0]?.project_budget_id || null,
    funding_name: '',
    organizer: '',
    signing_person: '',
    funding_price: null,
    tasks: []
  }
}

const openFundingModal = (funding = null) => {
  if (funding) {
    editingFundingId.value = funding.funding_id
    newFunding.value = {
      project_budget_id: funding.project_budget_id || null,
      funding_name: funding.funding_name || '',
      organizer: funding.organizer || '',
      signing_person: funding.signing_person || '',
      funding_price: funding.funding_price || null,
      tasks: (funding.tasks || []).map(task => ({
        task_name: task.task_name || '',
        task_budget: task.task_budget || null
      }))
    }
  } else {
    resetFundingForm()
  }
  showFundingModal.value = true
}

const closeFundingModal = () => {
  showFundingModal.value = false
  editingFundingId.value = null
}

const addFundingTask = () => {
  newFunding.value.tasks.push({ task_name: '', task_budget: null })
}

const removeFundingTask = index => {
  newFunding.value.tasks.splice(index, 1)
}

const saveFunding = async () => {
  if (fundingTasksTotal.value > Number(newFunding.value.funding_price || 0)) {
    return toast.error('Suma zadan nie moze przekraczac kwoty dofinansowania.')
  }
  const isEditing = Boolean(editingFundingId.value)
  const response = await fetch(`${API_URL}/fundings${isEditing ? `/${editingFundingId.value}` : ''}`, {
    method: isEditing ? 'PATCH' : 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      project_budget_id: newFunding.value.project_budget_id,
      funding_name: newFunding.value.funding_name.trim(),
      organizer: newFunding.value.organizer.trim(),
      signing_person: newFunding.value.signing_person.trim(),
      funding_price: Number(newFunding.value.funding_price),
      tasks: newFunding.value.tasks
        .filter(task => task.task_name || task.task_budget)
        .map(task => ({
          task_name: String(task.task_name || '').trim(),
          task_budget: Number(task.task_budget || 0)
        }))
    })
  })
  const data = await response.json()
  if (!response.ok) return toast.error(data.detail || 'Nie udalo sie zapisac dofinansowania.')
  closeFundingModal()
  toast.success(isEditing ? 'Dofinansowanie zostalo zaktualizowane.' : 'Dofinansowanie zostalo utworzone.')
  await loadData()
  activeFundingId.value = data.funding_id
  fundResponsiblePerson.value = data.signing_person || ''
}

const openPositionModal = (position = null) => {
  editingPositionId.value = position?.public_purchase_plan_id || null
  newPosition.value = position
    ? {
        cpv_code: position.cpv_code,
        plan_position_number: position.plan_position_number || '',
        cost: position.cost,
        description: position.description || '',
        product_category_id: position.product_category_id || null
      }
    : {
        cpv_code: '',
        plan_position_number: '',
        cost: null,
        description: '',
        product_category_id: null
      }
  showPositionModal.value = true
}
const closePositionModal = () => {
  showPositionModal.value = false
  editingPositionId.value = null
}

const savePosition = async () => {
  if (!selectedPlan.value) return
  const isEditing = Boolean(editingPositionId.value)
  const response = await fetch(`${API_URL}/public_purchase_plans${isEditing ? `/${editingPositionId.value}` : ''}`, {
    method: isEditing ? 'PATCH' : 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      public_purchase_plan_list_id: selectedPlan.value.public_purchase_plan_list_id,
      cpv_code: String(newPosition.value.cpv_code || '').trim(),
      plan_position_number: String(newPosition.value.plan_position_number || '').trim(),
      cost: Number(newPosition.value.cost),
      description: (newPosition.value.description || '').trim(),
      product_category_id: newPosition.value.product_category_id || null
    })
  })
  const data = await response.json()
  if (!response.ok) return toast.error(data.detail || 'Nie udało się dodać pozycji.')
  closePositionModal()
  toast.success(isEditing ? 'Pozycja CPV zostala zaktualizowana.' : 'Pozycja CPV zostala dodana.')
  await loadData()
}

const deletePosition = async id => {
  if (!confirm('Usunąć tę pozycję planu?')) return
  const response = await fetch(`${API_URL}/public_purchase_plans/${id}`, { method: 'DELETE' })
  const data = await response.json()
  if (!response.ok) return toast.error(data.detail || 'Nie udało się usunąć pozycji.')
  await loadData()
}

onMounted(loadData)
</script>

<style scoped>
.plans { color: #fff; padding: 28px 0; }
.plans__header, .workspace__header, .table-header, .create-plan, .modal header, .modal footer, .header-actions {
  display: flex; justify-content: space-between; align-items: center; gap: 20px;
}
h2, h3, p { margin: 0; }
h2 { color: #bfdbfe; font-size: 28px; }
h3 { color: #dbeafe; font-size: 20px; }
p, dt { color: #94a3b8; }
.plans__header { margin-bottom: 24px; }
.plans__header p, .workspace p, .table-header p { margin-top: 5px; }
.plans__layout { display: grid; grid-template-columns: minmax(240px, 300px) 1fr; gap: 20px; }
.funding-list { display: flex; flex-direction: column; gap: 10px; }
.funding {
  display: grid; gap: 6px; padding: 16px; text-align: left; color: #fff; cursor: pointer;
  background: rgba(15, 23, 42, .65); border: 1px solid rgba(148, 163, 184, .18); border-radius: 8px;
}
.funding span { color: #94a3b8; }
.funding--active { border-color: #60a5fa; background: rgba(30, 41, 59, .9); }
.workspace { padding: 22px; background: rgba(15, 23, 42, .65); border: 1px solid rgba(148, 163, 184, .18); border-radius: 8px; }
.workspace__header { padding-bottom: 20px; border-bottom: 1px solid rgba(148, 163, 184, .16); flex-wrap: wrap; }
dl { display: flex; gap: 24px; margin: 0; }
dt { font-size: 12px; } dd { margin: 3px 0 0; font-weight: 700; }
.tasks-summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; margin-top: 16px; }
.task-chip { display: flex; justify-content: space-between; gap: 12px; padding: 10px 12px; border-radius: 7px; background: rgba(30, 41, 59, .6); border: 1px solid rgba(148, 163, 184, .14); color: #cbd5e1; }
.task-chip strong { color: #bfdbfe; }
.create-plan { margin-top: 20px; padding: 18px; background: rgba(30, 41, 59, .62); border-radius: 8px; }
.table-header { margin: 22px 0 14px; }
.button {
  padding: 10px 16px; border: 0; border-radius: 7px; background: #2563eb; color: #fff;
  font-weight: 700; cursor: pointer;
}
.button--secondary { background: #334155; }
.state { padding: 34px; text-align: center; color: #94a3b8; border: 1px dashed #475569; border-radius: 8px; }
.state--error, .negative { color: #fca5a5; }
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 13px; text-align: left; border-bottom: 1px solid rgba(148, 163, 184, .15); }
th { color: #94a3b8; font-size: 13px; }
.delete { border: 0; background: transparent; color: #fca5a5; cursor: pointer; }
label { display: grid; gap: 7px; color: #cbd5e1; font-weight: 700; }
input { padding: 11px; border: 1px solid #475569; border-radius: 7px; background: #0f172a; color: #fff; }
select, textarea { padding: 11px; border: 1px solid #475569; border-radius: 7px; background: #0f172a; color: #fff; }
.modal-overlay { position: fixed; inset: 0; display: grid; place-items: center; background: rgba(2, 6, 23, .78); z-index: 1000; }
.modal { width: min(460px, calc(100vw - 32px)); padding: 22px; border-radius: 8px; background: #111827; }
.modal--wide { width: min(720px, calc(100vw - 32px)); max-height: 88vh; overflow-y: auto; }
.modal header button { border: 0; background: transparent; color: #fff; font-size: 25px; cursor: pointer; }
.modal form { display: grid; gap: 18px; margin-top: 20px; }
.funding-tasks { display: grid; gap: 10px; padding: 14px; border-radius: 8px; background: rgba(15, 23, 42, .55); border: 1px solid rgba(148, 163, 184, .14); }
.tasks-header, .task-row { display: grid; grid-template-columns: 1fr auto; gap: 10px; align-items: center; }
.task-row { grid-template-columns: 1fr 150px auto; }
@media (max-width: 850px) {
  .plans__layout { grid-template-columns: 1fr; }
  .plans__header, .workspace__header, .create-plan, .header-actions { align-items: flex-start; flex-direction: column; }
  .task-row { grid-template-columns: 1fr; }
  dl { flex-wrap: wrap; }
}
</style>
