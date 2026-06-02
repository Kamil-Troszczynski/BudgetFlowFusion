<template>
  <div class="requests-container">
    <template v-if="!activeRequest">
      <div class="requests-section">
        <div class="requests-header">
          <div class="requests-title-section">
            <h2 class="requests-title">Moje wnioski o zamówienie</h2>
            <p class="requests-subtitle">Wnioski zakupowe, które utworzyłeś</p>
          </div>
          <button class="requests-add-button" @click="showAddRequestModal = true">+ Nowy wniosek</button>
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
                <span class="request-card__value">{{ request.budget }} PLN</span>
              </p>
              <p class="request-card__detail">
                <span class="request-card__label">Typ:</span>
                <span class="request-card__value">{{ request.ifService ? 'Usługa' : 'Produkt' }}</span>
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
                <span class="request-card__value">{{ request.budget }} PLN</span>
              </p>
              <p class="request-card__detail">
                <span class="request-card__label">Typ:</span>
                <span class="request-card__value">{{ request.ifService ? 'Usługa' : 'Produkt' }}</span>
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
            <p>Budżet</p>
            <strong>{{ activeRequest.budget }} PLN</strong>
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
            <label class="modal-form__label">Budżet (PLN)</label>
            <input
              v-model="newRequestData.budget_allocated_for_the_order"
              type="number"
              placeholder="0.00"
              class="modal-form__input"
              required
            />
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
            <button type="submit" class="modal-btn modal-btn-save">Utwórz wniosek</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useAuth } from '@/composables/useAuth'

const { user } = useAuth()
const activeRequest = ref(null)
const showAddRequestModal = ref(false)

const userRequests = ref([])
const allRequests = ref([])

const newRequestData = ref({
  purchase_request_name: '',
  budget_allocated_for_the_order: null,
  if_service: false,
  used_cpv_id: 1,
  association_budget_id: 1,
  association_name: '',
  can_add: true
})

const mapRequest = (req) => ({
  id: req.purchase_request_id,
  name: req.purchase_request_name,
  budget: req.budget_allocated_for_the_order,
  ifService: req.if_service,
  status: req.can_add ? 'pending' : 'approved',
  created_at: req.created_at,
  used_cpv_id: req.used_cpv_id,
  itemCount: 0
})

const fetchRequests = async () => {
  try {
    const response = await fetch(`http://localhost:8080/api/purchase_requests`)
    if (!response.ok) throw new Error('Błąd pobierania danych')

    const data = await response.json()
    allRequests.value = data.map(mapRequest)
  } catch (error) {
    console.error('Błąd pobierania wniosków:', error)
  }
}

const fetchRequestsBySpecificProjectFinanceManager = async () => {
  if (!user.value?.id) return

  try {
    const response = await fetch(`http://localhost:8080/api/purchase_requests/${user.value.id}`)
    if (!response.ok) throw new Error('Błąd pobierania danych')

    const data = await response.json()
    userRequests.value = data.map(mapRequest)
  } catch (error) {
    console.error('Błąd pobierania wniosków dla managera:', error)
  }
}

const handleNewRequest = async () => {
  if (!user.value?.id) {
    alert("Błąd: Nie można utworzyć wniosku, brak ID użytkownika.")
    return
  }

  try {
    const payload = {
      purchase_request_name: newRequestData.value.purchase_request_name,
      budget_allocated_for_the_order: newRequestData.value.budget_allocated_for_the_order,
      if_service: newRequestData.value.if_service,
      used_cpv_id: newRequestData.value.used_cpv_id,
      association_budget_id: newRequestData.value.association_budget_id,
      created_at: new Date().toISOString(),
      can_add: newRequestData.value.can_add,
      project_finance_manager_id: user.value.id // <-- Dodane przekazywanie ID skarbnika
    }

    const response = await fetch('http://localhost:8080/api/create_purchase_requests', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })

    if (!response.ok) {
      const error = await response.json()
      alert(`Błąd przy dodawaniu wniosku: ${error.detail || 'Nieznany błąd'}`)
      return
    }

    const createdRequest = await response.json()
    
    // Resetuj formularz i zamknij modal
    newRequestData.value.purchase_request_name = ''
    newRequestData.value.budget_allocated_for_the_order = null
    showAddRequestModal.value = false

    // Odśwież listy
    fetchRequests()
    fetchRequestsBySpecificProjectFinanceManager()

  } catch (error) {
    console.error('Błąd przy dodawaniu wniosku:', error)
  }
}

const deleteRequest = async (id) => {
  if (!confirm('Czy na pewno chcesz usunąć ten wniosek?')) return

  try {
    const response = await fetch(`http://localhost:8080/api/purchase_requests/${id}`, { method: 'DELETE' })
    if (response.ok) {
      userRequests.value = userRequests.value.filter(r => r.id !== id)
      allRequests.value = allRequests.value.filter(r => r.id !== id)
      
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

const formatDate = (dateStr) => {
  if (!dateStr) return '—'
  return new Intl.DateTimeFormat('pl-PL').format(new Date(dateStr))
}

onMounted(() => {
  fetchRequests()
})

// Obserwujemy ID użytkownika i pobieramy dane, gdy jest dostępne
watch(
  () => user.value?.id,
  (newId) => {
    if (newId) {
      fetchRequestsBySpecificProjectFinanceManager()
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
  margin-top: 1vw;
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
</style>