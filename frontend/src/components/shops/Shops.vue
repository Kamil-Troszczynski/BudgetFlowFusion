<template>
  <div class="shops-view">
    <div class="shops-view__header">
      <div>
        <p class="shops-view__eyebrow">Baza dostawców</p>
        <h2>Sklepy</h2>
        <p>Dodawaj sklepy do historii zakupów. Do koszyków trafią dopiero po akceptacji skarbnika.</p>
      </div>
      <button class="shops-primary-btn" type="button" @click="openCreateModal">Dodaj sklep</button>
    </div>

    <div class="shops-toolbar">
      <label class="shops-filter shops-filter--search">
        <span>Szukaj</span>
        <input
          v-model="search"
          class="shops-input"
          type="text"
          placeholder="Nazwa, link albo opinia..."
        />
      </label>
      <button class="shops-secondary-btn" type="button" @click="fetchShops">Odśwież</button>
    </div>

    <div class="shops-summary">
      <div>
        <span>Zaakceptowane</span>
        <strong>{{ approvedShops.length }}</strong>
      </div>
      <div>
        <span>Oczekujące</span>
        <strong>{{ pendingShops.length }}</strong>
      </div>
      <div>
        <span>Widoczne</span>
        <strong>{{ filteredShops.length }}</strong>
      </div>
    </div>

    <div class="shops-table-wrap">
      <table class="shops-table">
        <thead>
          <tr>
            <th>Nazwa</th>
            <th>Status</th>
            <th>Link</th>
            <th>Opinia</th>
            <th>Darmowa dostawa</th>
            <th v-if="isTreasurer">Akcje</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="shop in filteredShops" :key="shop.shop_id">
            <td class="shops-name">{{ shop.shop_name }}</td>
            <td>
              <span class="shops-status" :class="`shops-status--${shop.status || 'approved'}`">
                {{ statusLabel(shop.status) }}
              </span>
            </td>
            <td>
              <a v-if="shop.link" :href="shop.link" target="_blank" rel="noreferrer" class="shops-link">
                {{ compactLink(shop.link) }}
              </a>
              <span v-else>-</span>
            </td>
            <td class="shops-opinion">{{ shop.opinion || '-' }}</td>
            <td>{{ formatMoney(shop.free_delivery_threshold) }} PLN</td>
            <td v-if="isTreasurer">
              <div class="shops-actions">
                <button class="shops-action-btn" type="button" @click="openEditModal(shop)">Edytuj</button>
                <button
                  v-if="shop.status === 'pending'"
                  class="shops-action-btn shops-action-btn--approve"
                  type="button"
                  @click="approveShop(shop)"
                >
                  Akceptuj
                </button>
                <button
                  v-if="shop.status === 'pending'"
                  class="shops-action-btn shops-action-btn--reject"
                  type="button"
                  @click="rejectShop(shop)"
                >
                  Odrzuć
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="!filteredShops.length">
            <td :colspan="isTreasurer ? 6 : 5" class="shops-empty">Brak sklepów dla wybranych filtrów.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showModal" class="shops-modal-overlay" @click="closeModal">
      <div class="shops-modal" @click.stop>
        <div class="shops-modal__header">
          <h3>{{ editingShop ? 'Edytuj sklep' : 'Dodaj sklep' }}</h3>
          <button type="button" class="shops-modal__close" @click="closeModal">x</button>
        </div>

        <form class="shops-form" @submit.prevent="submitShop">
          <label class="shops-form__group">
            <span>Nazwa</span>
            <input v-model="form.shop_name" class="shops-input" type="text" required />
          </label>
          <label class="shops-form__group">
            <span>Link</span>
            <input v-model="form.link" class="shops-input" type="url" placeholder="https://..." />
          </label>
          <label class="shops-form__group">
            <span>Opinia</span>
            <textarea v-model="form.opinion" class="shops-input" rows="4" placeholder="Krótka opinia o sklepie"></textarea>
          </label>
          <label class="shops-form__group">
            <span>Próg darmowej dostawy</span>
            <input
              v-model.number="form.free_delivery_threshold"
              class="shops-input"
              type="number"
              min="0"
              step="0.01"
              required
            />
          </label>

          <div class="shops-modal__actions">
            <button type="button" class="shops-secondary-btn" @click="closeModal">Anuluj</button>
            <button type="submit" class="shops-primary-btn" :disabled="isSaving">
              {{ isSaving ? 'Zapisywanie...' : editingShop ? 'Zapisz zmiany' : 'Zgłoś sklep' }}
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

const { user } = useAuth()
const toast = useToast()

const shops = ref([])
const search = ref('')
const showModal = ref(false)
const editingShop = ref(null)
const isSaving = ref(false)

const emptyForm = () => ({
  shop_name: '',
  link: '',
  opinion: '',
  free_delivery_threshold: 0
})

const form = ref(emptyForm())

const isTreasurer = computed(() => user.value?.role === 'treasurer')
const currentStudentId = computed(() => user.value?.id)

const normalize = value => String(value || '').toLowerCase().trim()

const filteredShops = computed(() => {
  const query = normalize(search.value)
  return shops.value.filter(shop => {
    const text = normalize([shop.shop_name, shop.link, shop.opinion, shop.status].filter(Boolean).join(' '))
    return !query || text.includes(query)
  })
})

const approvedShops = computed(() => shops.value.filter(shop => (shop.status || 'approved') === 'approved'))
const pendingShops = computed(() => shops.value.filter(shop => shop.status === 'pending'))

const statusLabel = status => {
  if (status === 'pending') return 'Oczekuje'
  if (status === 'rejected') return 'Odrzucony'
  return 'Zaakceptowany'
}

const compactLink = value => {
  try {
    return new URL(value).hostname.replace(/^www\./, '')
  } catch {
    return value
  }
}

const formatMoney = value => Number(value || 0).toLocaleString('pl-PL', {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2
})

const fetchShops = async () => {
  try {
    const response = await fetch('http://localhost:8080/api/shops?include_pending=true', { cache: 'no-store' })
    if (!response.ok) throw new Error('Nie udało się pobrać sklepów')
    shops.value = await response.json()
  } catch (error) {
    console.error(error)
    toast.error('Nie udało się pobrać sklepów')
  }
}

const openCreateModal = () => {
  editingShop.value = null
  form.value = emptyForm()
  showModal.value = true
}

const openEditModal = shop => {
  editingShop.value = shop
  form.value = {
    shop_name: shop.shop_name || '',
    link: shop.link || '',
    opinion: shop.opinion || '',
    free_delivery_threshold: Number(shop.free_delivery_threshold || 0)
  }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingShop.value = null
  form.value = emptyForm()
  isSaving.value = false
}

const submitShop = async () => {
  if (isSaving.value) return
  isSaving.value = true
  try {
    const payload = {
      ...form.value,
      student_id: currentStudentId.value,
      free_delivery_threshold: Number(form.value.free_delivery_threshold || 0)
    }
    const url = editingShop.value
      ? `http://localhost:8080/api/shops/${editingShop.value.shop_id}`
      : 'http://localhost:8080/api/shops'
    const response = await fetch(url, {
      method: editingShop.value ? 'PATCH' : 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    if (!response.ok) {
      const error = await response.json().catch(() => ({}))
      throw new Error(error.detail || 'Nie udało się zapisać sklepu')
    }
    toast.success(editingShop.value ? 'Zapisano sklep' : 'Sklep czeka na akceptację skarbnika')
    closeModal()
    await fetchShops()
  } catch (error) {
    console.error(error)
    toast.error(error.message || 'Nie udało się zapisać sklepu')
    isSaving.value = false
  }
}

const approveShop = async shop => {
  try {
    const response = await fetch(`http://localhost:8080/api/shops/${shop.shop_id}/approve`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ student_id: currentStudentId.value })
    })
    if (!response.ok) {
      const error = await response.json().catch(() => ({}))
      throw new Error(error.detail || 'Nie udało się zaakceptować sklepu')
    }
    toast.success('Sklep zaakceptowany')
    await fetchShops()
  } catch (error) {
    console.error(error)
    toast.error(error.message || 'Nie udało się zaakceptować sklepu')
  }
}

const rejectShop = async shop => {
  try {
    const params = new URLSearchParams({ student_id: String(currentStudentId.value) })
    const response = await fetch(`http://localhost:8080/api/shops/${shop.shop_id}/reject?${params.toString()}`, {
      method: 'DELETE'
    })
    if (!response.ok) {
      const error = await response.json().catch(() => ({}))
      throw new Error(error.detail || 'Nie udało się odrzucić sklepu')
    }
    toast.success('Sklep odrzucony')
    await fetchShops()
  } catch (error) {
    console.error(error)
    toast.error(error.message || 'Nie udało się odrzucić sklepu')
  }
}

onMounted(fetchShops)
</script>

<style scoped>
.shops-view {
  display: grid;
  gap: 1.4vw;
  width: 100%;
  padding: 2vh 0;
  color: #e2e8f0;
  font-family: 'Nunito', system-ui, sans-serif;
}

.shops-view__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 2vw;
  padding-bottom: 1.2vw;
  border-bottom: 0.08vw solid rgba(148, 163, 184, 0.16);
}

.shops-view__header h2 {
  margin: 0 0 0.5vw;
  color: #bfdbfe;
  font-size: 2vw;
  font-weight: 800;
}

.shops-view__header p {
  margin: 0;
  color: rgba(226, 232, 240, 0.64);
  font-size: 1vw;
  line-height: 1.5;
}

.shops-view__eyebrow {
  margin: 0 0 0.35vw 0 !important;
  color: #93c5fd !important;
  font-size: 0.78vw !important;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.shops-toolbar {
  display: grid;
  grid-template-columns: minmax(22vw, 1fr) auto;
  align-items: end;
  gap: 0.9vw;
  padding: 1vw;
  border: 0.08vw solid rgba(148, 163, 184, 0.15);
  border-radius: 0.9vw;
  background: rgba(15, 23, 42, 0.5);
}

.shops-filter,
.shops-form__group {
  display: grid;
  gap: 0.45vw;
}

.shops-filter span,
.shops-form__group span {
  color: rgba(226, 232, 240, 0.68);
  font-size: 0.8vw;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.shops-input {
  width: 100%;
  padding: 0.8vw 0.9vw;
  border: 0.08vw solid rgba(148, 163, 184, 0.22);
  border-radius: 0.65vw;
  background: rgba(15, 23, 42, 0.68);
  color: #ffffff;
  font-size: 0.92vw;
  font-family: inherit;
  box-sizing: border-box;
}

.shops-input:focus {
  outline: none;
  border-color: rgba(96, 165, 250, 0.62);
  background: rgba(15, 23, 42, 0.92);
}

.shops-summary {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1vw;
}

.shops-summary > div {
  display: grid;
  gap: 0.45vw;
  padding: 1vw;
  border: 0.08vw solid rgba(148, 163, 184, 0.16);
  border-radius: 0.8vw;
  background: rgba(15, 23, 42, 0.56);
}

.shops-summary span {
  color: rgba(226, 232, 240, 0.62);
  font-size: 0.82vw;
  font-weight: 700;
}

.shops-summary strong {
  color: #ffffff;
  font-size: 1.25vw;
}

.shops-table-wrap {
  overflow-x: auto;
  border: 0.08vw solid rgba(148, 163, 184, 0.16);
  border-radius: 0.9vw;
  background: rgba(15, 23, 42, 0.42);
  box-shadow: 0 1.2vw 3vw rgba(0, 0, 0, 0.18);
}

.shops-table {
  width: 100%;
  min-width: 980px;
  border-collapse: collapse;
}

.shops-table th,
.shops-table td {
  padding: 0.9vw 1vw;
  border-bottom: 0.08vw solid rgba(148, 163, 184, 0.1);
  text-align: left;
  font-size: 0.88vw;
  vertical-align: middle;
}

.shops-table th {
  background: rgba(30, 41, 59, 0.76);
  color: #93c5fd;
  font-size: 0.72vw;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  white-space: nowrap;
}

.shops-name {
  color: #ffffff;
  font-weight: 800;
}

.shops-opinion {
  max-width: 24vw;
  color: rgba(226, 232, 240, 0.78);
}

.shops-status {
  display: inline-flex;
  padding: 0.32vw 0.6vw;
  border-radius: 999px;
  font-size: 0.78vw;
  font-weight: 800;
}

.shops-status--approved {
  border: 0.08vw solid rgba(34, 197, 94, 0.24);
  background: rgba(34, 197, 94, 0.12);
  color: #bbf7d0;
}

.shops-status--pending {
  border: 0.08vw solid rgba(245, 158, 11, 0.24);
  background: rgba(245, 158, 11, 0.12);
  color: #fcd34d;
}

.shops-link {
  color: #60a5fa;
  font-weight: 800;
  text-decoration: none;
}

.shops-actions,
.shops-modal__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.55vw;
}

.shops-primary-btn,
.shops-secondary-btn,
.shops-action-btn {
  border: 0.08vw solid rgba(96, 165, 250, 0.35);
  border-radius: 0.6vw;
  background: rgba(59, 130, 246, 0.16);
  color: #93c5fd;
  padding: 0.75vw 1.2vw;
  font-weight: 800;
  font-size: 0.9vw;
  cursor: pointer;
  font-family: inherit;
}

.shops-primary-btn {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: #ffffff;
}

.shops-secondary-btn {
  background: rgba(148, 163, 184, 0.1);
  color: #e2e8f0;
}

.shops-action-btn {
  padding: 0.45vw 0.75vw;
  font-size: 0.78vw;
}

.shops-action-btn--approve {
  border-color: rgba(34, 197, 94, 0.35);
  background: rgba(34, 197, 94, 0.14);
  color: #86efac;
}

.shops-action-btn--reject {
  border-color: rgba(239, 68, 68, 0.35);
  background: rgba(239, 68, 68, 0.14);
  color: #fca5a5;
}

.shops-empty {
  color: rgba(226, 232, 240, 0.64);
  text-align: center;
  padding: 2vw !important;
}

.shops-modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: rgba(5, 8, 22, 0.82);
  backdrop-filter: blur(4px);
}

.shops-modal {
  width: min(100%, 620px);
  max-height: 90vh;
  overflow-y: auto;
  padding: 28px;
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: 14px;
  background: #0f172a;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6);
}

.shops-modal__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(59, 130, 246, 0.2);
}

.shops-modal__header h3 {
  margin: 0;
  color: #bfdbfe;
  font-size: 22px;
}

.shops-modal__close {
  border: 0;
  background: none;
  color: rgba(226, 232, 240, 0.7);
  font-size: 22px;
  cursor: pointer;
}

.shops-form {
  display: grid;
  gap: 16px;
}

.shops-modal__actions {
  justify-content: flex-end;
  padding-top: 16px;
  border-top: 1px solid rgba(59, 130, 246, 0.2);
}

@media (max-width: 900px) {
  .shops-view__header,
  .shops-toolbar,
  .shops-summary {
    grid-template-columns: 1fr;
  }

  .shops-view__header {
    display: grid;
  }

  .shops-view__header h2 {
    font-size: 24px;
  }

  .shops-view__header p,
  .shops-input,
  .shops-table th,
  .shops-table td,
  .shops-primary-btn,
  .shops-secondary-btn {
    font-size: 14px;
  }

  .shops-view__eyebrow,
  .shops-filter span,
  .shops-form__group span,
  .shops-status,
  .shops-action-btn {
    font-size: 12px !important;
  }

  .shops-summary strong {
    font-size: 18px;
  }

  .shops-toolbar,
  .shops-summary > div {
    padding: 14px;
    border-radius: 10px;
  }

  .shops-table th,
  .shops-table td {
    padding: 12px 14px;
  }

  .shops-modal {
    padding: 20px;
  }

  .shops-modal__actions {
    display: grid;
  }
}
</style>
