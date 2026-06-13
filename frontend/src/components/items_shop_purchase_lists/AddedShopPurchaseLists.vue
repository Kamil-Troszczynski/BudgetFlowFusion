<template>
  <div v-if="!activeList" class="lists-section">
    <div class="lists-header">
      <div class="lists-title-section">
        <h2 class="lists-title">{{ isTreasurer ? 'Listy zamówień' : 'Otwarte listy zamówień' }}</h2>
        <p class="lists-subtitle">
          {{ isTreasurer ? 'Twoje listy są na górze, a listy innych skarbników poniżej' : 'Wybierz otwartą listę dla sklepu i dodaj swoje pozycje' }}
        </p>
      </div>
      <button v-if="isTreasurer" class="lists-add-button" @click="showAddListModal = true">+ Nowa lista</button>
    </div>

    <div v-if="!isTreasurer" class="lists-filter">
      <label class="lists-filter__label">Sklep</label>
      <select v-model="selectedShopId" class="lists-filter__select" @change="fetchLists">
        <option value="">Wszystkie sklepy</option>
        <option v-for="shop in shops" :key="shop.shop_id" :value="shop.shop_id">
          {{ shop.shop_name }}
        </option>
      </select>
    </div>

    <section v-for="section in listSections" :key="section.key" class="lists-group">
      <div v-if="section.title" class="lists-group__header">
        <div>
          <h3 class="lists-group__title">{{ section.title }}</h3>
          <p class="lists-group__subtitle">{{ section.subtitle }}</p>
        </div>
        <span class="lists-group__count">{{ section.lists.length }}</span>
      </div>

      <div v-if="section.lists.length === 0" class="lists-empty" :class="{ 'lists-empty--compact': section.title }">
        <p class="lists-empty-text">{{ section.emptyText }}</p>
        <p class="lists-empty-subtext">{{ section.emptySubtext }}</p>
      </div>

      <div v-else class="lists-grid">
        <div
          v-for="list in section.lists"
          :key="list.id"
          class="list-card"
          :class="{ 'list-card--closed': !list.isOpen }"
        >
          <div class="list-card__header">
            <h3 class="list-card__title">{{ list.name }}</h3>
            <span class="list-card__shop">{{ list.shopName }}</span>
          </div>
          <div class="list-card__content">
            <p class="list-card__detail">
              <span class="list-card__label">Przedmioty:</span>
              <span class="list-card__value">{{ list.itemCount }} pozycji / {{ list.itemTotal }} szt.</span>
            </p>
            <p class="list-card__detail">
              <span class="list-card__label">Kwota:</span>
              <span class="list-card__value">{{ formatMoney(list.totalPrice) }} PLN</span>
            </p>
            <p class="list-card__detail">
              <span class="list-card__label">Status:</span>
              <span class="list-card__value">{{ list.isOpen ? 'Otwarta' : 'Zamknięta' }}</span>
            </p>
            <p v-if="isTreasurer" class="list-card__detail">
              <span class="list-card__label">Utworzył:</span>
              <span class="list-card__value">{{ list.creatorName }}</span>
            </p>
          </div>
          <div class="list-card__actions">
            <button class="list-card__button view" @click="openList(list)">Otwórz listę</button>
            <button v-if="canCloseList(list)" class="list-card__button close" @click.stop="promptCloseList(list)">Zamknij</button>
            <button v-if="canDeleteList(list)" class="list-card__button delete" @click.stop="promptDeleteList(list)">Usuń</button>
          </div>
        </div>
      </div>
    </section>
  </div>

  <ShopPurchaseListDetails
    v-else-if="activeList"
    :list="activeList"
    :can-manage-items="isOwnList(activeList)"
    :can-close-list="canCloseList(activeList)"
    @back="activeList = null"
    @close-list="promptCloseList(activeList)"
  />

  <div v-if="showDeleteModal" class="confirm-modal-overlay" @click="showDeleteModal = false">
    <div class="confirm-modal-content" @click.stop>
      <h2 class="confirm-modal-title">Usuwanie listy</h2>
      <p class="confirm-modal-text">
        Czy na pewno chcesz usunąć listę "{{ listToDeleteName }}"?<br/>
        <strong class="text-danger">Wszystkie przedmioty w jej koszyku również zostaną usunięte.</strong>
      </p>
      <div class="confirm-modal-actions">
        <button class="confirm-btn confirm-btn-cancel" @click="showDeleteModal = false">Anuluj</button>
        <button class="confirm-btn confirm-btn-danger" @click="executeDeleteList">Tak, usuń</button>
      </div>
    </div>
  </div>

  <div v-if="showCloseModal" class="confirm-modal-overlay" @click="showCloseModal = false">
    <div class="confirm-modal-content confirm-modal-content--close" @click.stop>
      <h2 class="confirm-modal-title confirm-modal-title--close">Zamykanie zamówienia</h2>
      <p class="confirm-modal-text">
        Czy na pewno chcesz zamknąć listę "{{ listToCloseName }}"?<br/>
        Po zamknięciu członkowie nie będą mogli dodawać do niej kolejnych pozycji.
      </p>
      <div class="confirm-modal-actions">
        <button class="confirm-btn confirm-btn-cancel" @click="showCloseModal = false">Anuluj</button>
        <button class="confirm-btn confirm-btn-close" @click="executeCloseList">Zamknij zamówienie</button>
      </div>
    </div>
  </div>

  <AddListModal
    v-if="isTreasurer"
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
const students = ref([])
const showDeleteModal = ref(false)
const showCloseModal = ref(false)
const listToDeleteId = ref(null)
const listToCloseId = ref(null)
const selectedShopId = ref('')

const isTreasurer = computed(() => user.value?.role === 'treasurer')
const currentStudentId = computed(() => Number(user.value?.id))

const userLists = computed(() => allLists.value)
const ownLists = computed(() => allLists.value.filter(list => isOwnList(list)))
const otherTreasurerLists = computed(() => allLists.value.filter(list => !isOwnList(list)))

const listSections = computed(() => {
  if (!isTreasurer.value) {
    return [{
      key: 'open',
      title: '',
      subtitle: '',
      lists: userLists.value,
      emptyText: 'Brak otwartych list dla wybranego sklepu',
      emptySubtext: 'Skarbnik musi najpierw utworzyć otwartą listę zamówienia'
    }]
  }

  return [
    {
      key: 'own',
      title: 'Moje zamówienia',
      subtitle: 'Listy utworzone przez Ciebie. Tylko te listy możesz zamykać.',
      lists: ownLists.value,
      emptyText: 'Nie masz jeszcze własnych list zamówień',
      emptySubtext: 'Utwórz nową listę dla wybranego sklepu'
    },
    {
      key: 'others',
      title: 'Zamówienia innych skarbników',
      subtitle: 'Listy utworzone przez pozostałych skarbników Twojego koła.',
      lists: otherTreasurerLists.value,
      emptyText: 'Nie ma list utworzonych przez innych skarbników Twojego koła',
      emptySubtext: 'Gdy inny skarbnik z Twojego koła utworzy listę, pojawi się tutaj'
    }
  ]
})

const listToDelete = computed(() => allLists.value.find(list => list.id === listToDeleteId.value))
const listToClose = computed(() => allLists.value.find(list => list.id === listToCloseId.value))
const listToDeleteName = computed(() => listToDelete.value?.name || 'tę listę')
const listToCloseName = computed(() => listToClose.value?.name || activeList.value?.name || 'tę listę')

const fetchShops = async () => {
  try {
    const response = await fetch('http://localhost:8080/api/shops')
    const data = await response.json()
    shops.value = data
  } catch (error) {
    console.error('Błąd pobierania sklepów:', error)
  }
}

const fetchStudents = async () => {
  try {
    const response = await fetch('http://localhost:8080/api/students')
    if (!response.ok) throw new Error('Błąd sieci przy pobieraniu członków')
    students.value = await response.json()
  } catch (error) {
    console.error('Błąd pobierania członków:', error)
  }
}

const fetchLists = async () => {
  try {
    await fetchShops()
    if (isTreasurer.value) await fetchStudents()

    let fundings = []
    if (isTreasurer.value || user.value?.association_id) {
      const fundingsUrl = `http://localhost:8080/api/fundings?association_id=${user.value.association_id}`
      const fundingsResponse = await fetch(fundingsUrl)
      if (fundingsResponse.ok) {
        fundings = await fundingsResponse.json()
      }
    }

    const timestamp = new Date().getTime()
    const params = new URLSearchParams({ t: String(timestamp) })
    if (isTreasurer.value) {
      params.set('treasurer_view', 'true')
      if (user.value?.association_id) params.set('association_id', user.value.association_id)
    } else {
      params.set('open_only', 'true')
      if (user.value?.association_id) params.set('association_id', user.value.association_id)
      if (selectedShopId.value) params.set('shop_id', selectedShopId.value)
    }

    const response = await fetch(`http://localhost:8080/api/lists?${params.toString()}`, {
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
        console.warn('Brak przedmiotów na liście', e)
      }

      const foundShop = shops.value.find(s => s.shop_id === list.shop_id)
      const foundFunding = Array.isArray(fundings) ? fundings.find(f => f.funding_id === list.funding_id) : null
      const maxBudget = foundFunding ? (foundFunding.funding_price - foundFunding.spent_money) : 0
      const creator = list.student || students.value.find(student => Number(student.student_id) === Number(list.student_id))
      const itemTotal = items.reduce((sum, item) => sum + (Number(item.amount) || 0), 0)
      const totalPrice = items.reduce((sum, item) => sum + (Number(item.total_price) || 0), 0)

      return {
        ...list,
        id: list.shop_purchase_list_id,
        name: list.name?.trim() || `Zamówienie #${list.shop_purchase_list_id}`,
        shopName: foundShop ? foundShop.shop_name : 'Nieznany sklep',
        itemCount: items.length,
        itemTotal,
        totalPrice,
        participants: 1,
        maxBudget,
        isOpen: list.settlement_id === null || list.settlement_id === undefined,
        creatorName: creator ? `${creator.name} ${creator.surname}` : `Student #${list.student_id}`
      }
    }))

    allLists.value = processedLists
  } catch (error) {
    console.error('Krytyczny błąd pobierania list:', error)
  }
}

onMounted(() => {
  fetchLists()
})

const isOwnList = (list) => {
  return isTreasurer.value && Number(list?.student_id) === currentStudentId.value
}

const canCloseList = (list) => {
  return isOwnList(list) && list?.isOpen
}

const canDeleteList = (list) => {
  return isOwnList(list)
}

const formatMoney = (value) => {
  return Number(value || 0).toFixed(2)
}

const openList = (list) => {
  activeList.value = list
}

const handleNewList = async (listData) => {
  if (!isTreasurer.value) {
    toast.error('Tylko skarbnik może tworzyć listy zamówień.')
    return
  }

  try {
    const payload = {
      name: listData.name,
      priority: listData.priority || 1,
      cost: 0.0,
      created_at: new Date().toISOString(),
      funding_id: listData.fundingId || listData.funding_id,
      shop_id: listData.shopId || listData.shop_id,
      student_id: currentStudentId.value
    }

    const response = await fetch('http://localhost:8080/api/lists', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })

    if (!response.ok) {
      const err = await response.json().catch(() => ({}))
      console.error('Błąd backendu:', err)
      throw new Error(err.detail || 'Nie udało się zapisać listy w bazie')
    }

    await fetchLists()

    showAddListModal.value = false
    toast.success('Lista została poprawnie utworzona!')
  } catch (error) {
    console.error('Błąd zapisu listy:', error)
    toast.error(error.message || 'Wystąpił błąd podczas zapisu nowej listy.')
  }
}

const promptDeleteList = (list) => {
  if (!canDeleteList(list)) {
    toast.error('Możesz usunąć tylko własną listę zamówienia.')
    return
  }

  listToDeleteId.value = list.id
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
    console.error('Błąd podczas usuwania:', error)
    toast.error('Wystąpił problem przy usuwaniu listy.')
  } finally {
    showDeleteModal.value = false
    listToDeleteId.value = null
  }
}

const promptCloseList = (list) => {
  if (!canCloseList(list)) {
    toast.error('Możesz zamknąć tylko własną otwartą listę zamówienia.')
    return
  }

  listToCloseId.value = list.id
  showCloseModal.value = true
}

const executeCloseList = async () => {
  if (!listToCloseId.value) return

  try {
    const response = await fetch(`http://localhost:8080/api/lists/${listToCloseId.value}/close`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ student_id: currentStudentId.value })
    })

    if (!response.ok) {
      const err = await response.json().catch(() => ({}))
      throw new Error(err.detail || 'Nie udało się zamknąć listy')
    }

    toast.success('Lista została zamknięta.')
    activeList.value = null
    await fetchLists()
  } catch (error) {
    console.error('Błąd podczas zamykania listy:', error)
    toast.error(error.message || 'Wystąpił problem przy zamykaniu listy.')
  } finally {
    showCloseModal.value = false
    listToCloseId.value = null
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

.lists-filter {
  display: flex;
  align-items: center;
  gap: 1vw;
  margin-bottom: 2vw;
  padding: 1vw;
  background: rgba(15, 23, 42, 0.5);
  border: 0.08vw solid rgba(148, 163, 184, 0.15);
  border-radius: 0.8vw;
}

.lists-filter__label {
  color: rgba(226, 232, 240, 0.75);
  font-size: 0.95vw;
  font-weight: 800;
}

.lists-filter__select {
  min-width: 18vw;
  padding: 0.8vw 1vw;
  background: rgba(30, 41, 59, 0.65);
  border: 0.08vw solid rgba(148, 163, 184, 0.2);
  border-radius: 0.65vw;
  color: #ffffff;
  font-size: 0.95vw;
  font-family: 'Nunito', system-ui, sans-serif;
}

.lists-filter__select:focus {
  outline: none;
  border-color: rgba(96, 165, 250, 0.7);
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

.lists-group + .lists-group {
  margin-top: 3vw;
  padding-top: 2.5vw;
  border-top: 0.08vw solid rgba(148, 163, 184, 0.16);
}

.lists-group__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1vw;
  margin-bottom: 1.5vw;
}

.lists-group__title {
  color: #e2e8f0;
  font-size: 1.35vw;
  font-weight: 800;
  margin: 0 0 0.35vw 0;
}

.lists-group__subtitle {
  color: rgba(226, 232, 240, 0.58);
  font-size: 0.95vw;
  margin: 0;
}

.lists-group__count {
  min-width: 2.4vw;
  height: 2.4vw;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.5vw;
  background: rgba(59, 130, 246, 0.16);
  color: #bfdbfe;
  font-size: 1vw;
  font-weight: 800;
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

.lists-empty--compact {
  padding: 4vh;
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

.list-card--closed {
  opacity: 0.74;
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
  min-width: 0;
  overflow-wrap: anywhere;
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
  gap: 1vw;
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
  text-align: right;
}

.list-card__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.8vw;
}

.list-card__button {
  flex: 1;
  min-width: 7vw;
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

.list-card__button.close {
  background: rgba(245, 158, 11, 0.18);
  color: #fcd34d;
}

.list-card__button.close:hover {
  background: rgba(245, 158, 11, 0.3);
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
.confirm-modal-content--close { border-color: rgba(245, 158, 11, 0.32); }
@keyframes modalPop { 0% { transform: scale(0.9); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }
.confirm-modal-title { color: #ef4444; font-size: 2vw; font-weight: 800; margin: 0 0 1vw 0; }
.confirm-modal-title--close { color: #fcd34d; }
.confirm-modal-text { color: #e2e8f0; font-size: 1.1vw; line-height: 1.6; margin-bottom: 2.5vw; }
.text-danger { color: #fca5a5; font-weight: 700; }
.confirm-modal-actions { display: flex; gap: 1.5vw; justify-content: center; }
.confirm-btn { padding: 0.9vw 2.5vw; border-radius: 0.8vw; font-size: 1.1vw; font-weight: 800; cursor: pointer; border: none; transition: all 0.2s ease; }
.confirm-btn-cancel { background: rgba(148, 163, 184, 0.15); color: #e2e8f0; }
.confirm-btn-cancel:hover { background: rgba(148, 163, 184, 0.3); color: #ffffff; }
.confirm-btn-danger { background: linear-gradient(135deg, #ef4444, #dc2626); color: #ffffff; box-shadow: 0 10px 20px rgba(239, 68, 68, 0.3); }
.confirm-btn-danger:hover { transform: translateY(-0.3vh); filter: brightness(1.1); box-shadow: 0 14px 28px rgba(239, 68, 68, 0.5); }
.confirm-btn-close { background: linear-gradient(135deg, #f59e0b, #d97706); color: #ffffff; box-shadow: 0 10px 20px rgba(245, 158, 11, 0.25); }
.confirm-btn-close:hover { transform: translateY(-0.3vh); filter: brightness(1.08); box-shadow: 0 14px 28px rgba(245, 158, 11, 0.4); }
</style>
