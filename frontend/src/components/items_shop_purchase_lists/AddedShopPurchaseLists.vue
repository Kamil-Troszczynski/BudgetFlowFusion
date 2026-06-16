<template>
  <div v-if="!activeList" class="lists-section">
    <div class="lists-header">
      <div class="lists-title-section">
        <h2 class="lists-title">{{ isTreasurer ? 'Koszyki sklepowe' : 'Otwarte koszyki sklepowe' }}</h2>
        <p class="lists-subtitle">
          {{ isTreasurer ? 'Zarządzaj wszystkimi listami koła z tego poziomu' : 'Wybierz otwartą listę dla sklepu lub utwórz nową i dodaj swoje pozycje' }}
        </p>
      </div>
      <button class="lists-add-button" @click="showAddListModal = true">Nowy koszyk sklepowy</button>
    </div>

    <div class="lists-filter-bar">
      <div v-if="!isTreasurer" class="lists-filter">
        <label class="lists-filter__label">Sklep</label>
        <select v-model="selectedShopId" class="lists-filter__select" @change="fetchLists">
          <option value="">Wszystkie sklepy</option>
          <option v-for="shop in shops" :key="shop.shop_id" :value="shop.shop_id">
            {{ shop.shop_name }}
          </option>
        </select>
      </div>
      <div v-else class="search-placeholder-block"></div>

      <div class="view-toggle-container">
        <button 
          class="toggle-view-btn" 
          :class="{ 'toggle-view-btn--active': currentLayout === 'grid' }"
          @click="currentLayout = 'grid'"
        >
          Kafelki
        </button>
        <button 
          class="toggle-view-btn" 
          :class="{ 'toggle-view-btn--active': currentLayout === 'list' }"
          @click="currentLayout = 'list'"
        >
          Lista
        </button>
      </div>
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

      <template v-else>
        <div v-if="currentLayout === 'grid'" class="lists-grid">
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
              <p class="list-card__detail">
                <span class="list-card__label">Utworzył:</span>
                <span class="list-card__value">{{ list.creatorName }}</span>
              </p>
              <p v-if="list.lastContributionTime" class="list-card__detail">
                <span class="list-card__label">Ostatnia edycja:</span>
                <span class="list-card__value">{{ formatTimeAgo(list.lastContributionTime) }}</span>
              </p>
              <p v-if="list.lastContributorName" class="list-card__detail">
                <span class="list-card__label">Ostatnio edytował:</span>
                <span class="list-card__value">{{ list.lastContributorName }}</span>
              </p>
              <p v-if="list.contributedStudentsNameList && list.contributedStudentsNameList.length > 0" class="list-card__detail">
                <span class="list-card__label">Współtwórcy:</span>
                <span class="list-card__value">{{ list.contributedStudentsNameList.join(', ') }}</span>
              </p>
            </div>
            <div class="list-card__actions">
              <button class="list-card__button view" @click="openList(list)">Otwórz listę</button>
              <button v-if="canCloseList(list)" class="list-card__button close" @click.stop="promptCloseList(list)">Zamknij</button>
              <button v-if="canDeleteList(list)" class="list-card__button delete" @click.stop="promptDeleteList(list)">Usuń</button>
            </div>
          </div>
        </div>

        <div v-else-if="currentLayout === 'list'" class="excel-table-wrapper custom-scrollbar">
          <table class="excel-list-table">
            <thead>
              <tr>
                <th>Nazwa zamówienia</th>
                <th>Sklep</th>
                <th>Pozycje / Sztuki</th>
                <th>Suma Brutto</th>
                <th>Status</th>
                <th>Utworzył</th>
                <th>Ostatnia edycja</th>
                <th>Ostatni edytor</th>
                <th>Współtwórcy</th>
                <th>Akcje</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="list in section.lists" :key="list.id" :class="{ 'row-closed': !list.isOpen }">
                <td class="font-bold text-white">{{ list.name }}</td>
                <td><span class="table-shop-badge">{{ list.shopName }}</span></td>
                <td>{{ list.itemCount }} poz. / {{ list.itemTotal }} szt.</td>
                <td class="font-mono text-blue font-bold">{{ formatMoney(list.totalPrice) }} PLN</td>
                <td>
                  <span :class="list.isOpen ? 'status-open-tag' : 'status-closed-tag'">
                    {{ list.isOpen ? 'Otwarta' : 'Zamknięta' }}
                  </span>
                </td>
                <td>{{ list.creatorName }}</td>
                <td>{{ list.lastContributionTime ? formatTimeAgo(list.lastContributionTime) : '-' }}</td>
                <td>{{ list.lastContributorName || '-' }}</td>
                <td class="max-cell-width">{{ list.contributedStudentsNameList?.join(', ') || '-' }}</td>
                <td>
                  <div class="table-row-actions">
                    <button class="table-btn view" @click="openList(list)">Otwórz</button>
                    <button v-if="canCloseList(list)" class="table-btn close" @click.stop="promptCloseList(list)">Zamknij</button>
                    <button v-if="canDeleteList(list)" class="table-btn delete" @click.stop="promptDeleteList(list)">Usuń</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </section>
  </div>

  <ShopPurchaseListDetails
    v-else-if="activeList"
    :list="activeList"
    :can-manage-items="true" 
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
const currentLayout = ref('grid')

const isTreasurer = computed(() => user.value?.role === 'treasurer')
const currentStudentId = computed(() => Number(user.value?.id))

const userLists = computed(() => allLists.value)
const ownLists = computed(() => allLists.value.filter(list => Number(list.student_id) === currentStudentId.value))
const otherTreasurerLists = computed(() => allLists.value.filter(list => Number(list.student_id) !== currentStudentId.value))

const listSections = computed(() => {
  if (!isTreasurer.value) {
    return [{
      key: 'open',
      title: '',
      subtitle: '',
      lists: userLists.value,
      emptyText: 'Brak aktywnego zamówienia dla wybranego sklepu',
      emptySubtext: 'Utwórz nowe klikając przycisk "+ Nowa lista" na górze strony'
    }]
  }

  return [
    {
      key: 'own',
      title: 'Zamówienia utworzone przeze mnie',
      subtitle: 'Listy zakupowe zarejestrowane z Twojego konta.',
      lists: ownLists.value,
      emptyText: 'Nie utworzyłeś jeszcze żadnej listy zakupowej',
      emptySubtext: 'Kliknij przycisk powyżej, aby zainicjować koszyk'
    },
    {
      key: 'others',
      title: 'Wszystkie pozostałe zamówienia koła',
      subtitle: 'Listy zainicjowane przez innych członków organizacji. Jako skarbnik masz do nich pełne prawa modyfikacji.',
      lists: otherTreasurerLists.value,
      emptyText: 'Brak list od innych członków organizacji',
      emptySubtext: 'Gdy ktoś inny założy listę, pojawi się ona w tej sekcji'
    }
  ]
})

const listToDelete = computed(() => allLists.value.find(list => list.id === listToDeleteId.value))
const listToClose = computed(() => allLists.value.find(list => list.id === listToCloseId.value))
const listToDeleteName = computed(() => listToDelete.value?.name || 'tę listę')
const listToCloseName = computed(() => listToClose.value?.name || activeList.value?.name || 'tę listę')

const formatTimeAgo = (dateInput) => {
  if (!dateInput) return '-'
  const dateStr = String(dateInput).endsWith('Z') || String(dateInput).includes('+') ? dateInput : `${dateInput}Z`
  const date = new Date(dateStr)
  const now = new Date()
  const serverTimeMs = date.getTime() + (2 * 60 * 60 * 1000)
  const diffMs = now.getTime() - serverTimeMs
  if (diffMs < 0 && diffMs > -60000) return 'przed chwilą'
  const diffSec = Math.floor(diffMs / 1000)
  const diffMin = Math.floor(diffSec / 60)
  const diffHour = Math.floor(diffMin / 60)
  const diffDay = Math.floor(diffHour / 24)
  if (diffSec < 60) return 'przed chwilą'
  if (diffMin < 60) return `${diffMin} min temu`
  if (diffHour < 24) return `${diffHour} godz. temu`
  return `${diffDay} dni temu`
}

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
    await fetchStudents()

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

      const studentIdsSet = new Set()
      let latestTime = null
      let latestContributorId = null

      items.forEach(item => {
        const sId = item.student_id
        if (sId) {
          studentIdsSet.add(sId)
        }
        const itemTime = item.updated_at || item.created_at
        const itemTimeMs = itemTime ? new Date(itemTime).getTime() : null
        if (itemTimeMs && (!latestTime || itemTimeMs > latestTime)) {
          latestTime = itemTimeMs
          latestContributorId = sId
        }
      })

      const lastEditedByStudent = students.value.find(s => Number(s.student_id) === Number(latestContributorId))
      const lastContributorName = lastEditedByStudent ? `${lastEditedByStudent.name} ${lastEditedByStudent.surname}` : (latestContributorId ? `Student #${latestContributorId}` : null)

      const contributedStudentsNameList = Array.from(studentIdsSet).map(id => {
        const match = students.value.find(s => Number(s.student_id) === Number(id))
        return match ? `${match.name} ${match.surname.substring(0, 1)}.` : `Student #${id}`
      })

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
        creatorName: creator ? `${creator.name} ${creator.surname}` : `Student #${list.student_id}`,
        lastContributionTime: latestTime ? new Date(latestTime).toISOString() : null,
        lastContributor_id: latestContributorId,
        lastContributorName,
        contributedStudents_id: Array.from(studentIdsSet),
        contributedStudentsNameList
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
  return Number(list?.student_id) === currentStudentId.value
}

// Zmiana reguł: Tylko skarbnik może zamykać i usuwać dowolne listy
const canCloseList = (list) => {
  return isTreasurer.value && list?.isOpen
}

const canDeleteList = (list) => {
  return isTreasurer.value
}

const formatMoney = (value) => {
  return Number(value || 0).toFixed(2)
}

const openList = (list) => {
  activeList.value = list
}

const handleNewList = async (listData) => {
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
      throw new Error(err.detail || 'Nie udało się zapisać listy w bazie')
    }

    await fetchLists()
    showAddListModal.value = false
    toast.success('Lista została poprawnie utworzona!')
  } catch (error) {
    toast.error(error.message || 'Wystąpił błąd podczas zapisu nowej listy.')
  }
}

const promptDeleteList = (list) => {
  if (!canDeleteList(list)) {
    toast.error('Tylko skarbnik ma uprawnienia do usuwania zamówień.')
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
    toast.error('Wystąpił problem przy usuwaniu listy.')
  } finally {
    showDeleteModal.value = false
    listToDeleteId.value = null
  }
}

const promptCloseList = (list) => {
  if (!canCloseList(list)) {
    toast.error('Tylko skarbnik ma uprawnienia do zamykania zamówień.')
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

.shops-header-actions {
  display: flex;
  gap: 0.8vw;
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
  box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3);
}

.lists-add-button:hover {
  transform: translateY(-0.2vh);
  box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4);
}

.lists-filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 2vw;
  margin-bottom: 2vw;
  padding: 1vw;
  background: rgba(15, 23, 42, 0.5);
  border: 0.08vw solid rgba(148, 163, 184, 0.15);
  border-radius: 0.8vw;
}

.lists-filter {
  display: flex;
  align-items: center;
  gap: 1vw;
}

.search-placeholder-block {
  flex: 1;
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
  outline: none;
}

.lists-filter__select:focus {
  border-color: rgba(96, 165, 250, 0.7);
}

.view-toggle-container {
  display: flex;
  background: rgba(30, 41, 59, 0.8);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 0.6vw;
  padding: 0.2vw;
}

.toggle-view-btn {
  background: transparent;
  border: none;
  color: #94a3b8;
  padding: 0.5vw 1.2vw;
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

.lists-empty--compact { padding: 4vh; }
.lists-empty-text { font-size: 1.2vw; font-weight: 600; color: rgba(226, 232, 240, 0.8); margin: 0 0 0.5vh 0; }
.lists-empty-subtext { font-size: 0.95vw; color: rgba(226, 232, 240, 0.5); margin: 0; }

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

.list-card--closed { opacity: 0.74; }

.list-card:hover {
  background: rgba(15, 23, 42, 0.8);
  border-color: rgba(59, 130, 246, 0.3);
  transform: translateY(-0.4vh);
}

.list-card__header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.5vw; gap: 1vw; }
.list-card__title { padding: 0.4vw 0.0vw; font-size: 1.25vw; font-weight: 700; color: #ffffff; margin: 0; flex: 1; min-width: 0; overflow-wrap: anywhere; }
.list-card__shop { padding: 0.4vw 0.8vw; border-radius: 0.4vw; font-size: 1.25vw; font-weight: 600; background: rgba(59, 130, 246, 0.2); color: #93c5fd; white-space: nowrap; }

.list-card__content { flex: 1; display: flex; flex-direction: column; gap: 0.8vw; margin-bottom: 1.5vw; }
.list-card__detail { display: flex; align-items: center; justify-content: space-between; gap: 1vw; font-size: 0.95vw; margin: 0; }
.list-card__label { color: rgba(226, 232, 240, 0.6); font-weight: 600; }
.list-card__value { color: #ffffff; font-weight: 500; text-align: right; }

.list-card__actions { display: flex; flex-wrap: wrap; gap: 0.8vw; }

.list-card__button { 
  flex: 1; 
  min-width: 7vw; 
  padding: 0.8vw; 
  border: none; 
  border-radius: 0.6vw; 
  font-size: 0.9vw; 
  font-weight: 700; 
  cursor: pointer; 
  transition: all 0.2s ease; 
  font-family: 'Nunito', system-ui, sans-serif;
}
.list-card__button.view { background: rgba(59, 130, 246, 0.18); color: #93c5fd; border: 1px solid rgba(59, 130, 246, 0.3); }
.list-card__button.view:hover { background: #2563eb; color: white; border-color: #2563eb; transform: translateY(-2px); }
.list-card__button.close { background: rgba(245, 158, 11, 0.18); color: #fcd34d; border: 1px solid rgba(245, 158, 11, 0.3); }
.list-card__button.close:hover { background: #d97706; color: white; border-color: #d97706; transform: translateY(-2px); }
.list-card__button.delete { background: rgba(239, 68, 68, 0.15); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.3); }
.list-card__button.delete:hover { background: #dc2626; color: white; border-color: #dc2626; transform: translateY(-2px); }

.excel-table-wrapper { background: rgba(15, 23, 42, 0.4); border: 1px solid rgba(148, 163, 184, 0.15); border-radius: 0.8vw; overflow-x: auto; width: 100%; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2); }
.excel-list-table { width: 100%; border-collapse: collapse; text-align: left; font-size: 0.85vw; min-width: 1100px; }
.excel-list-table th, .excel-list-table td { padding: 1vw 1.2vw; border-bottom: 1px solid rgba(148, 163, 184, 0.1); vertical-align: middle; }
.excel-list-table th { background: rgba(30, 41, 59, 0.8); color: #94a3b8; font-weight: 700; text-transform: uppercase; font-size: 0.75vw; letter-spacing: 0.05em; border-bottom: 2px solid rgba(148, 163, 184, 0.2); }
.excel-list-table tr:hover { background: rgba(59, 130, 246, 0.02); }
.row-closed { opacity: 0.65; }

.table-shop-badge { padding: 0.2vw 0.5vw; background: rgba(59, 130, 246, 0.15); color: #60a5fa; border-radius: 0.4vw; font-weight: 700; }
.status-open-tag { color: #34d399; font-weight: 700; }
.status-closed-tag { color: #fca5a5; font-weight: 700; }
.max-cell-width { max-width: 14vw; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.table-row-actions { display: flex; gap: 0.4vw; }
.table-btn { 
  padding: 0.5vw 0.9vw; 
  border: none; 
  border-radius: 0.5vw; 
  font-size: 0.8vw; 
  font-weight: 700; 
  cursor: pointer; 
  transition: all 0.2s ease; 
  font-family: 'Nunito', system-ui, sans-serif;
}
.table-btn.view { background: rgba(59, 130, 246, 0.15); color: #93c5fd; border: 1px solid rgba(59, 130, 246, 0.25); }
.table-btn.view:hover { background: #2563eb; color: white; border-color: #2563eb; }
.table-btn.close { background: rgba(245, 158, 11, 0.15); color: #fcd34d; border: 1px solid rgba(245, 158, 11, 0.25); }
.table-btn.close:hover { background: #d97706; color: white; border-color: #d97706; }
.table-btn.delete { background: rgba(239, 68, 68, 0.15); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.25); }
.table-btn.delete:hover { background: #dc2626; color: white; border-color: #dc2626; }

.confirm-modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background-color: rgba(5, 8, 22, 0.85); display: flex; align-items: center; justify-content: center; z-index: 9999; backdrop-filter: blur(8px); }
.confirm-modal-content { background: #0f172a; border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 1.5vw; padding: 3vw; width: 90%; max-width: 32vw; text-align: center; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7); animation: modalPop 0.3s cubic-bezier(0.34, 1.56, 0.64, 1); }
.confirm-modal-content--close { border-color: rgba(245, 158, 11, 0.32); }
.confirm-modal-title { color: #ef4444; font-size: 2vw; font-weight: 800; margin: 0 0 1vw 0; }
.confirm-modal-title--close { color: #fcd34d; }
.confirm-modal-text { color: #e2e8f0; font-size: 1.1vw; line-height: 1.6; margin-bottom: 2.5vw; }
.text-danger { color: #fca5a5; font-weight: 700; }

.confirm-btn { padding: 0.9vw 2.5vw; border-radius: 0.8vw; font-size: 1.1vw; font-weight: 800; cursor: pointer; border: none; transition: all 0.2s ease; }
.confirm-btn-cancel { background: rgba(148, 163, 184, 0.15); color: #e2e8f0; }
.confirm-btn-cancel:hover { background: rgba(148, 163, 184, 0.3); color: #ffffff; }
.confirm-btn-danger { background: linear-gradient(135deg, #ef4444, #dc2626); color: #ffffff; box-shadow: 0 10px 20px rgba(239, 68, 68, 0.3); }
.confirm-btn-danger:hover { transform: translateY(-0.3vh); filter: brightness(1.1); box-shadow: 0 14px 28px rgba(239, 68, 68, 0.5); }
.confirm-btn-close { background: linear-gradient(135deg, #f59e0b, #d97706); color: #ffffff; box-shadow: 0 10px 20px rgba(245, 158, 11, 0.25); }
.confirm-btn-close:hover { transform: translateY(-0.3vh); filter: brightness(1.08); box-shadow: 0 14px 28px rgba(245, 158, 11, 0.4); }

.font-bold { font-weight: 700; }
.font-mono { font-family: monospace; }
.text-white { color: #ffffff; }
.custom-scrollbar::-webkit-scrollbar { height: 7px; background: rgba(30, 41, 59, 0.5); border-radius: 10px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(148, 163, 184, 0.25); border-radius: 10px; }
</style>