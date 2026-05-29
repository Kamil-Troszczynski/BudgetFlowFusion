<template>
  <div class="items-section">
    <div class="items-header">
      <h2 class="items-title">Moje przedmioty</h2>
      <p class="items-subtitle">Przedmioty, które dodałeś do list zakupowych</p>
    </div>

    <div v-if="userItems.length === 0" class="items-empty">
      <p class="items-empty-icon">📦</p>
      <p class="items-empty-text">Nie dodałeś jeszcze żadnych przedmiotów</p>
      <p class="items-empty-subtext">Kliknij na jedną z list zakupowych i dodaj przedmiot</p>
    </div>

    <div v-else class="items-grid">
      <div 
        v-for="item in userItems" 
        :key="item.id"
        class="item-card"
      >
        <div class="item-card__header">
          <h3 class="item-card__title">{{ item.name }}</h3>
          <span class="item-card__status" :class="{ completed: item.completed }">
            {{ item.completed ? '✓ Zakupiono' : '⏳ Oczekuje' }}
          </span>
        </div>
        <div class="item-card__content">
          <p class="item-card__detail">
            <span class="item-card__label">Lista:</span>
            <span class="item-card__value">{{ item.listName }}</span>
          </p>
          <p class="item-card__detail">
            <span class="item-card__label">Ilość:</span>
            <span class="item-card__value">{{ item.quantity }}</span>
          </p>
          <p class="item-card__detail">
            <span class="item-card__label">Cena:</span>
            <span class="item-card__value">{{ item.price }} PLN</span>
          </p>
          <p class="item-card__detail">
            <span class="item-card__label">Data dodania:</span>
            <span class="item-card__value">{{ formatDate(item.addedDate) }}</span>
          </p>
        </div>
        <div class="item-card__actions">
          <button class="item-card__button edit">Edytuj</button>
          <button class="item-card__button delete">Usuń</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuth } from '@/composables/useAuth'

const { user } = useAuth()

const allItems = ref([
  { id: 1, name: 'Mleko', quantity: '2 l', price: '6.99', listName: 'Biedronka', addedDate: new Date(), completed: false, userId: 'user1' },
  { id: 2, name: 'Chleb', quantity: '1 szt', price: '3.99', listName: 'Carrefour', addedDate: new Date(), completed: true, userId: 'user1' },
  { id: 3, name: 'Masło', quantity: '250g', price: '8.50', listName: 'Biedronka', addedDate: new Date(), completed: false, userId: 'user1' }
])

const userItems = computed(() => {
  return allItems.value.filter(item => item.userId === user.value?.id)
})

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('pl-PL', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
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
</style>
