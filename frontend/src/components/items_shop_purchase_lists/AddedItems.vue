<template>
  <div class="items-section">
    <div class="items-header" style="display: flex; justify-content: space-between; align-items: center;">
      <div>
        <h2 class="items-title">Katalog Przedmiotów</h2>
        <p class="items-subtitle">Przeglądaj przedmioty i dodawaj nowe do akceptacji</p>
      </div>
      <button class="items-add-button" @click="showAddModal = true">+ Dodaj nowy przedmiot</button>
    </div>

    <div class="items-grid">
      <div
        v-for="item in catalogItems"
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

    <AddItemModal
      :isOpen="showAddModal"
      @close="showAddModal = false"
      @submit-item="handleNewItemSubmit"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AddItemModal from './AddItemModal.vue'

const showAddModal = ref(false)
const catalogItems = ref([])

const fetchCatalog = async () => {
  try {
    const response = await fetch('http://localhost:8080/api/items')
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

onMounted(() => {
  fetchCatalog()
})

const handleNewItemSubmit = async (itemData) => {
  try {
    const response = await fetch('http://localhost:8080/api/items', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: itemData.name,
        link: itemData.link,
        price: itemData.price,
        currency: itemData.currency,
        product_subcategory_id: itemData.subcategoryId
      })
    })

    if (!response.ok) throw new Error('Nie udało się wysłać przedmiotu do akceptacji')

    alert('Sukces! Przedmiot został wysłany do akceptacji przez Skarbnika.')
    showAddModal.value = false;

  } catch (error) {
    console.error("Błąd podczas dodawania przedmiotu:", error)
    alert("Wystąpił błąd podczas zapisywania w bazie.")
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