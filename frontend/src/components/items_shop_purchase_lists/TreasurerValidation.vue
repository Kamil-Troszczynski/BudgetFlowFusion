<template>
  <div class="validation-section">
    <div class="validation-header">
      <div>
        <h2 class="validation-title">Panel Skarbnika</h2>
        <p class="validation-subtitle">Weryfikacja przedmiotów i zarządzanie kategoriami CPV</p>
      </div>
      <div class="stats-badges">
        <button class="action-btn accept" @click="showCategoryModal = true" style="background: rgba(59, 130, 246, 0.2); color: #93c5fd; border-color: rgba(59, 130, 246, 0.3);">
          + Zarządzaj CPV
        </button>
      </div>
    </div>

    <div class="tab-bar">
      <button
        :class="['tab-btn', { active: activeTab === 'items' }]"
        @click="activeTab = 'items'"
      >
        Akceptacja przedmiotów
        <span class="tab-badge" v-if="pendingItems.length > 0">{{ pendingItems.length }}</span>
      </button>
      <button
        :class="['tab-btn', { active: activeTab === 'subcategories' }]"
        @click="activeTab = 'subcategories'"
      >
        Oczekujące podkategorie
        <span class="tab-badge subcategory-badge" v-if="pendingSubcategories.length > 0">{{ pendingSubcategories.length }}</span>
      </button>
    </div>

    <!-- Items tab -->
    <div v-if="activeTab === 'items'">
      <div class="search-bar-wrapper">
        <input
          v-model="itemSearch"
          type="text"
          placeholder="Szukaj po nazwie przedmiotu lub zgłaszającym..."
          class="search-input"
        />
      </div>

      <div v-if="filteredPendingItems.length === 0" class="validation-empty">
        <p class="empty-icon"></p>
        <p class="empty-text">{{ pendingItems.length === 0 ? 'Wszystkie przedmioty zostały zweryfikowane!' : 'Brak wyników dla podanej frazy.' }}</p>
        <p class="empty-subtext">{{ pendingItems.length === 0 ? 'Dobra robota, katalog jest aktualny.' : 'Spróbuj zmienić wyszukiwanie.' }}</p>
      </div>

      <div v-else class="table-container">
        <table class="validation-table">
          <thead>
            <tr>
              <th>Nazwa przedmiotu</th>
              <th>Zgłaszający</th>
              <th>Cena bazowa</th>
              <th>Podkategoria</th>
              <th>Link</th>
              <th>Akcje</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in filteredPendingItems" :key="item.id">
              <td class="item-name">{{ item.name }}</td>
              <td class="item-student">{{ item.addedBy }}</td>
              <td class="item-price">{{ item.price }} {{ item.currency }}</td>
              <td class="item-cpv">
                <div class="cpv-info">
                  <span class="category">{{ item.subcategoryName }}</span>
                  <span class="cpv-code" v-if="item.cpvCode !== 'N/A'">CPV: {{ item.cpvCode }}</span>
                </div>
              </td>
              <td>
                <a :href="item.link" target="_blank" class="link-btn">Sprawdź sklep ↗</a>
              </td>
              <td class="actions-cell">
                <button class="action-btn accept" @click="handleAccept(item.id)">✓ Akceptuj</button>
                <button class="action-btn reject" @click="promptReject(item.id)">✕ Odrzuć</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Pending subcategories tab -->
    <div v-if="activeTab === 'subcategories'">
      <div class="search-bar-wrapper">
        <input
          v-model="subcategorySearch"
          type="text"
          placeholder="Szukaj po nazwie podkategorii..."
          class="search-input"
        />
      </div>

      <div v-if="filteredPendingSubcategories.length === 0" class="validation-empty">
        <p class="empty-icon"></p>
        <p class="empty-text">{{ pendingSubcategories.length === 0 ? 'Brak oczekujących podkategorii!' : 'Brak wyników dla podanej frazy.' }}</p>
        <p class="empty-subtext">{{ pendingSubcategories.length === 0 ? 'Żaden student nie zgłosił nowej podkategorii.' : 'Spróbuj zmienić wyszukiwanie.' }}</p>
      </div>

      <div v-else class="table-container">
        <table class="validation-table">
          <thead>
            <tr>
              <th>Nazwa podkategorii</th>
              <th>Przypisz kategorię CPV</th>
              <th>Akcja</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="subcat in filteredPendingSubcategories" :key="subcat.product_subcategory_id">
              <td class="item-name">{{ subcat.product_subcategory_name }}</td>
              <td>
                <select
                  v-model="assignSelections[subcat.product_subcategory_id]"
                  class="category-select"
                >
                  <option value="" disabled>Wybierz kategorię...</option>
                  <option v-for="cat in dbCategories" :key="cat.id" :value="cat.id">
                    {{ cat.name }} (CPV: {{ cat.cpv }})
                  </option>
                </select>
              </td>
              <td class="actions-cell">
                <button
                  class="action-btn accept"
                  :disabled="!assignSelections[subcat.product_subcategory_id]"
                  @click="assignCategory(subcat.product_subcategory_id)"
                >
                  ✓ Zatwierdź
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <AddCategoryModal
    :isOpen="showCategoryModal"
    :existingCategories="dbCategories"
    @close="showCategoryModal = false"
    @refresh-categories="fetchCategoriesFromDB"
  />

  <div v-if="showRejectModal" class="confirm-modal-overlay" @click="showRejectModal = false">
    <div class="confirm-modal-content" @click.stop>
      <div class="confirm-modal-icon"></div>
      <h2 class="confirm-modal-title">Uwaga!</h2>
      <p class="confirm-modal-text">Czy na pewno chcesz odrzucić ten przedmiot?</p>
      <div class="confirm-modal-actions">
        <button class="confirm-btn confirm-btn-cancel" @click="showRejectModal = false">Anuluj</button>
        <button class="confirm-btn confirm-btn-danger" @click="executeReject">Tak, odrzuć</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AddCategoryModal from './AddCategoryModal.vue'
import { useAuth } from '@/composables/useAuth'
import { useToast } from '@/composables/useToast'

const toast = useToast()
const { user } = useAuth()

const activeTab = ref('items')
const pendingItems = ref([])
const pendingSubcategories = ref([])
const dbCategories = ref([])
const showCategoryModal = ref(false)
const showRejectModal = ref(false)
const itemToRejectId = ref(null)
const itemSearch = ref('')
const subcategorySearch = ref('')
const assignSelections = ref({})

const filteredPendingItems = computed(() => {
  const q = itemSearch.value.toLowerCase().trim()
  if (!q) return pendingItems.value
  return pendingItems.value.filter(i =>
    i.name.toLowerCase().includes(q) || i.addedBy.toLowerCase().includes(q)
  )
})

const filteredPendingSubcategories = computed(() => {
  const q = subcategorySearch.value.toLowerCase().trim()
  if (!q) return pendingSubcategories.value
  return pendingSubcategories.value.filter(s =>
    s.product_subcategory_name.toLowerCase().includes(q)
  )
})

const fetchCategoriesFromDB = async () => {
  try {
    const response = await fetch('http://localhost:8080/api/categories')
    if (response.ok) {
      const data = await response.json()
      dbCategories.value = data.map(c => ({
        id: c.product_category_id,
        name: c.product_category_name || c.name,
        cpv: c.cpv || c.cpv_code
      }))
    }
  } catch (error) {
    console.error('Błąd pobierania kategorii', error)
  }
}

const fetchPendingItems = async () => {
  try {
    const associationId = user.value.associationId || user.value.association_id
    const response = await fetch(`http://localhost:8080/api/items/pending?association_id=${associationId}`)
    if (!response.ok) throw new Error('Błąd sieci')
    const data = await response.json()

    pendingItems.value = data.map(item => {
      const subcat = item.product_subcategory
      const cat = subcat?.product_category
      return {
        id: item.item_id,
        name: item.name,
        addedBy: item.student?.name || 'Użytkownik',
        price: item.price,
        currency: item.currency || 'PLN',
        subcategoryName: subcat?.product_subcategory_name || 'Niezaklasyfikowane',
        cpvCode: cat?.cpv || 'N/A',
        link: item.link || '#'
      }
    })
  } catch (error) {
    console.error("Błąd pobierania oczekujących:", error)
  }
}

const fetchPendingSubcategories = async () => {
  try {
    const response = await fetch('http://localhost:8080/api/subcategories/pending')
    if (response.ok) {
      pendingSubcategories.value = await response.json()
    }
  } catch (error) {
    console.error('Błąd pobierania oczekujących podkategorii', error)
  }
}

onMounted(async () => {
  await fetchCategoriesFromDB()
  await Promise.all([fetchPendingItems(), fetchPendingSubcategories()])
})

const handleAccept = async (itemId) => {
  try {
    const response = await fetch(`http://localhost:8080/api/items/${itemId}/approve`, { method: 'PATCH' })
    if (!response.ok) throw new Error('Błąd serwera przy akceptacji')
    toast.success('Przedmiot został pomyślnie dodany do katalogu!')
    await fetchPendingItems()
  } catch (error) {
    toast.error('Wystąpił błąd podczas akceptacji przedmiotu.')
  }
}

const promptReject = (itemId) => {
  itemToRejectId.value = itemId
  showRejectModal.value = true
}

const executeReject = async () => {
  if (!itemToRejectId.value) return
  try {
    const response = await fetch(`http://localhost:8080/api/items/${itemToRejectId.value}/reject`, { method: 'DELETE' })
    if (!response.ok) throw new Error('Błąd serwera przy odrzucaniu')
    toast.info('Przedmiot został odrzucony')
    await fetchPendingItems()
  } catch (error) {
    toast.error('Wystąpił błąd podczas odrzucania przedmiotu')
  } finally {
    showRejectModal.value = false
    itemToRejectId.value = null
  }
}

const assignCategory = async (subcategoryId) => {
  const categoryId = assignSelections.value[subcategoryId]
  if (!categoryId) return

  try {
    const response = await fetch(`http://localhost:8080/api/subcategories/${subcategoryId}/assign-category`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ product_category_id: categoryId })
    })

    if (!response.ok) throw new Error('Błąd serwera')

    toast.success('Kategoria została przypisana do podkategorii!')
    delete assignSelections.value[subcategoryId]
    await fetchPendingSubcategories()
  } catch (error) {
    toast.error('Wystąpił błąd podczas przypisywania kategorii.')
  }
}
</script>

<style scoped>
.validation-section {
  color: #ffffff;
  padding: 1vw 0;
}

.validation-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2vw;
}

.validation-title {
  font-size: 1.8vw;
  color: #bfdbfe;
  margin: 0 0 0.5vw 0;
}

.validation-subtitle {
  color: rgba(226, 232, 240, 0.6);
  margin: 0;
  font-size: 0.95vw;
}

.stats-badges {
  display: flex;
  gap: 1vw;
  align-items: center;
}

.tab-bar {
  display: flex;
  gap: 0.5vw;
  margin-bottom: 2vw;
  background: rgba(15, 23, 42, 0.5);
  padding: 0.5vw;
  border-radius: 0.8vw;
  border: 1px solid rgba(148, 163, 184, 0.15);
}

.tab-btn {
  flex: 1;
  padding: 0.8vw 1.5vw;
  background: transparent;
  border: none;
  color: #94a3b8;
  font-size: 0.95vw;
  font-weight: 700;
  border-radius: 0.6vw;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.6vw;
  font-family: 'Nunito', system-ui, sans-serif;
}

.tab-btn.active {
  background: rgba(59, 130, 246, 0.2);
  color: #93c5fd;
}

.tab-badge {
  background: rgba(245, 158, 11, 0.25);
  color: #fef08a;
  border: 1px solid rgba(245, 158, 11, 0.4);
  border-radius: 9999px;
  padding: 0.1vw 0.6vw;
  font-size: 0.8vw;
  font-weight: 800;
}

.tab-badge.subcategory-badge {
  background: rgba(59, 130, 246, 0.25);
  color: #93c5fd;
  border-color: rgba(59, 130, 246, 0.4);
}

.search-bar-wrapper {
  margin-bottom: 1.5vw;
}

.search-input {
  width: 100%;
  padding: 0.9vw 1.2vw;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 0.7vw;
  color: #ffffff;
  font-size: 0.95vw;
  font-family: 'Nunito', system-ui, sans-serif;
  transition: border-color 0.2s;
  box-sizing: border-box;
}
.search-input:focus {
  outline: none;
  border-color: rgba(96, 165, 250, 0.6);
}
.search-input::placeholder { color: rgba(226, 232, 240, 0.4); }

.table-container {
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.15);
  border-radius: 1vw;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.validation-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.9vw;
}

.validation-table th, .validation-table td {
  padding: 1.2vw;
  border-bottom: 1px solid rgba(148, 163, 184, 0.1);
}

.validation-table th {
  background: rgba(30, 41, 59, 0.8);
  color: #93c5fd;
  font-weight: 700;
  text-transform: uppercase;
  font-size: 0.75vw;
  letter-spacing: 0.05em;
}

.validation-table tr:last-child td { border-bottom: none; }
.validation-table tr:hover { background: rgba(30, 41, 59, 0.4); }

.item-name { font-weight: 700; color: #f8fafc; }
.item-student { color: #cbd5e1; }
.item-price { font-family: monospace; font-size: 1vw; }

.cpv-info { display: flex; flex-direction: column; gap: 0.3vw; }
.category { color: #e2e8f0; }
.cpv-code { font-size: 0.8vw; color: #fbbf24; font-family: monospace; }

.link-btn {
  color: #60a5fa;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.2s;
}
.link-btn:hover { color: #93c5fd; text-decoration: underline; }

.actions-cell {
  display: flex;
  gap: 0.5vw;
}

.action-btn {
  padding: 0.6vw 1vw;
  border: 1px solid transparent;
  border-radius: 0.4vw;
  font-size: 0.8vw;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  font-family: 'Nunito', system-ui, sans-serif;
}

.action-btn.accept { background: rgba(34, 197, 94, 0.15); color: #86efac; border-color: rgba(34, 197, 94, 0.3); }
.action-btn.accept:hover:not(:disabled) { background: rgba(34, 197, 94, 0.3); }
.action-btn.accept:disabled { opacity: 0.4; cursor: not-allowed; }

.action-btn.reject { background: rgba(239, 68, 68, 0.15); color: #fca5a5; border-color: rgba(239, 68, 68, 0.3); }
.action-btn.reject:hover { background: rgba(239, 68, 68, 0.3); }

.category-select {
  width: 100%;
  padding: 0.6vw 0.8vw;
  background: rgba(30, 41, 59, 0.7);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 0.5vw;
  color: #ffffff;
  font-size: 0.85vw;
  font-family: 'Nunito', system-ui, sans-serif;
}
.category-select:focus { outline: none; border-color: #3b82f6; }
.category-select option { background: #0f172a; }

.validation-empty {
  text-align: center;
  padding: 4vw;
  background: rgba(15, 23, 42, 0.4);
  border: 1px dashed rgba(148, 163, 184, 0.2);
  border-radius: 1vw;
}
.empty-icon { font-size: 3vw; margin-bottom: 1vw; }
.empty-text { font-size: 1.2vw; font-weight: 700; color: #e2e8f0; margin-bottom: 0.5vw; }
.empty-subtext { color: #94a3b8; font-size: 0.95vw; }

.confirm-modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background-color: rgba(5, 8, 22, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  backdrop-filter: blur(8px);
}

.confirm-modal-content {
  background: #0f172a;
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 1.5vw;
  padding: 3vw;
  width: 90%;
  max-width: 32vw;
  text-align: center;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
  animation: modalPop 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes modalPop {
  0% { transform: scale(0.9); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}

.confirm-modal-icon { font-size: 3.5vw; margin-bottom: 1vw; }

.confirm-modal-title {
  color: #ef4444;
  font-size: 2vw;
  font-weight: 800;
  margin: 0 0 1vw 0;
  font-family: 'Nunito', system-ui, sans-serif;
}

.confirm-modal-text {
  color: #e2e8f0;
  font-size: 1.1vw;
  line-height: 1.6;
  margin-bottom: 2.5vw;
  font-family: 'Nunito', system-ui, sans-serif;
}

.confirm-modal-actions {
  display: flex;
  gap: 1.5vw;
  justify-content: center;
}

.confirm-btn {
  padding: 0.9vw 2.5vw;
  border-radius: 0.8vw;
  font-size: 1.1vw;
  font-weight: 800;
  cursor: pointer;
  border: none;
  transition: all 0.2s ease;
  font-family: 'Nunito', system-ui, sans-serif;
}

.confirm-btn-cancel {
  background: rgba(148, 163, 184, 0.15);
  color: #e2e8f0;
}
.confirm-btn-cancel:hover { background: rgba(148, 163, 184, 0.3); color: #ffffff; }

.confirm-btn-danger {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: #ffffff;
  box-shadow: 0 10px 20px rgba(239, 68, 68, 0.3);
}
.confirm-btn-danger:hover {
  transform: translateY(-0.3vh);
  filter: brightness(1.1);
  box-shadow: 0 14px 28px rgba(239, 68, 68, 0.5);
}
</style>
