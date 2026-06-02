<template>
  <div v-if="!activeList" class="lists-section">
    <div class="lists-header">
      <div class="lists-title-section">
        <h2 class="lists-title">Moje listy zakupów</h2>
        <p class="lists-subtitle">Listy zakupowe, które utworzyłeś</p>
      </div>
      <button class="lists-add-button" @click="showAddListModal = true">+ Nowa lista</button>
    </div>

    <div v-if="userLists.length === 0" class="lists-empty">
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
            <span class="list-card__label">Uczestnicy:</span>
            <span class="list-card__value">{{ list.participants }} osób</span>
          </p>
        </div>
        <div class="list-card__actions">
          <button class="list-card__button view" @click="activeList = list">Otwórz listę</button>
          <button class="list-card__button delete" @click.stop="promptDeleteList(list.id)">Usuń</button>
        </div>
      </div>
    </div>
  </div>

  <ShopPurchaseListDetails
    v-else-if="activeList"
    :list="activeList"
    @back="activeList = null"
  />

  <div v-if="showDeleteModal" class="confirm-modal-overlay" @click="showDeleteModal = false">
    <div class="confirm-modal-content" @click.stop>
      <h2 class="confirm-modal-title">Usuwanie listy</h2>
      <p class="confirm-modal-text">
        Czy na pewno chcesz usunąć tę listę?<br/>
        <strong class="text-danger">Wszystkie przedmioty w jej koszyku również zostaną usunięte.</strong>
      </p>
      <div class="confirm-modal-actions">
        <button class="confirm-btn confirm-btn-cancel" @click="showDeleteModal = false">Anuluj</button>
        <button class="confirm-btn confirm-btn-danger" @click="executeDeleteList">Tak, usuń</button>
      </div>
    </div>
  </div>

  <AddListModal
    :isOpen="showAddListModal"
    @close="showAddListModal = false"
    @submit-list="handleNewList"
  />
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { useToast } from '@/composables/useToast'
import ShopPurchaseListDetails from './ShopPurchaseListDetails.vue'
import AddListModal from './AddListModal.vue'

const { user } = useAuth()
const activeList = ref(null)
const showAddListModal = ref(false)
const toast = useToast()
const allLists = ref([])
const shops = ref([])
const showDeleteModal = ref(false)
const listToDeleteId = ref(null)

const userLists = computed(() => {
  console.log("Moje listy z bazy:", allLists.value);
  console.log("Mój zalogowany User ID:", user.value?.id);
  return allLists.value
})

const fetchShops = async () => {
  try {
    const response = await fetch('http://localhost:8080/api/shops')
    const data = await response.json()
    shops.value = data
  } catch (error) {
    console.error("Błąd pobierania sklepów:", error)
  }
}

const fetchLists = async () => {
  try {
    await fetchShops()

    let fundings = []
    if (user.value?.association_id) {
      const fundingsResponse = await fetch(`http://localhost:8080/api/fundings?association_id=${user.value.association_id}`)
      if (fundingsResponse.ok) {
        fundings = await fundingsResponse.json()
      }
    }

    const timestamp = new Date().getTime()
    const response = await fetch(`http://localhost:8080/api/lists?student_id=${user.value.id}&t=${timestamp}`, {
      cache: 'no-store'
    })

    if (!response.ok) throw new Error('Błąd sieci przy pobieraniu list')
    const data = await response.json()

    const processedLists = await Promise.all(data.map(async (list) => {
      let items = []
      try {
        const itemsResponse = await fetch(`http://localhost:8080/api/lists/${list.shop_purchase_list_id}/items?t=${timestamp}`, { cache: 'no-store' })
        if (itemsResponse.ok) items = await itemsResponse.json()
      } catch (e) {
        console.warn("Brak przedmiotów na liście", e)
      }

      const foundShop = shops.value.find(s => s.shop_id === list.shop_id)
      const foundFunding = Array.isArray(fundings) ? fundings.find(f => f.funding_id === list.funding_id) : null
      const maxBudget = foundFunding ? (foundFunding.funding_price - foundFunding.spent_money) : 0

      return {
        ...list,
        id: list.shop_purchase_list_id,
        name: list.name || `Zamówienie #${list.shop_purchase_list_id}`,
        shopName: foundShop ? foundShop.shop_name : 'Nieznany sklep',
        itemCount: items.length,
        totalPrice: items.reduce((sum, item) => sum + item.total_price, 0),
        participants: 1,
        maxBudget: maxBudget
      }
    }))

    allLists.value = processedLists
  } catch (error) {
    console.error("Krytyczny błąd pobierania list:", error)
  }
}

onMounted(() => {
  fetchLists()
})

const handleNewList = async (listData) => {
  try {
    const payload = {
      priority: listData.priority || 1,
      cost: 0.0,
      created_at: new Date().toISOString(),
      funding_id: listData.fundingId || listData.funding_id,
      shop_id: listData.shopId || listData.shop_id,
      student_id: user.value.id
    }

    const response = await fetch('http://localhost:8080/api/lists', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })

    if (!response.ok) {
      const err = await response.json()
      console.error("Błąd backendu:", err)
      throw new Error('Nie udało się zapisać listy w bazie')
    }

    await fetchLists()

    showAddListModal.value = false
    toast.success('Lista została poprawnie utworzona!')

  } catch (error) {
    console.error("Błąd zapisu listy:", error)
    toast.error("Wystąpił błąd podczas zapisu nowej listy.")
  }
}

const promptDeleteList = (listId) => {
  listToDeleteId.value = listId
  showDeleteModal.value = true
}

const executeDeleteList = async () => {
  if (!listToDeleteId.value) return

  try {
    const response = await fetch(`http://localhost:8080/api/lists/${listToDeleteId.value}`, {
      method: 'DELETE'
    })

    if (!response.ok) throw new Error('Nie udało się usunąć listy z backendu')

    toast.info('Lista została trwale usunięta z systemu.')

    await fetchLists()

  } catch (error) {
    console.error("Błąd podczas usuwania:", error)
    toast.error('Wystąpił problem przy usuwaniu listy.')
  } finally {
    showDeleteModal.value = false
    listToDeleteId.value = null
  }
}
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

.confirm-modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background-color: rgba(5, 8, 22, 0.85); display: flex; align-items: center; justify-content: center; z-index: 9999; backdrop-filter: blur(8px); }
.confirm-modal-content { background: #0f172a; border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 1.5vw; padding: 3vw; width: 90%; max-width: 32vw; text-align: center; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7); animation: modalPop 0.3s cubic-bezier(0.34, 1.56, 0.64, 1); }
@keyframes modalPop { 0% { transform: scale(0.9); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }
.confirm-modal-icon { font-size: 3.5vw; margin-bottom: 1vw; filter: drop-shadow(0 0 10px rgba(245, 158, 11, 0.5)); }
.confirm-modal-title { color: #ef4444; font-size: 2vw; font-weight: 800; margin: 0 0 1vw 0; }
.confirm-modal-text { color: #e2e8f0; font-size: 1.1vw; line-height: 1.6; margin-bottom: 2.5vw; }
.text-danger { color: #fca5a5; font-weight: 700; }
.confirm-modal-actions { display: flex; gap: 1.5vw; justify-content: center; }
.confirm-btn { padding: 0.9vw 2.5vw; border-radius: 0.8vw; font-size: 1.1vw; font-weight: 800; cursor: pointer; border: none; transition: all 0.2s ease; }
.confirm-btn-cancel { background: rgba(148, 163, 184, 0.15); color: #e2e8f0; }
.confirm-btn-cancel:hover { background: rgba(148, 163, 184, 0.3); color: #ffffff; }
.confirm-btn-danger { background: linear-gradient(135deg, #ef4444, #dc2626); color: #ffffff; box-shadow: 0 10px 20px rgba(239, 68, 68, 0.3); }
.confirm-btn-danger:hover { transform: translateY(-0.3vh); filter: brightness(1.1); box-shadow: 0 14px 28px rgba(239, 68, 68, 0.5); }
</style>
