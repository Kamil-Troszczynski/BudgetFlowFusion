<template>
  <div class="items-section">
    <div class="items-header" style="display: flex; justify-content: space-between; align-items: center;">
      <div>
        <h2 class="items-title">Katalog Przedmiotów</h2>
        <p class="items-subtitle">Przeglądaj przedmioty i dodawaj nowe do akceptacji</p>
      </div>
      <div style="display: flex; gap: 0.8vw; align-items: center;">
        <button class="items-request-subcategory-button" @click="showRequestSubcategoryModal = true">+ Zgłoś podkategorię</button>
        <button class="items-add-button" @click="showAddModal = true">+ Dodaj nowy przedmiot</button>
      </div>
    </div>

    <div class="search-bar-wrapper">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Szukaj przedmiotu po nazwie..."
        class="search-input"
      />
    </div>

    <div class="items-toolbar">
      <span class="items-toolbar__label">Grupowanie</span>
      <button
        v-for="option in groupingOptions"
        :key="option.value"
        type="button"
        class="items-toolbar__btn"
        :class="{ active: activeGroupMode === option.value }"
        @click="setGroupMode(option.value)"
      >
        {{ option.label }}
      </button>
    </div>

    <div v-if="activeGroupMode === 'none'" class="items-grid">
      <div
        v-for="item in filteredCatalogItems"
        :key="item.id"
        class="item-card"
      >
        <div class="item-card__header">
          <h3 class="item-card__title">{{ item.name }}</h3>
          <span class="item-card__status completed">✓ W katalogu</span>
        </div>
        <div class="item-card__content">
          <p class="item-card__detail">
            <span class="item-card__label">Cena:</span>
            <span class="item-card__value">{{ item.price }} {{ item.currency }}</span>
          </p>
          <p class="item-card__detail">
            <span class="item-card__label">Link:</span>
            <span class="item-card__value">
              <a :href="item.link" target="_blank" style="color: #60a5fa;">Zobacz w sklepie ↗</a>
            </span>
          </p>
        </div>
      </div>
    </div>

    <div v-else class="grouped-items">
      <div
        v-for="group in groupedItems"
        :key="group.group_key"
        class="item-group"
      >
        <div class="item-group__header">
          <div>
            <h3 class="item-group__title">{{ group.group_label }}</h3>
            <p class="item-group__meta">
              {{ group.count }} pozycji · {{ formatMoney(group.total_price) }} PLN
            </p>
          </div>
        </div>

        <div class="items-grid">
          <div
            v-for="item in group.items"
            :key="item.item_id"
            class="item-card"
          >
            <div class="item-card__header">
              <h3 class="item-card__title">{{ item.name }}</h3>
              <span class="item-card__status completed">{{ item.status }}</span>
            </div>
            <div class="item-card__content">
              <p class="item-card__detail">
                <span class="item-card__label">Cena:</span>
                <span class="item-card__value">{{ formatMoney(item.price) }} {{ item.currency }}</span>
              </p>
              <p class="item-card__detail">
                <span class="item-card__label">Sklep:</span>
                <span class="item-card__value">{{ item.shop_name || 'Brak' }}</span>
              </p>
              <p class="item-card__detail">
                <span class="item-card__label">CPV:</span>
                <span class="item-card__value">{{ item.cpv || 'Brak' }}</span>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <AddItemModal
      :isOpen="showAddModal"
      :isLoading="isSubmitting"
      @close="showAddModal = false"
      @submit-item="handleNewItemSubmit"
    />

    <RequestSubcategoryModal
      :isOpen="showRequestSubcategoryModal"
      @close="showRequestSubcategoryModal = false"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { useToast } from '@/composables/useToast'
import AddItemModal from './AddItemModal.vue'
import RequestSubcategoryModal from './RequestSubcategoryModal.vue'

const showAddModal = ref(false)
const showRequestSubcategoryModal = ref(false)
const toast = useToast()
const catalogItems = ref([])
const groupedItems = ref([])
const { user } = useAuth()
const isSubmitting = ref(false)
const activeGroupMode = ref('none')
const searchQuery = ref('')

const filteredCatalogItems = computed(() => {
  const q = searchQuery.value.toLowerCase().trim()
  if (!q) return catalogItems.value
  return catalogItems.value.filter(i => i.name.toLowerCase().includes(q))
})

const groupingOptions = [
  { value: 'none', label: 'Brak' },
  { value: 'shop', label: 'Sklep' },
  { value: 'cpv', label: 'CPV' },
  { value: 'category', label: 'Kategoria' },
  { value: 'status', label: 'Status' }
]

const fetchCatalog = async () => {
  try {
    const response = await fetch(`http://localhost:8080/api/items?student_id=${user.value.id}`)
    if (!response.ok) throw new Error('Błąd sieci')
    const data = await response.json()

    catalogItems.value = data.map(item => ({
      ...item,
      id: item.item_id
    }))
  } catch (error) {
    console.error("Błąd pobierania katalogu:", error)
  }
}

const fetchGroupedCatalog = async () => {
  if (activeGroupMode.value === 'none') return

  try {
    const response = await fetch(
      `http://localhost:8080/api/items/grouped?student_id=${user.value.id}&group_by=${activeGroupMode.value}`
    )
    if (!response.ok) throw new Error('Błąd sieci')

    groupedItems.value = await response.json()
  } catch (error) {
    console.error("Błąd pobierania pogrupowanego katalogu:", error)
  }
}

const setGroupMode = async (mode) => {
  activeGroupMode.value = mode
  if (mode !== 'none') {
    await fetchGroupedCatalog()
  }
}

const formatMoney = (value) => {
  return Number(value || 0).toLocaleString('pl-PL', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

onMounted(() => {
  fetchCatalog()
})

const handleNewItemSubmit = async (itemData) => {
  isSubmitting.value = true

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

    if (!response.ok) throw new Error('Nie udało się wysłać przedmiotu do akceptacji')

    showAddModal.value = false;

    if (user.value.role === 'treasurer') {
      toast.success('Przedmiot został automatycznie dodany do katalogu!')
      fetchCatalog()
      fetchGroupedCatalog()
    } else {
      toast.success('Przedmiot został wysłany do akceptacji!')
    }

  } catch (error) {
    console.error("Błąd podczas dodawania przedmiotu:", error)
    toast.error("Wystąpił błąd podczas zapisywania w bazie.")
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;500;600;700;800&display=swap');

.items-section {
  width: 100%;
  padding: 3vh 0;
  font-family: 'Nunito', system-ui, sans-serif;
}

.items-header {
  margin-bottom: 3vh;
}

.items-title {
  font-size: 2vw;
  font-weight: 800;
  color: #bfdbfe;
  margin: 0 0 0.8vh 0;
}

.items-subtitle {
  font-size: 1vw;
  color: rgba(226, 232, 240, 0.6);
  margin: 0;
}

.search-bar-wrapper {
  margin-bottom: 1.5vw;
}

.search-input {
  width: 100%;
  padding: 0.9vw 1.2vw;
  background: rgba(15, 23, 42, 0.6);
  border: 0.08vw solid rgba(148, 163, 184, 0.2);
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

.items-toolbar {
  display: flex;
  align-items: center;
  gap: 0.7vw;
  margin-bottom: 2vw;
  padding: 0.8vw;
  border: 0.08vw solid rgba(148, 163, 184, 0.15);
  border-radius: 0.8vw;
  background: rgba(15, 23, 42, 0.5);
}

.items-toolbar__label {
  color: rgba(226, 232, 240, 0.65);
  font-size: 0.9vw;
  font-weight: 800;
}

.items-toolbar__btn {
  padding: 0.55vw 0.9vw;
  border: 0.08vw solid rgba(148, 163, 184, 0.18);
  border-radius: 0.55vw;
  background: rgba(30, 41, 59, 0.55);
  color: #cbd5e1;
  font-family: 'Nunito', system-ui, sans-serif;
  font-size: 0.88vw;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.2s ease;
}

.items-toolbar__btn:hover,
.items-toolbar__btn.active {
  border-color: rgba(96, 165, 250, 0.5);
  background: rgba(59, 130, 246, 0.2);
  color: #93c5fd;
}

.items-empty {
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

.items-empty-icon {
  font-size: 4vw;
  margin: 0 0 1.5vh 0;
}

.items-empty-text {
  font-size: 1.2vw;
  font-weight: 600;
  color: rgba(226, 232, 240, 0.8);
  margin: 0 0 0.5vh 0;
}

.items-empty-subtext {
  font-size: 0.95vw;
  color: rgba(226, 232, 240, 0.5);
  margin: 0;
}

.items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(24vw, 1fr));
  gap: 2vw;
}

.grouped-items {
  display: grid;
  gap: 2vw;
}

.item-group {
  display: grid;
  gap: 1.2vw;
  padding: 1.5vw;
  border: 0.08vw solid rgba(148, 163, 184, 0.15);
  border-radius: 1vw;
  background: rgba(15, 23, 42, 0.38);
}

.item-group__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 1vw;
  border-bottom: 0.08vw solid rgba(148, 163, 184, 0.12);
}

.item-group__title {
  margin: 0;
  color: #bfdbfe;
  font-size: 1.25vw;
  font-weight: 800;
}

.item-group__meta {
  margin: 0.4vh 0 0 0;
  color: rgba(226, 232, 240, 0.58);
  font-size: 0.9vw;
  font-weight: 700;
}

.item-card {
  display: flex;
  flex-direction: column;
  padding: 2vw;
  background: rgba(15, 23, 42, 0.6);
  border: 0.08vw solid rgba(148, 163, 184, 0.15);
  border-radius: 1vw;
  transition: all 0.3s ease;
}

.item-card:hover {
  background: rgba(15, 23, 42, 0.8);
  border-color: rgba(59, 130, 246, 0.3);
  transform: translateY(-0.4vh);
}

.item-card__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5vw;
  gap: 1vw;
}

.item-card__title {
  font-size: 1.2vw;
  font-weight: 700;
  color: #ffffff;
  margin: 0;
  flex: 1;
}

.item-card__status {
  padding: 0.4vw 0.8vw;
  border-radius: 0.4vw;
  font-size: 0.85vw;
  font-weight: 600;
  background: rgba(239, 68, 68, 0.15);
  color: #fca5a5;
  white-space: nowrap;
}

.item-card__status.completed {
  background: rgba(34, 197, 94, 0.15);
  color: #86efac;
}

.item-card__content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.8vw;
  margin-bottom: 1.5vw;
}

.item-card__detail {
  display: flex;
  align-items: center;
  gap: 0.8vw;
  font-size: 0.95vw;
  margin: 0;
}

.item-card__label {
  color: rgba(226, 232, 240, 0.6);
  font-weight: 600;
  min-width: 5vw;
}

.item-card__value {
  color: #ffffff;
  font-weight: 500;
}

.item-card__actions {
  display: flex;
  gap: 0.8vw;
}

.item-card__button {
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

.item-card__button.edit {
  background: rgba(59, 130, 246, 0.2);
  color: #93c5fd;
}

.item-card__button.edit:hover {
  background: rgba(59, 130, 246, 0.35);
}

.item-card__button.delete {
  background: rgba(239, 68, 68, 0.2);
  color: #fca5a5;
}

.item-card__button.delete:hover {
  background: rgba(239, 68, 68, 0.35);
}

.items-request-subcategory-button {
  padding: 0.8vw 1.5vw;
  background: rgba(59, 130, 246, 0.15);
  color: #93c5fd;
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 0.8vw;
  font-size: 1vw;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: 'Nunito', system-ui, sans-serif;
}

.items-request-subcategory-button:hover {
  background: rgba(59, 130, 246, 0.28);
  border-color: rgba(59, 130, 246, 0.5);
}

.items-add-button {
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

.items-add-button:hover {
  transform: translateY(-0.2vh);
  box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4);
}

</style>
