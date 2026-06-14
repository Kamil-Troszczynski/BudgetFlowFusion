<template>
  <section class="plans">
    <header class="plans__header">
      <div>
        <h2>Plany zamówień publicznych</h2>
        <p>Każde dofinansowanie ma własny roczny plan kwot według kodów CPV.</p>
      </div>
      <button type="button" class="button button--secondary" @click="loadData">Odśwież</button>
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
          <span>{{ formatMoney(funding.funding_price) }} PLN</span>
        </button>
      </nav>

      <div v-if="selectedFunding" class="workspace">
        <header class="workspace__header">
          <div>
            <h3>{{ selectedFunding.funding_name }}</h3>
            <p>{{ selectedFunding.project_budget_name }}</p>
          </div>
          <dl>
            <div><dt>Dofinansowanie</dt><dd>{{ formatMoney(selectedFunding.funding_price) }} PLN</dd></div>
            <div><dt>Zaplanowano</dt><dd>{{ formatMoney(selectedPlan?.total_cost) }} PLN</dd></div>
          </dl>
        </header>

        <form v-if="!selectedPlan" class="create-plan" @submit.prevent="createPlanList">
          <div>
            <h3>Utwórz plan dla dofinansowania</h3>
            <p>Plan będzie zawierał wyłącznie kody CPV i planowane kwoty.</p>
          </div>
          <label>
            <span>Rok planu</span>
            <input v-model.number="planYear" type="number" min="2000" max="2100" required />
          </label>
          <button class="button" type="submit">Utwórz plan</button>
        </form>

        <template v-else>
          <div class="table-header">
            <div>
              <h3>{{ selectedPlan.public_plan_list_name }}</h3>
              <p>Rok {{ selectedPlan.plan_year }}</p>
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
                  <th>Planowana kwota</th>
                  <th>Wykorzystano</th>
                  <th>Pozostało</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="position in selectedPlan.public_purchase_plans" :key="position.public_purchase_plan_id">
                  <td><strong>{{ position.cpv_code }}</strong></td>
                  <td>{{ formatMoney(position.cost) }} PLN</td>
                  <td>{{ formatMoney(position.used_amount) }} PLN</td>
                  <td :class="{ negative: position.remaining_amount < 0 }">
                    {{ formatMoney(position.remaining_amount) }} PLN
                  </td>
                  <td>
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
          <h3>Nowa pozycja planu</h3>
          <button type="button" title="Zamknij" @click="closePositionModal">×</button>
        </header>
        <form @submit.prevent="createPosition">
          <label>
            <span>Kod CPV</span>
            <input v-model.number="newPosition.cpv_code" type="number" min="1" placeholder="np. 42000000" required />
          </label>
          <label>
            <span>Planowana kwota</span>
            <input v-model.number="newPosition.cost" type="number" min="0.01" step="0.01" required />
          </label>
          <footer>
            <button class="button button--secondary" type="button" @click="closePositionModal">Anuluj</button>
            <button class="button" type="submit">Dodaj</button>
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
const activeFundingId = ref(null)
const loading = ref(false)
const error = ref('')
const planYear = ref(new Date().getFullYear())
const showPositionModal = ref(false)
const newPosition = ref({ cpv_code: null, cost: null })

const selectedFunding = computed(() =>
  fundings.value.find(funding => funding.funding_id === activeFundingId.value) || fundings.value[0]
)
const selectedPlan = computed(() =>
  planLists.value.find(plan => plan.funding_id === selectedFunding.value?.funding_id) || null
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
    const [fundingsResponse, plansResponse] = await Promise.all([
      fetch(`${API_URL}/fundings?association_id=${user.value.association_id}`),
      fetch(`${API_URL}/public_purchase_plan_lists?association_id=${user.value.association_id}`)
    ])
    if (!fundingsResponse.ok || !plansResponse.ok) throw new Error('Nie udało się pobrać planów.')
    fundings.value = await fundingsResponse.json()
    planLists.value = await plansResponse.json()
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
      public_plan_list_name: `Plan ZP - ${funding.funding_name}`
    })
  })
  const data = await response.json()
  if (!response.ok) return toast.error(data.detail || 'Nie udało się utworzyć planu.')
  toast.success('Plan dofinansowania został utworzony.')
  await loadData()
}

const openPositionModal = () => {
  newPosition.value = { cpv_code: null, cost: null }
  showPositionModal.value = true
}
const closePositionModal = () => { showPositionModal.value = false }

const createPosition = async () => {
  if (!selectedPlan.value) return
  const response = await fetch(`${API_URL}/public_purchase_plans`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      public_purchase_plan_list_id: selectedPlan.value.public_purchase_plan_list_id,
      cpv_code: Number(newPosition.value.cpv_code),
      cost: Number(newPosition.value.cost)
    })
  })
  const data = await response.json()
  if (!response.ok) return toast.error(data.detail || 'Nie udało się dodać pozycji.')
  closePositionModal()
  toast.success('Pozycja CPV została dodana.')
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
.plans__header, .workspace__header, .table-header, .create-plan, .modal header, .modal footer {
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
.workspace__header { padding-bottom: 20px; border-bottom: 1px solid rgba(148, 163, 184, .16); }
dl { display: flex; gap: 24px; margin: 0; }
dt { font-size: 12px; } dd { margin: 3px 0 0; font-weight: 700; }
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
.modal-overlay { position: fixed; inset: 0; display: grid; place-items: center; background: rgba(2, 6, 23, .78); z-index: 1000; }
.modal { width: min(460px, calc(100vw - 32px)); padding: 22px; border-radius: 8px; background: #111827; }
.modal header button { border: 0; background: transparent; color: #fff; font-size: 25px; cursor: pointer; }
.modal form { display: grid; gap: 18px; margin-top: 20px; }
@media (max-width: 850px) {
  .plans__layout { grid-template-columns: 1fr; }
  .plans__header, .workspace__header, .create-plan { align-items: flex-start; flex-direction: column; }
  dl { flex-wrap: wrap; }
}
</style>
