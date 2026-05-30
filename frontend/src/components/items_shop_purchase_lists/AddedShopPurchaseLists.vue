<template>
  <div v-if="!activeList" class="lists-section">
    <div class="lists-header">
      <div class="lists-title-section">
        <h2 class="lists-title">Moje listy zakupów</h2>
        <p class="lists-subtitle">Listy zakupowe, które utworzyłeś</p>
      </div>
      <button class="lists-add-button">+ Nowa lista</button>
    </div>

    <div v-if="userLists.length === 0" class="lists-empty">
      <p class="lists-empty-icon">🛒</p>
      <p class="lists-empty-text">Nie utworzyłeś jeszcze żadnej listy</p>
      <p class="lists-empty-subtext">Stwórz nową listę zakupów klikając przycisk powyżej</p>
    </div>

    <div v-else class="lists-grid">
      <div
        v-for="list in userLists"
        :key="list.id"
        class="list-card"
      >
        <div class="list-card__header">
          <h3 class="list-card__title">{{ list.name }}</h3>
          <span class="list-card__shop">{{ list.shopName }}</span>
        </div>
        <div class="list-card__content">
          <p class="list-card__detail">
            <span class="list-card__label">Przedmioty:</span>
            <span class="list-card__value">{{ list.itemCount }} / {{ list.itemTotal }}</span>
          </p>
          <p class="list-card__detail">
            <span class="list-card__label">Kwota:</span>
            <span class="list-card__value">{{ list.totalPrice }} PLN</span>
          </p>
          <p class="list-card__detail">
            <span class="list-card__label">Postęp:</span>
            <span class="list-card__value">{{ Math.round((list.itemCount / list.itemTotal) * 100) }}%</span>
          </p>
          <p class="list-card__detail">
            <span class="list-card__label">Uczestnicy:</span>
            <span class="list-card__value">{{ list.participants }} osób</span>
          </p>
          <div class="list-card__progress">
            <div class="list-card__progress-bar">
              <div
                class="list-card__progress-fill"
                :style="{ width: Math.round((list.itemCount / list.itemTotal) * 100) + '%' }"
              ></div>
            </div>
          </div>
        </div>
        <div class="list-card__actions">
          <button class="list-card__button view" @click="activeList = list">Otwórz listę</button>
          <button class="list-card__button delete">Usuń</button>
        </div>
      </div>
    </div>
  </div>
  <ShopPurchaseListDetails
    v-else
    :list="activeList"
    @back="activeList = null"
  />
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuth } from '@/composables/useAuth'
import ShopPurchaseListDetails from './ShopPurchaseListDetails.vue'

const activeList = ref(null)
const { user } = useAuth()

const allLists = ref([
  {
    id: 1,
    name: 'Lista 1',
    shopName: 'Biedronka',
    itemCount: 5,
    itemTotal: 8,
    totalPrice: 245.50,
    participants: 3,
    createdDate: new Date(),
    userId: 'user1'
  },
  {
    id: 2,
    name: 'Zakupy spożywcze',
    shopName: 'Carrefour',
    itemCount: 3,
    itemTotal: 5,
    totalPrice: 156.20,
    participants: 2,
    createdDate: new Date(),
    userId: 'user1'
  },
  {
    id: 3,
    name: 'Artykuły domowe',
    shopName: 'Leroy Merlin',
    itemCount: 2,
    itemTotal: 7,
    totalPrice: 890.00,
    participants: 4,
    createdDate: new Date(),
    userId: 'user1'
  }
])

const userLists = computed(() => {
  return allLists.value.filter(list => list.userId === user.value?.id)
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;500;600;700;800&display=swap');

.lists-section {
  width: 100%;
  padding: 3vh 0;
  font-family: 'Nunito', system-ui, sans-serif;
}

.lists-header {
  margin-bottom: 3vh;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 2vw;
}

.lists-title-section {
  display: flex;
  flex-direction: column;
  gap: 0.5vw;
}

.lists-title {
  font-size: 2vw;
  font-weight: 800;
  color: #bfdbfe;
  margin: 0;
}

.lists-subtitle {
  font-size: 1vw;
  color: rgba(226, 232, 240, 0.6);
  margin: 0;
}

.lists-add-button {
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

.lists-add-button:hover {
  transform: translateY(-0.2vh);
  box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4);
}

.lists-empty {
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

.lists-empty-icon {
  font-size: 4vw;
  margin: 0 0 1.5vh 0;
}

.lists-empty-text {
  font-size: 1.2vw;
  font-weight: 600;
  color: rgba(226, 232, 240, 0.8);
  margin: 0 0 0.5vh 0;
}

.lists-empty-subtext {
  font-size: 0.95vw;
  color: rgba(226, 232, 240, 0.5);
  margin: 0;
}

.lists-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(26vw, 1fr));
  gap: 2vw;
}

.list-card {
  display: flex;
  flex-direction: column;
  padding: 2vw;
  background: rgba(15, 23, 42, 0.6);
  border: 0.08vw solid rgba(148, 163, 184, 0.15);
  border-radius: 1vw;
  transition: all 0.3s ease;
}

.list-card:hover {
  background: rgba(15, 23, 42, 0.8);
  border-color: rgba(59, 130, 246, 0.3);
  transform: translateY(-0.4vh);
}

.list-card__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5vw;
  gap: 1vw;
}

.list-card__title {
  font-size: 1.2vw;
  font-weight: 700;
  color: #ffffff;
  margin: 0;
  flex: 1;
}

.list-card__shop {
  padding: 0.4vw 0.8vw;
  border-radius: 0.4vw;
  font-size: 0.85vw;
  font-weight: 600;
  background: rgba(59, 130, 246, 0.2);
  color: #93c5fd;
  white-space: nowrap;
}

.list-card__content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.8vw;
  margin-bottom: 1.5vw;
}

.list-card__detail {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.95vw;
  margin: 0;
}

.list-card__label {
  color: rgba(226, 232, 240, 0.6);
  font-weight: 600;
}

.list-card__value {
  color: #ffffff;
  font-weight: 500;
}

.list-card__progress {
  margin-top: 0.8vw;
}

.list-card__progress-bar {
  width: 100%;
  height: 0.6vw;
  background: rgba(148, 163, 184, 0.2);
  border-radius: 0.3vw;
  overflow: hidden;
}

.list-card__progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #60a5fa);
  transition: width 0.3s ease;
}

.list-card__actions {
  display: flex;
  gap: 0.8vw;
}

.list-card__button {
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

.list-card__button.view {
  background: rgba(59, 130, 246, 0.2);
  color: #93c5fd;
}

.list-card__button.view:hover {
  background: rgba(59, 130, 246, 0.35);
}

.list-card__button.delete {
  background: rgba(239, 68, 68, 0.2);
  color: #fca5a5;
}

.list-card__button.delete:hover {
  background: rgba(239, 68, 68, 0.35);
}
</style>
