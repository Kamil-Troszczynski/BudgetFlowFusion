<template>
  <div class="details-page-wrapper">
    <div class="list-details">
      <button class="back-btn" @click="$emit('back')">← Powrót do list</button>

      <div class="list-details__header">
        <div>
          <h2 class="list-details__title">{{ list?.name || 'Nowe zamówienie' }}</h2>
          <p class="list-details__subtitle">
            Sklep: {{ list?.shopName || 'Brak' }} | Budżet: {{ (currentTotal || 0).toFixed(2) }} / {{ (list?.maxBudget || 0).toFixed(2) }} PLN
          </p>
        </div>
        <div class="list-details__actions">
          <div class="view-toggle-container">
            <button 
              class="toggle-view-btn" 
              :class="{ 'toggle-view-btn--active': currentView === 'basic' }"
              @click="currentView = 'basic'"
            >
              Podstawowy
            </button>
            <button 
              class="toggle-view-btn" 
              :class="{ 'toggle-view-btn--active': currentView === 'detailed' }"
              @click="currentView = 'detailed'"
            >
              Szczegółowy
            </button>
          </div>
          <button v-if="isListOpen" class="add-item-btn" @click="showModal = true">+ Dodaj pozycję do listy</button>
          <button v-if="canCloseList" class="close-list-btn" @click="$emit('close-list')">Zamknij zamówienie</button>
          <span v-else-if="!isListOpen" class="closed-badge">Lista zamknięta</span>
        </div>
      </div>

      <div class="items-table-container">
        <table class="items-table" :class="`items-table--view-${currentView}`">
          <thead>
            <tr>
              <th>Nazwa przedmiotu z katalogu</th>
              <th>Cena jednostkowa</th>
              <th>Ilość sztuk</th>
              <th>Suma</th>
              <th v-if="currentView === 'detailed'">Ostatnia modyfikacja</th>
              <th v-if="canShowActions">Akcje</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in listItems" :key="item.id" :class="{ 'excel-row--editing': editingItemId === item.id }">
              <td class="font-bold excel-cell--left">{{ item.name }}</td>

              <td class="excel-cell--price">
                <template v-if="editingItemId === item.id">
                  <input 
                    v-model.number="editFormData.price" 
                    type="number" 
                    step="0.01" 
                    min="0"
                    class="excel-inline-input text-right"
                  />
                </template>
                <template v-else>
                  {{ Number(item.price).toFixed(2) }} {{ item.currency }}
                </template>
              </td>

              <td class="excel-cell--center">
                <template v-if="editingItemId === item.id">
                  <input 
                    v-model.number="editFormData.amount" 
                    type="number" 
                    min="1"
                    class="excel-inline-input text-center"
                    @keyup.enter="saveItemEdit(item)" 
                  />
                </template>
                <template v-else>
                  {{ item.amount }} szt.
                </template>
              </td>

              <td class="font-bold text-blue excel-cell--price">
                <template v-if="editingItemId === item.id">
                  {{ (editFormData.price * editFormData.amount).toFixed(2) }} {{ item.currency }}
                </template>
                <template v-else>
                  {{ Number(item.totalPrice).toFixed(2) }} {{ item.currency }}
                </template>
              </td>

              <td v-if="currentView === 'detailed'" class="excel-cell--muted text-center">
                <div v-if="item.lastEditedAt" class="excel-modification-cell">
                  <span class="excel-time-ago">{{ formatTimeAgo(item.lastEditedAt) }}</span>
                  <span v-if="item.lastEditedByName" class="excel-user-id-badge">{{ item.lastEditedByName }}</span>
                </div>
                <span v-else>-</span>
              </td>

              <td v-if="canShowActions" class="excel-cell--center">
                <div class="excel-row-actions">
                  <template v-if="editingItemId === item.id">
                    <button class="save-btn" @click="saveItemEdit(item)">Zapisz</button>
                    <button class="cancel-btn" @click="cancelEdit">X</button>
                  </template>
                  
                  <template v-else-if="canRemoveItem(item)">
                    <button class="edit-btn" @click="startEdit(item)">Edytuj</button>
                    <button class="delete-btn" @click="promptRemoveItem(item)">Usuń</button>
                  </template>
                  
                  <span v-else class="muted-action">-</span>
                </div>
              </td>
            </tr>
            <tr v-if="listItems.length === 0">
              <td :colspan="currentView === 'detailed' ? (canShowActions ? 6 : 5) : (canShowActions ? 5 : 4)" class="empty-table">
                Koszyk jest pusty. Kliknij "+ Dodaj pozycję do listy".
              </td>
            </tr>

            <tr v-if="listItems.length > 0" class="excel-summary-row">
              <td class="excel-cell--left">RAZEM (SUMA)</td>
              <td></td>
              <td class="excel-cell--center font-bold">
                {{ listItems.reduce((sum, item) => sum + item.amount, 0) }} szt.
              </td>
              <td class="font-bold excel-cell--price-total">
                {{ (currentTotal || 0).toFixed(2) }} {{ listItems[0]?.currency || 'PLN' }}
              </td>
              <td v-if="currentView === 'detailed'"></td>
              <td v-if="canShowActions"></td>
            </tr>
          </tbody>
        </table>
      </div>

      <AddItemToListModal
        v-if="isListOpen"
        :isOpen="showModal"
        :currentTotal="currentTotal"
        :maxBudget="list?.maxBudget || 0"
        @close="showModal = false"
        @add-to-list="addItemToList"
      />
    </div>

    <div v-if="showDeleteModal" class="confirm-modal-overlay" @click="showDeleteModal = false">
      <div class="confirm-modal-content" @click.stop>
        <h2 class="confirm-modal-title">Usuwanie przedmiotu</h2>
        <p class="confirm-modal-text">
          Czy na pewno chcesz usunąć tę pozycję z koszyka?
        </p>
        <div class="confirm-modal-actions">
          <button class="confirm-btn confirm-btn-cancel" @click="showDeleteModal = false">Anuluj</button>
          <button class="confirm-btn confirm-btn-danger" @click="executeRemoveItem">Tak, usuń</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AddItemToListModal from './AddItemToListModal.vue'
import { useToast } from '@/composables/useToast'
import { useAuth } from '@/composables/useAuth'

const toast = useToast()
const { user } = useAuth()
const showDeleteModal = ref(false)
const itemToDeleteId = ref(null)
const currentView = ref('basic')

const props = defineProps({
  list: {
    type: Object,
    required: true
  },
  canManageItems: {
    type: Boolean,
    default: false
  },
  canCloseList: {
    type: Boolean,
    default: false
  }
})

defineEmits(['back', 'close-list'])

const showModal = ref(false)
const listItems = ref([])
const students = ref({})
const isListOpen = computed(() => props.list?.isOpen !== false)
const canEditItems = computed(() => props.canManageItems && isListOpen.value)
const canShowActions = computed(() => {
  return isListOpen.value && (
    props.canManageItems || listItems.value.some(item => item.canRemoveByCurrentStudent)
  )
})

const currentStudentId = computed(() => user.value?.id)

const formatTimeAgo = (dateInput) => {
  if (!dateInput) return '-'
  
  const dateStr = String(dateInput).endsWith('Z') || String(dateInput).includes('+') 
    ? dateInput 
    : `${dateInput}Z`
    
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()

  if (diffMs < 0) return 'przed chwilą'

  const diffSec = Math.floor(diffMs / 1000)
  const diffMin = Math.floor(diffSec / 60)
  const diffHour = Math.floor(diffMin / 60)
  const diffDay = Math.floor(diffHour / 24)

  if (diffSec < 60) return 'przed chwilą'
  if (diffMin < 60) return `${diffMin} min temu`
  if (diffHour < 24) return `${diffHour} godz. temu`
  return `${diffDay} dni temu`
}

const fetchStudents = async () => {
  try {
    const response = await fetch('http://localhost:8080/api/students', { cache: 'no-store' })
    if (!response.ok) throw new Error('Błąd pobierania studentów')
    const data = await response.json()
    const map = {}
    ;(data || []).forEach(s => {
      const id = s.student_id ?? s.id
      const name = [s.name, s.surname].filter(Boolean).join(' ') || null
      if (id) map[id] = name || `ID: ${id}`
    })
    students.value = map
  } catch (error) {
    console.error('Błąd pobierania studentów:', error)
  }
}

const fetchListItems = async () => {
  try {
    const timestamp = new Date().getTime()
    const params = new URLSearchParams({ t: String(timestamp) })
    if (currentStudentId.value) params.set('student_id', currentStudentId.value)

    const response = await fetch(`http://localhost:8080/api/lists/${props.list.id}/items?${params.toString()}`, {
      cache: 'no-store'
    })
    if (!response.ok) throw new Error('Błąd sieci')
    const data = await response.json()
    listItems.value = data.map(item => {
      const byId = item.student_id
      return {
        ...item,
        id: item.line_item_id,
        amount: item.amount,
        totalPrice: item.total_price,
        currentStudentAmount: item.current_student_amount || 0,
        canRemoveByCurrentStudent: item.can_remove_by_current_student === true,
        lastEditedAt: item.updated_at || item.created_at,
        lastEditedById: byId,
        lastEditedByName: byId ? (students.value?.[byId] || `ID: ${byId}`) : null
      }
    })
  } catch (error) {
    console.error("Błąd pobierania przedmiotów:", error)
  }
}

const addItemToList = async (arg1, arg2) => {
  try {
    let targetItemId = null;
    let targetAmount = null;

    if (arg1 && typeof arg1 === 'object') {
      targetItemId = arg1.item_id || arg1.id;
      targetAmount = arg1.amount || arg1.quantity || 1;
    } else {
      targetItemId = arg1;
      targetAmount = arg2 || 1;
    }

    if (!targetItemId) {
      toast.error('Błąd: Formularz nie przesłał ID przedmiotu.');
      return;
    }

    const payload = {
      item_id: parseInt(targetItemId),
      amount: parseInt(targetAmount),
      student_id: currentStudentId.value
    };

    if (!payload.student_id) {
      toast.error('Błąd: Brak ID zalogowanego studenta.');
      return;
    }

    const response = await fetch(`http://localhost:8080/api/lists/${props.list.id}/items`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const errorText = await response.text();
      try {
        const errorJson = JSON.parse(errorText);
        toast.error(`Backend: ${errorJson.detail || 'Błąd zapisu'}`);
      } catch (e) {
        console.error("Zrzut błędu z FastAPI (HTML):", errorText);
        toast.error('Błąd serwera. Prawdopodobnie próbujesz dodać element do usuniętej listy.');
      }
      return;
    }

    await fetchListItems();
    toast.success('Przedmiot wylądował w koszyku!');

  } catch (error) {
    console.error("Całkowita awaria sieci:", error);
    toast.error(`Awaria sieci: ${error.message}`);
  }
}

const canRemoveItem = (item) => {
  return isListOpen.value && (props.canManageItems || item.canRemoveByCurrentStudent)
}

const promptRemoveItem = (item) => {
  if (!canRemoveItem(item)) return
  itemToDeleteId.value = item.id
  showDeleteModal.value = true
}

const executeRemoveItem = async () => {
  if (!itemToDeleteId.value) return

  try {
    const params = new URLSearchParams()
    if (currentStudentId.value) params.set('student_id', currentStudentId.value)

    const response = await fetch(`http://localhost:8080/api/lists/${props.list.id}/items/${itemToDeleteId.value}?${params.toString()}`, {
      method: 'DELETE',
    })

    if (!response.ok) {
      const err = await response.json().catch(() => ({}))
      throw new Error(err.detail || 'Błąd serwera podczas usuwania')
    }

    await fetchListItems()
    toast.info('Przedmiot usunięty z koszyka.')

  } catch (error) {
    console.error("Błąd podczas usuwania przedmiotu:", error)
    toast.error(error.message || "Wystąpił błąd. Nie udało się usunąć przedmiotu.")
  } finally {
    showDeleteModal.value = false
    itemToDeleteId.value = null
  }
}

const currentTotal = computed(() => {
  return listItems.value.reduce((sum, item) => sum + item.totalPrice, 0)
})

onMounted(async () => {
  await fetchStudents()
  await fetchListItems()
})

const editingItemId = ref(null)

const editFormData = ref({
  price: 0,
  amount: 0
})

const startEdit = (item) => {
  editingItemId.value = item.id
  editFormData.value = {
    price: item.price,
    amount: item.amount
  }
}

const cancelEdit = () => {
  editingItemId.value = null
}

const saveItemEdit = async (item) => {
  try {
    const payload = {
      item_id: item.item_id,
      price: parseFloat(editFormData.value.price),
      amount: parseInt(editFormData.value.amount),
      student_id: currentStudentId.value
    }

    const response = await fetch(`http://localhost:8080/api/lists/${props.list.id}/items/${item.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })

    if (!response.ok) {
      const err = await response.json().catch(() => ({}))
      throw new Error(err.detail || 'Nie udało się zaktualizować elementu')
    }

    toast.success('Pozycja zaktualizowana!')
    editingItemId.value = null
    await fetchListItems()
  } catch (error) {
    console.error('Błąd aktualizacji:', error)
    toast.error(error.message || 'Wystąpił błąd podczas zapisu zmian.')
  }
}
</script>

<style scoped>
.list-details { color: #ffffff; padding: 1vw 0; animation: fadeIn 0.3s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(1vh); } to { opacity: 1; transform: translateY(0); } }

.back-btn { background: none; border: none; color: #93c5fd; cursor: pointer; font-size: 1vw; margin-bottom: 2vh; font-weight: 700; transition: color 0.2s; }
.back-btn:hover { color: #ffffff; }

.list-details__header { display: flex; justify-content: space-between; align-items: center; gap: 2vw; margin-bottom: 4vh; }
.list-details__title { font-size: 2vw; color: #bfdbfe; margin: 0 0 0.5vh 0; }
.list-details__subtitle { color: rgba(226, 232, 240, 0.6); margin: 0; font-size: 1vw; font-weight: 600; }

.list-details__actions { display: flex; align-items: center; justify-content: flex-end; gap: 0.8vw; flex-wrap: wrap; }

.view-toggle-container {
  display: flex;
  background: rgba(30, 41, 59, 0.8);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 0.6vw;
  padding: 0.2vw;
  margin-right: 0.5vw;
}

.toggle-view-btn {
  background: transparent;
  border: none;
  color: #94a3b8;
  padding: 0.5vw 1vw;
  font-size: 0.85vw;
  font-weight: 700;
  border-radius: 0.4vw;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: 'Nunito', system-ui, sans-serif;
}

.toggle-view-btn--active {
  background: rgba(59, 130, 246, 0.2);
  color: #60a5fa;
}

.add-item-btn { padding: 0.8vw 1.5vw; background: linear-gradient(135deg, #3b82f6, #2563eb); border: none; border-radius: 0.8vw; color: white; font-weight: 700; cursor: pointer; font-size: 0.95vw; box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3); transition: all 0.2s; }
.add-item-btn:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4); }

.close-list-btn { padding: 0.8vw 1.3vw; background: rgba(245, 158, 11, 0.18); border: 1px solid rgba(245, 158, 11, 0.35); border-radius: 0.8vw; color: #fcd34d; font-weight: 800; cursor: pointer; font-size: 0.95vw; transition: all 0.2s; }
.close-list-btn:hover { background: rgba(245, 158, 11, 0.3); transform: translateY(-2px); }

.closed-badge { padding: 0.7vw 1vw; border-radius: 0.7vw; background: rgba(148, 163, 184, 0.14); color: #cbd5e1; font-size: 0.9vw; font-weight: 800; }

.items-table-container { 
  background: rgba(15, 23, 42, 0.4); 
  border: 1px solid rgba(148, 163, 184, 0.15); 
  border-radius: 0.8vw; 
  overflow: hidden; 
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2); 
}

.items-table { 
  width: 100%; 
  border-collapse: collapse; 
  text-align: left; 
  font-size: 0.95vw; 
}

.items-table th, .items-table td { 
  padding: 0.9vw 1.2vw; 
  border-bottom: 1px solid rgba(148, 163, 184, 0.1); 
  vertical-align: middle;
}

.items-table th { 
  background: rgba(30, 41, 59, 0.8); 
  color: #94a3b8; 
  font-weight: 700; 
  text-transform: uppercase; 
  font-size: 0.8vw; 
  letter-spacing: 0.05em; 
  border-bottom: 2px solid rgba(148, 163, 184, 0.2);
}

.items-table--view-basic th:nth-child(1) { width: 40%; text-align: left; }
.items-table--view-basic th:nth-child(2) { width: 15%; text-align: right; }
.items-table--view-basic th:nth-child(3) { width: 15%; text-align: center; }
.items-table--view-basic th:nth-child(4) { width: 15%; text-align: right; }
.items-table--view-basic th:nth-child(5) { width: 15%; text-align: center; }

.items-table--view-detailed th:nth-child(1) { width: 30%; text-align: left; }
.items-table--view-detailed th:nth-child(2) { width: 12%; text-align: right; }
.items-table--view-detailed th:nth-child(3) { width: 12%; text-align: center; }
.items-table--view-detailed th:nth-child(4) { width: 13%; text-align: right; }
.items-table--view-detailed th:nth-child(5) { width: 20%; text-align: center; }
.items-table--view-detailed th:nth-child(6) { width: 13%; text-align: center; }

.items-table tr:hover { 
  background: rgba(59, 130, 246, 0.03); 
}

.excel-cell--left {
  text-align: left;
}

.excel-cell--center {
  text-align: center;
}

.excel-cell--price {
  text-align: right;
  font-family: monospace;
  font-size: 1vw;
  color: #e2e8f0;
}

.excel-cell--muted {
  color: #64748b;
  font-size: 0.85vw;
}

.excel-modification-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.2vw;
}

.excel-time-ago {
  font-size: 0.85vw;
  color: #94a3b8;
}

.excel-user-id-badge {
  display: inline-block;
  padding: 0.15vw 0.4vw;
  background: rgba(59, 130, 246, 0.12);
  color: #60a5fa;
  border-radius: 0.3vw;
  font-size: 0.75vw;
  font-weight: 700;
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.excel-summary-row {
  background: rgba(30, 41, 59, 0.5) !important;
}

.excel-summary-row td {
  border-top: 2px solid rgba(148, 163, 184, 0.3);
  border-bottom: 2px double rgba(148, 163, 184, 0.4) !important;
  color: #94a3b8;
  font-weight: 700;
  font-size: 0.9vw;
}

.excel-cell--price-total {
  text-align: right;
  font-family: monospace;
  font-size: 1.1vw;
  color: #38bdf8 !important;
}

.excel-inline-input {
  width: 100%;
  box-sizing: border-box;
  background: #1e293b;
  border: 1px solid #3b82f6;
  border-radius: 0.3vw;
  color: #ffffff;
  padding: 0.3vw 0.5vw;
  font-family: monospace;
  font-size: 0.95vw;
  outline: none;
}

.excel-inline-input:focus {
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.4);
}

.text-right { text-align: right; }
.text-center { text-align: center; }

.excel-row--editing {
  background: rgba(59, 130, 246, 0.08) !important;
}

.excel-row-actions {
  display: flex;
  gap: 0.4vw;
  justify-content: center;
}

.edit-btn {
  background: rgba(16, 185, 129, 0.15);
  color: #34d399;
  border: 1px solid rgba(16, 185, 129, 0.3);
  padding: 0.4vw 0.8vw;
  border-radius: 0.4vw;
  font-size: 0.8vw;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}
.edit-btn:hover { background: rgba(16, 185, 129, 0.3); }

.save-btn {
  background: rgba(52, 211, 153, 0.15);
  color: #34d399;
  border: 1px solid rgba(52, 211, 153, 0.3);
  padding: 0.4vw 0.8vw;
  border-radius: 0.4vw;
  font-size: 0.8vw;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}
.save-btn:hover { background: rgba(52, 211, 153, 0.3); }

.cancel-btn {
  background: #475569;
  color: #ffffff;
  border: none;
  padding: 0.4vw 0.6vw;
  border-radius: 0.4vw;
  font-size: 0.8vw;
  font-weight: 700;
  cursor: pointer;
}
.cancel-btn:hover { background: #64748b; }

.font-bold { font-weight: 700; }
.text-blue { color: #60a5fa; }
.empty-table { text-align: center; color: rgba(226, 232, 240, 0.5); padding: 4vw; font-style: italic; }

.delete-btn { background: rgba(239, 68, 68, 0.15); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.3); padding: 0.4vw 0.8vw; border-radius: 0.4vw; font-size: 0.8vw; font-weight: 700; cursor: pointer; transition: all 0.2s; }
.delete-btn:hover { background: rgba(239, 68, 68, 0.3); }
.muted-action { color: rgba(226, 232, 240, 0.03); font-size: 0.9vw; }

.confirm-modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background-color: rgba(5, 8, 22, 0.85); display: flex; align-items: center; justify-content: center; z-index: 9999; backdrop-filter: blur(8px); }
.confirm-modal-content { background: #0f172a; border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 1.5vw; padding: 3vw; width: 90%; max-width: 32vw; text-align: center; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7); animation: modalPop 0.3s cubic-bezier(0.34, 1.56, 0.64, 1); }
@keyframes modalPop { 0% { transform: scale(0.9); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }
.confirm-modal-icon { font-size: 3.5vw; margin-bottom: 1vw; filter: drop-shadow(0 0 10px rgba(245, 158, 11, 0.5)); }
.confirm-modal-title { color: #ef4444; font-size: 2vw; font-weight: 800; margin: 0 0 1vw 0; }
.confirm-modal-text { color: #e2e8f0; font-size: 1.1vw; line-height: 1.6; margin-bottom: 2.5vw; }
.confirm-modal-actions { display: flex; gap: 1.5vw; justify-content: center; }
.confirm-btn { padding: 0.9vw 2.5vw; border-radius: 0.8vw; font-size: 1.1vw; font-weight: 800; cursor: pointer; border: none; transition: all 0.2s ease; }
.confirm-btn-cancel { background: rgba(148, 163, 184, 0.15); color: #e2e8f0; }
.confirm-btn-cancel:hover { background: rgba(148, 163, 184, 0.3); color: #ffffff; }
.confirm-btn-danger { background: linear-gradient(135deg, #ef4444, #dc2626); color: #ffffff; box-shadow: 0 10px 20px rgba(239, 68, 68, 0.3); }
.confirm-btn-danger:hover { transform: translateY(-0.3vh); filter: brightness(1.1); box-shadow: 0 14px 28px rgba(239, 68, 68, 0.5); }
</style>