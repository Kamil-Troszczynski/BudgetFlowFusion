<template>
  <div class="dashboard">
    <header class="dashboard__header">
      <div class="dashboard__container">
        <div class="dashboard__header-content">
          <div class="dashboard__logo-section">
            <img src="/logo.png" alt="Logo" class="dashboard__logo" />
            <h1 class="dashboard__title">BudgetFlowFusion</h1>
          </div>
          <nav class="dashboard__nav">
            <button 
              v-for="(link, index) in navLinks" 
              :key="index"
              class="dashboard__nav-link"
              :class="{ active: activeNavIndex === index }"
              @click="navigateToSection(index)"
            >
              {{ link }}
            </button>
          </nav>
          <div class="dashboard__user-section">
            <div class="dashboard__user-menu" ref="userMenuRef">
              <button 
                class="dashboard__user-name"
                @click="showUserMenu = !showUserMenu"
              >
                {{ user.firstName }} {{ user.lastName }}
              </button>
              <div v-if="showUserMenu" class="dashboard__user-dropdown">
                <button class="dashboard__dropdown-item" @click="showEditProfileModal = true"> Edytuj profil </button>
                <button class="dashboard__dropdown-item" @click="handleLogout"> Wyloguj się </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>

    <main class="dashboard__main">
      <div class="dashboard__container">
        <div class="dashboard__sections-container" ref="sectionsContainer" @scroll="handleScroll">
          <section class="dashboard__section" v-if="showPulpit">
            <section class="dashboard__welcome">
              <h2 class="dashboard__welcome-title">
                Cześć {{ user.firstName }}
              </h2>
            </section>

            <div class="dashboard__user-info-card">
              <div class="dashboard__user-info-header">
                <h2 class="dashboard__user-info-title">Moje informacje</h2>
              </div>
              <div class="dashboard__user-info-content">
                <div class="dashboard__user-info-row">
                  <span class="dashboard__user-info-icon">{{ user.role === 'member' ? '🧩' : '💰' }}</span>
                  <span class="dashboard__user-info-label">Rola</span>
                  <span class="dashboard__user-info-value">{{ user.role === 'member' ? 'Członek koła naukowego' : 'Skarbnik' }}</span>
                </div>
                <div class="dashboard__user-info-row">
                  <span class="dashboard__user-info-icon">📬</span>
                  <span class="dashboard__user-info-label">E-mail</span>
                  <span class="dashboard__user-info-value">{{ user.email }}</span>
                </div>
                <div class="dashboard__user-info-row">
                  <span class="dashboard__user-info-icon">🏛️</span>
                  <span class="dashboard__user-info-label">Koło naukowe</span>
                  <span class="dashboard__user-info-value">{{ user.circleName }}</span>
                </div>
                <div class="dashboard__user-info-row">
                  <span class="dashboard__user-info-icon">🔧</span>
                  <span class="dashboard__user-info-label">Sekcja</span>
                  <span class="dashboard__user-info-value">{{ formatPosition(user.position) }}</span>
                </div>
                <div class="dashboard__user-info-row">
                  <span class="dashboard__user-info-icon">{{ user.inSAP ? '✅' : '❌' }}</span>
                  <span class="dashboard__user-info-label">SAP</span>
                  <span class="dashboard__user-info-value">{{ user.inSAP ? 'Jestem w SAP' : 'Nie jestem w SAP' }}</span>
                </div>
              </div>
            </div>

            <section class="dashboard__grid">
              <div v-if="user.role === 'treasurer'" class="dashboard__card budget-card">
                <div class="dashboard__card-header">
                  <h3 class="dashboard__card-title">💰 Przegląd budżetu</h3>
                  <span class="dashboard__card-badge">Miesiąc</span>
                </div>
                <div class="dashboard__card-body">
                  <div 
                    v-for="stat in budgetStats" 
                    :key="stat.label"
                    class="budget-stat"
                  >
                    <p class="budget-stat__label">{{ stat.label }}</p>
                    <p class="budget-stat__value" :class="stat.class">{{ stat.value }}</p>
                  </div>
                  <div class="budget-progress">
                    <div class="budget-progress__bar">
                      <div class="budget-progress__fill" style="width: 24.7%"></div>
                    </div>
                    <p class="budget-progress__text">24.7% wydane</p>
                  </div>
                </div>
              </div>

              <div v-if="user.role === 'treasurer'" class="dashboard__card transactions-card">
                <div class="dashboard__card-header">
                  <h3 class="dashboard__card-title">📋 Ostatnie transakcje</h3>
                  <button class="dashboard__card-link">Wszystkie →</button>
                </div>
                <div class="dashboard__card-body">
                  <div 
                    v-for="transaction in recentTransactions" 
                    :key="transaction.id"
                    class="transaction-item"
                  >
                    <div class="transaction-item__info">
                      <p class="transaction-item__title">{{ transaction.title }}</p>
                      <p class="transaction-item__date">{{ transaction.date }}</p>
                    </div>
                    <p class="transaction-item__amount" :class="transaction.amountClass">
                      {{ transaction.amount }}
                    </p>
                  </div>
                  <button class="dashboard__btn-secondary">+ Nowa transakcja</button>
                </div>
              </div>
              <div class="dashboard__card actions-card">
                <div class="dashboard__card-header">
                  <h3 class="dashboard__card-title">⚡ Szybki dostęp</h3>
                </div>
                <div class="dashboard__card-body">
                  <button 
                    v-for="action in quickActions" 
                    :key="action.id"
                    class="dashboard__quick-action"
                  >
                    <span class="dashboard__quick-action-icon">{{ action.icon }}</span>
                    <span class="dashboard__quick-action-text">{{ action.label }}</span>
                  </button>
                </div>
              </div>

              <div v-if="user.role === 'treasurer'" class="dashboard__card stats-card">
                <div class="dashboard__card-header">
                  <h3 class="dashboard__card-title">📈 Statystyki</h3>
                </div>
                <div class="dashboard__card-body">
                  <div 
                    v-for="stat in statistics" 
                    :key="stat.label"
                    class="stat-row"
                  >
                    <p class="stat-row__label">{{ stat.label }}</p>
                    <p class="stat-row__value">{{ stat.value }}</p>
                  </div>
                </div>
              </div>
            </section>
          </section>

          <section class="dashboard__section" v-if="!showPulpit && (navLinks[activeNavIndex]?.includes('Dodane') || navLinks[activeNavIndex]?.includes('przedmioty'))">
            <AddedItems />
          </section>

          <section class="dashboard__section" v-if="!showPulpit && navLinks[activeNavIndex]?.includes('Listy') && navLinks[activeNavIndex]?.includes('zakupów')">
            <AddedShopPurchaseLists />
          </section>
        </div>
      </div>
    </main>

    <div v-if="showEditProfileModal" class="modal-overlay" @click="showEditProfileModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2 class="modal-title">Edytuj profil</h2>
          <button class="modal-close" @click="showEditProfileModal = false">✕</button>
        </div>
        
        <form class="edit-form" @submit.prevent="handleSaveProfile">
          <div class="edit-form-group">
            <label class="edit-form-label">Imię</label>
            <input 
              v-model="editFormData.firstName"
              type="text" 
              placeholder="Jan"
              class="edit-form-input"
              required
            />
          </div>

          <div class="edit-form-group">
            <label class="edit-form-label">Nazwisko</label>
            <input 
              v-model="editFormData.lastName"
              type="text" 
              placeholder="Kowalski"
              class="edit-form-input"
              required
            />
          </div>

          <div class="edit-form-group">
            <label class="edit-form-label">E-mail</label>
            <input 
              v-model="editFormData.email"
              type="email" 
              placeholder="name@example.com"
              class="edit-form-input"
              required
            />
          </div>

          <div class="edit-form-group">
            <label class="edit-form-label">Sekcja</label>
            <select 
              v-model="editFormData.position"
              required
              class="edit-form-select"
            >
              <option value="" disabled>Wybierz sekcję</option>
              <option value="elektronika">Elektronika</option>
              <option value="autonomia">Autonomia</option>
              <option value="mechanika">Mechanika</option>
              <option value="embedded">Embedded</option>
            </select>
          </div>

          <div v-if="user.role === 'treasurer'" class="edit-form__role-toggle">
            <span class="edit-form__role-label">Rola</span>
            <button 
              class="edit-form__toggle" 
              :class="{ 'is-treasurer': editFormData.role === 'treasurer' }"
              type="button"
              @click="toggleEditRole"
              :disabled="editFormData.role === 'member'"
            >
              <span class="edit-form__toggle-text">
                {{ editFormData.role === 'member' ? 'Zwykły członek koła' : 'Skarbnik' }}
              </span>
              <span class="edit-form__toggle-indicator"></span>
            </button>
            <span v-if="editFormData.role === 'member'" class="edit-form__role-info">
              Po zmianie na zwykłego członka nie będziesz mógł wrócić do roli skarbnika
            </span>
          </div>

          <div class="edit-form__role-toggle">
            <span class="edit-form__role-label">SAP</span>
            <button 
              class="edit-form__toggle" 
              :class="{ 'is-in-sap': editFormData.inSAP === true }"
              type="button"
              @click="toggleEditSAP"
            >
              <span class="edit-form__toggle-text">
                {{ editFormData.inSAP ? 'Jestem w SAP' : 'Nie jestem w SAP' }}
              </span>
              <span class="edit-form__toggle-indicator"></span>
            </button>
          </div>

          <div class="modal-actions">
            <button type="button" class="modal-btn modal-btn-cancel" @click="showEditProfileModal = false">Anuluj</button>
            <button type="submit" class="modal-btn modal-btn-save">Zapisz zmiany</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted, watch } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { useRouter } from 'vue-router'
import AddedItems from '@/components/items_shop_purchase_lists/AddedItems.vue'
import AddedShopPurchaseLists from '@/components/items_shop_purchase_lists/AddedShopPurchaseLists.vue'

const router = useRouter()
const { user, logout } = useAuth()
const showUserMenu = ref(false)
const showEditProfileModal = ref(false)
const activeNavIndex = ref(0)
const sectionsContainer = ref(null)
const userMenuRef = ref(null)

const editFormData = ref({
  firstName: '',
  lastName: '',
  email: '',
  position: '',
  inSAP: false,
  role: ''
})

const navLinks = computed(() => {
  if (user.value?.role === 'member') {
    return ['Pulpit', 'Dodane przedmioty', 'Listy zakupów']
  }
  return ['Pulpit', 'Dodane przedmioty', 'Listy zakupów', 'Budżet', 'Transakcje']
})

const showPulpit = computed(() => activeNavIndex.value === 0)

const navigateToSection = (index) => {
  activeNavIndex.value = index
  if (sectionsContainer.value) {
    const sectionWidth = sectionsContainer.value.offsetWidth
    sectionsContainer.value.scrollTo({
      left: sectionWidth * index,
      behavior: 'smooth'
    })
  }
}

const handleScroll = () => {
  if (sectionsContainer.value) {
    const scrollLeft = sectionsContainer.value.scrollLeft
    const sectionWidth = sectionsContainer.value.offsetWidth
    const newIndex = Math.round(scrollLeft / sectionWidth)
    if (newIndex !== activeNavIndex.value && newIndex >= 0 && newIndex < navLinks.value.length) {
      activeNavIndex.value = newIndex
    }
  }
}

const handleKeydown = (e) => {
  if (e.key === 'ArrowRight' && activeNavIndex.value < navLinks.value.length - 1) {
    navigateToSection(activeNavIndex.value + 1)
  } else if (e.key === 'ArrowLeft' && activeNavIndex.value > 0) {
    navigateToSection(activeNavIndex.value - 1)
  }
}

const handleClickOutside = (e) => {
  if (userMenuRef.value && !userMenuRef.value.contains(e.target)) {
    showUserMenu.value = false
  }
}

const resetEditFormData = () => {
  if (user.value) {
    editFormData.value = {
      firstName: user.value.firstName || '',
      lastName: user.value.lastName || '',
      email: user.value.email || '',
      position: user.value.position || '',
      inSAP: user.value.inSAP || false,
      role: user.value.role || 'member'
    }
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
  document.addEventListener('click', handleClickOutside)
  resetEditFormData()
})

watch(showEditProfileModal, (newValue) => {
  if (newValue) {
    resetEditFormData()
  }
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
  document.removeEventListener('click', handleClickOutside)
})

const toggleEditRole = () => {
  if (user.value?.role === 'treasurer') {
    editFormData.value.role = editFormData.value.role === 'member' ? 'treasurer' : 'member'
  }
}

const toggleEditSAP = () => {
  editFormData.value.inSAP = !editFormData.value.inSAP
}

const handleSaveProfile = () => {
  if (user.value) {
    user.value.firstName = editFormData.value.firstName
    user.value.lastName = editFormData.value.lastName
    user.value.email = editFormData.value.email
    user.value.position = editFormData.value.position
    user.value.inSAP = editFormData.value.inSAP
    user.value.role = editFormData.value.role
    
    localStorage.setItem('user', JSON.stringify(user.value))
    
    showEditProfileModal.value = false
    showUserMenu.value = false
  }
}

const budgetStats = [
  { label: 'Budżet dostępny', value: '5 000,00 PLN', class: '' },
  { label: 'Wydane', value: '1 234,56 PLN', class: 'warning' },
  { label: 'Pozostało', value: '3 765,44 PLN', class: 'success' }
]

const recentTransactions = [
  { 
    id: 1,
    title: 'Zakup materiałów promocyjnych', 
    date: 'Dzisiaj', 
    amount: '-450,00 PLN',
    amountClass: ''
  },
  { 
    id: 2,
    title: 'Wpłata członkowska', 
    date: 'Wczoraj', 
    amount: '+200,00 PLN',
    amountClass: 'success-text'
  },
  { 
    id: 3,
    title: 'Koszty wynajęcia sali', 
    date: '3 dni temu', 
    amount: '-784,56 PLN',
    amountClass: ''
  }
]

const quickActions = [
  { id: 1, icon: '➕', label: 'Dodaj przedmiot' },
  { id: 2, icon: '🛒', label: 'Dodaj listę zakupów' },
  { id: 3, icon: '👥', label: 'Członkowie koła' }
]

const statistics = [
  { label: 'Transakcje ten miesiąc', value: '12' },
  { label: 'Średnia transakcji', value: '102,88 PLN' },
  { label: 'Największy wydatek', value: '784,56 PLN' },
  { label: 'Liczba członków', value: '8' }
]

const formatPosition = (position) => {
  if (!position) return 'Nie wybrana'
  const positionNames = {
    'elektronika': 'Elektronika',
    'autonomia': 'Autonomia',
    'mechanika': 'Mechanika',
    'embedded': 'Embedded'
  }
  return positionNames[position] || position
}

const handleLogout = () => {
  logout()
  router.push('/login')
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;500;600;700;800&display=swap');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.dashboard {
  min-height: 100dvh;
  background: #050816;
  color: #ffffff;
  font-family: 'Nunito', system-ui, sans-serif;
}

.dashboard__container {
  max-width: 85vw;
  margin: 0 auto;
  padding: 0 1.5vw;
}

.dashboard__header {
  background: rgba(9, 14, 32, 0.5);
  border-bottom: 0.08vw solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(0.7vw);
  position: sticky;
  top: 0;
  z-index: 100;
  padding: 0.8vh 0;
}

.dashboard__header-content {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 2vw;
}

.dashboard__logo-section {
  display: flex;
  align-items: center;
  gap: 1.5vw;
}

.dashboard__logo {
  width: 3.5vw;
  height: 3.5vw;
  border-radius: 0.5vw;
  object-fit: contain;
}

.dashboard__title {
  font-size: 1.8vw;
  font-weight: 800;
  background: linear-gradient(135deg, #3b82f6, #60a5fa);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.dashboard__nav {
  display: flex;
  gap: 0.5vw;
  justify-content: center;
}

.dashboard__nav-link {
  background: none;
  border: none;
  color: rgba(226, 232, 240, 0.6);
  font-size: 1vw;
  font-weight: 600;
  padding: 0.5vw 1.2vw;
  cursor: pointer;
  border-radius: 0.5vw;
  transition: all 0.2s ease;
  font-family: 'Nunito', system-ui, sans-serif;
}

.dashboard__nav-link:hover {
  color: rgba(226, 232, 240, 0.9);
  background: rgba(59, 130, 246, 0.1);
}

.dashboard__nav-link.active {
  color: #93c5fd;
  background: rgba(59, 130, 246, 0.2);
}

.dashboard__user-section {
  display: flex;
  align-items: center;
  gap: 2vw;
  justify-self: end;
}

.dashboard__user-menu {
  position: relative;
  margin-left: 6vw;
}

.dashboard__user-name {
  background: none;
  border: none;
  font-weight: 600;
  font-size: 1vw;
  color: rgba(226, 232, 240, 0.8);
  cursor: pointer;
  padding: 0.6vw 1.2vw;
  border-radius: 0.5vw;
  transition: all 0.2s ease;
  font-family: 'Nunito', system-ui, sans-serif;
}

.dashboard__user-name:hover {
  color: rgba(226, 232, 240, 0.9);
  background: rgba(59, 130, 246, 0.1);
}

.dashboard__user-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  background: rgba(15, 23, 42, 0.95);
  border: 0.08vw solid rgba(255, 255, 255, 0.1);
  border-radius: 0.5vw;
  min-width: 12vw;
  margin-top: 0.8vw;
  backdrop-filter: blur(0.7vw);
  z-index: 1000;
  overflow: hidden;
}

.dashboard__dropdown-item {
  display: block;
  width: 100%;
  padding: 0.8vw 1.2vw;
  background: none;
  border: none;
  color: rgba(226, 232, 240, 0.8);
  font-size: 0.95vw;
  font-weight: 500;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: 'Nunito', system-ui, sans-serif;
}

.dashboard__dropdown-item:hover {
  background: rgba(59, 130, 246, 0.2);
  color: rgba(226, 232, 240, 1);
}

.dashboard__logout-btn {
  background: rgba(239, 68, 68, 0.15);
  border: 0.08vw solid rgba(239, 68, 68, 0.3);
  color: #fca5a5;
  padding: 0.6vw 1.5vw;
  border-radius: 0.5vw;
  font-weight: 600;
  font-size: 0.95vw;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: 'Nunito', system-ui, sans-serif;
}

.dashboard__logout-btn:hover {
  background: rgba(239, 68, 68, 0.25);
  border-color: rgba(239, 68, 68, 0.5);
}

.dashboard__main {
  padding: 6vh 0 2vh 0;
}

.dashboard__welcome {
  margin-bottom: 1vh;
  margin-top: 3vh;
}

.dashboard__welcome-title {
  font-size: 2.5vw;
  font-weight: 800;
  margin-bottom: 6vh;
  color: #bfdbfe;
}

.highlight {
  color: #93c5fd;
  font-weight: 700;
}

.dashboard__info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(18vw, 1fr));
  gap: 1.5vw;
  margin-bottom: 3vh;
}

.dashboard__info-card {
  display: flex;
  gap: 1.5vw;
  padding: 1.8vw;
  background: rgba(15, 23, 42, 0.6);
  border: 0.08vw solid rgba(148, 163, 184, 0.15);
  border-radius: 1vw;
  transition: all 0.3s ease;
}

.dashboard__info-card:hover {
  background: rgba(15, 23, 42, 0.8);
  border-color: rgba(59, 130, 246, 0.3);
}

.dashboard__user-info-card {
  padding: 2.5vw;
  background: rgba(15, 23, 42, 0.6);
  border: 0.08vw solid rgba(148, 163, 184, 0.15);
  border-radius: 1.2vw;
  margin-bottom: 3vh;
  transition: all 0.3s ease;
}

.dashboard__user-info-card:hover {
  background: rgba(15, 23, 42, 0.8);
  border-color: rgba(59, 130, 246, 0.3);
}

.dashboard__user-info-header {
  margin-bottom: 2vw;
  padding-bottom: 1.5vw;
  border-bottom: 0.08vw solid rgba(148, 163, 184, 0.2);
}

.dashboard__user-info-title {
  font-size: 1.3vw;
  font-weight: 700;
  color: #bfdbfe;
  margin: 0;
}

.dashboard__user-info-content {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.2vw;
}

.dashboard__user-info-row {
  display: flex;
  align-items: center;
  gap: 1.2vw;
  padding: 1vw;
  background: rgba(59, 130, 246, 0.08);
  border-radius: 0.8vw;
  transition: all 0.2s ease;
}

.dashboard__user-info-row:hover {
  background: rgba(59, 130, 246, 0.15);
}

.dashboard__user-info-icon {
  font-size: 1.4vw;
  flex-shrink: 0;
}

.dashboard__user-info-label {
  font-weight: 600;
  color: rgba(226, 232, 240, 0.7);
  font-size: 1vw;
  min-width: 8vw;
}

.dashboard__user-info-value {
  color: #ffffff;
  font-weight: 500;
  font-size: 1vw;
}

.dashboard__card-icon {
  font-size: 2.5vw;
}

.dashboard__card-content {
  flex: 1;
}

.dashboard__card-label {
  font-size: 0.8vw;
  color: rgba(226, 232, 240, 0.6);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.4vh;
}

.dashboard__card-value {
  font-size: 1.1vw;
  font-weight: 600;
  color: #bfdbfe;
}

.dashboard__grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(25vw, 1fr));
  gap: 2vw;
  margin-bottom: 3vh;
}

.dashboard__grid .actions-card:only-child {
  max-width: 26.4vw;
}

.dashboard__card {
  background: rgba(15, 23, 42, 0.5);
  border: 0.08vw solid rgba(148, 163, 184, 0.15);
  border-radius: 1.2vw;
  overflow: hidden;
  transition: all 0.3s ease;
}

.dashboard__card:hover {
  background: rgba(15, 23, 42, 0.7);
  border-color: rgba(59, 130, 246, 0.3);
}

.dashboard__card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5vw;
  border-bottom: 0.08vw solid rgba(148, 163, 184, 0.1);
}

.dashboard__card-title {
  font-size: 1.3vw;
  font-weight: 700;
  color: #bfdbfe;
}

.dashboard__card-badge {
  background: rgba(59, 130, 246, 0.2);
  color: #93c5fd;
  padding: 0.4vw 0.8vw;
  border-radius: 0.4vw;
  font-size: 0.7vw;
  font-weight: 600;
  text-transform: uppercase;
}

.dashboard__card-link {
  background: none;
  border: none;
  color: #93c5fd;
  font-weight: 600;
  font-size: 0.95vw;
  cursor: pointer;
  transition: color 0.2s ease;
  font-family: 'Nunito', system-ui, sans-serif;
}

.dashboard__card-link:hover {
  color: #bfdbfe;
}

.dashboard__card-body {
  padding: 1.5vw;
}

.budget-stat {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.2vw 0;
  border-bottom: 0.08vw solid rgba(148, 163, 184, 0.1);
}

.budget-stat:last-of-type {
  border-bottom: none;
}

.budget-stat__label {
  color: rgba(226, 232, 240, 0.7);
  font-size: 1vw;
}

.budget-stat__value {
  font-size: 1.6vw;
  font-weight: 700;
  color: #bfdbfe;
}

.budget-stat__value.warning {
  color: #fbbf24;
}

.budget-stat__value.success {
  color: #86efac;
}

.budget-progress {
  margin-top: 1.5vw;
}

.budget-progress__bar {
  width: 100%;
  height: 0.6vh;
  background: rgba(148, 163, 184, 0.2);
  border-radius: 9999vw;
  overflow: hidden;
  margin-bottom: 0.5vh;
}

.budget-progress__fill {
  height: 100%;
  background: linear-gradient(90deg, #fbbf24, #f59e0b);
  border-radius: 9999vw;
  transition: width 0.3s ease;
}

.budget-progress__text {
  font-size: 0.9vw;
  color: rgba(226, 232, 240, 0.6);
}

.transaction-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.2vw 0;
  border-bottom: 0.08vw solid rgba(148, 163, 184, 0.1);
}

.transaction-item:last-of-type {
  border-bottom: none;
}

.transaction-item__info {
  flex: 1;
}

.transaction-item__title {
  font-weight: 600;
  font-size: 1vw;
  color: #bfdbfe;
  margin-bottom: 0.3vh;
}

.transaction-item__date {
  font-size: 0.85vw;
  color: rgba(226, 232, 240, 0.6);
}

.transaction-item__amount {
  font-weight: 700;
  color: #fca5a5;
  font-size: 1.1vw;
}

.transaction-item__amount.success-text {
  color: #86efac;
}

.dashboard__btn-secondary {
  width: 100%;
  margin-top: 1.2vw;
  padding: 1vw;
  background: rgba(59, 130, 246, 0.15);
  border: 0.08vw solid rgba(59, 130, 246, 0.3);
  color: #93c5fd;
  border-radius: 0.8vw;
  font-weight: 600;
  font-size: 0.95vw;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: 'Nunito', system-ui, sans-serif;
}

.dashboard__btn-secondary:hover {
  background: rgba(59, 130, 246, 0.25);
  border-color: rgba(59, 130, 246, 0.5);
}

.dashboard__quick-action {
  display: flex;
  align-items: center;
  gap: 1vw;
  width: 100%;
  padding: 1.3vw;
  background: rgba(59, 130, 246, 0.1);
  border: 0.08vw solid rgba(59, 130, 246, 0.2);
  color: #bfdbfe;
  border-radius: 0.8vw;
  font-weight: 600;
  font-size: 1vw;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: 'Nunito', system-ui, sans-serif;
  margin-bottom: 0.9vw;
}

.dashboard__quick-action:last-child {
  margin-bottom: 0;
}

.dashboard__quick-action:hover {
  background: rgba(59, 130, 246, 0.2);
  border-color: rgba(59, 130, 246, 0.4);
}

.dashboard__quick-action-icon {
  font-size: 1.4vw;
}

.dashboard__quick-action-text {
  font-size: 1vw;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.2vw 0;
  border-bottom: 0.08vw solid rgba(148, 163, 184, 0.1);
}

.stat-row:last-child {
  border-bottom: none;
}

.stat-row__label {
  color: rgba(226, 232, 240, 0.7);
  font-size: 1vw;
}

.stat-row__value {
  font-size: 1.4vw;
  font-weight: 700;
  color: #bfdbfe;
}

@media (max-width: 1024px) {
  .dashboard__header-content {
    grid-template-columns: 1fr;
    gap: 1.5vw;
  }

  .dashboard__nav {
    order: 3;
    grid-column: 1 / -1;
    justify-content: flex-start;
    overflow-x: auto;
  }

  .dashboard__user-section {
    justify-self: auto;
  }

  .dashboard__grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .dashboard__container {
    padding: 0 1.5vw;
  }

  .dashboard__header {
    padding: 0.6vh 0;
  }

  .dashboard__header-content {
    gap: 1vw;
  }

  .dashboard__title {
    font-size: 1.8vw;
  }

  .dashboard__nav {
    overflow-x: auto;
    gap: 0.3vw;
  }

  .dashboard__nav-link {
    font-size: 0.8vw;
    padding: 0.4vw 0.8vw;
    white-space: nowrap;
  }

  .dashboard__welcome-title {
    font-size: 2vw;
  }

  .dashboard__info-grid {
    grid-template-columns: 1fr;
    gap: 1vw;
    margin-bottom: 2vh;
  }

  .dashboard__card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1vw;
  }

  .dashboard__user-name {
    display: none;
  }
}

.dashboard__sections-container {
  display: flex;
  overflow-x: auto;
  scroll-behavior: smooth;
  gap: 0;
  width: 100%;
  scrollbar-width: none;
  -ms-overflow-style: none;
  margin: 0;
  padding: 0;
}

.dashboard__sections-container::-webkit-scrollbar {
  display: none;
}

.dashboard__section {
  flex: 0 0 100%;
  width: 100%;
  max-width: 100%;
  min-width: 100%;
  padding: 0;
  overflow-y: auto;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: #1e293b;
  border: 0.1vw solid rgba(59, 130, 246, 0.2);
  border-radius: 1.2vw;
  padding: 2.5vw;
  max-width: 45vw;
  width: 90%;
  max-height: 85vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.modal-content::-webkit-scrollbar {
  display: none;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2vw;
  padding-bottom: 1.5vw;
  border-bottom: 0.1vw solid rgba(59, 130, 246, 0.2);
}

.modal-title {
  font-size: 1.6vw;
  font-weight: 700;
  color: #e2e8f0;
}

.modal-close {
  background: none;
  border: none;
  color: rgba(226, 232, 240, 0.7);
  font-size: 1.6vw;
  cursor: pointer;
  padding: 0;
  width: 2vw;
  height: 2vw;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s ease;
}

.modal-close:hover {
  color: #e2e8f0;
}

.edit-form-group {
  margin-bottom: 1.5vw;
}

.edit-form-label {
  display: block;
  margin-bottom: 0.6vw;
  color: #bfdbfe;
  font-size: 0.95vw;
  font-weight: 600;
}

.edit-form-input {
  width: 100%;
  padding: 0.8vw;
  background: rgba(30, 41, 59, 0.8);
  border: 0.08vw solid rgba(59, 130, 246, 0.3);
  border-radius: 0.6vw;
  color: #e2e8f0;
  font-size: 0.95vw;
  font-family: 'Nunito', system-ui, sans-serif;
  transition: all 0.2s ease;
}

.edit-form-input:focus {
  outline: none;
  border-color: rgba(59, 130, 246, 0.6);
  background: rgba(30, 41, 59, 0.95);
}

.edit-form-select {
  width: 100%;
  padding: 0.8vw;
  background: rgba(30, 41, 59, 0.8);
  border: 0.08vw solid rgba(59, 130, 246, 0.3);
  border-radius: 0.6vw;
  color: #e2e8f0;
  font-size: 0.95vw;
  font-family: 'Nunito', system-ui, sans-serif;
  transition: all 0.2s ease;
}

.edit-form-select:focus {
  outline: none;
  border-color: rgba(59, 130, 246, 0.6);
  background: rgba(30, 41, 59, 0.95);
}

.edit-form-checkbox {
  display: flex;
  align-items: center;
  gap: 0.8vw;
}

.edit-form-checkbox input {
  width: 1.2vw;
  height: 1.2vw;
  cursor: pointer;
  accent-color: #3b82f6;
}

.edit-form-checkbox label {
  margin: 0;
  cursor: pointer;
  color: #bfdbfe;
}

.edit-form__role-toggle {
  display: flex;
  flex-direction: column;
  gap: 0.6vw;
  margin-bottom: 1.5vw;
}

.edit-form__role-label {
  font-weight: 700;
  font-size: 0.95vw;
  color: #e2e8f0;
  font-family: 'Nunito', system-ui, sans-serif;
}

.edit-form__toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 0.9vw 1.2vw;
  border: 1px solid rgba(148, 163, 184, 0.22);
  border-radius: 0.9vw;
  background: rgba(15, 23, 42, 0.68);
  color: #ffffff;
  font-family: 'Nunito', system-ui, sans-serif;
  font-size: 0.95vw;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.edit-form__toggle:hover {
  border-color: rgba(96, 165, 250, 0.5);
  background: rgba(15, 23, 42, 0.85);
}

.edit-form__toggle.is-treasurer {
  border-color: rgba(96, 165, 250, 0.9);
  background: rgba(59, 130, 246, 0.15);
}

.edit-form__toggle.is-in-sap {
  border-color: rgba(34, 197, 94, 0.9);
  background: rgba(34, 197, 94, 0.15);
}

.edit-form__toggle.is-in-sap .edit-form__toggle-indicator {
  background: linear-gradient(135deg, #22c55e, #16a34a);
}

.edit-form__toggle-text {
  flex: 1;
  text-align: left;
}

.edit-form__toggle-indicator {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.5vw;
  height: 1.5vw;
  margin-left: 0.8vw;
  border-radius: 0.4vw;
  background: rgba(96, 165, 250, 0.3);
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.edit-form__toggle.is-treasurer .edit-form__toggle-indicator {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
}

.edit-form__toggle-indicator::after {
  content: '↔';
  color: #ffffff;
  font-size: 0.95vw;
  font-weight: bold;
}

.edit-form__toggle:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.edit-form__role-info {
  display: block;
  margin-top: 0.5vw;
  font-size: 0.85vw;
  color: #fbbf24;
  font-style: italic;
}

.modal-actions {
  display: flex;
  gap: 1vw;
  justify-content: flex-end;
  margin-top: 2.5vw;
  padding-top: 1.5vw;
  border-top: 0.1vw solid rgba(59, 130, 246, 0.2);
}

.modal-btn {
  padding: 0.8vw 1.6vw;
  border: 0.1vw solid rgba(59, 130, 246, 0.3);
  border-radius: 0.6vw;
  font-size: 0.95vw;
  font-weight: 600;
  cursor: pointer;
  font-family: 'Nunito', system-ui, sans-serif;
  transition: all 0.2s ease;
}

.modal-btn-cancel {
  background: rgba(59, 130, 246, 0.1);
  color: #bfdbfe;
}

.modal-btn-cancel:hover {
  background: rgba(59, 130, 246, 0.2);
  border-color: rgba(59, 130, 246, 0.5);
}

.modal-btn-save {
  background: #3b82f6;
  color: #fff;
  border-color: #3b82f6;
}

.modal-btn-save:hover {
  background: #60a5fa;
  border-color: #60a5fa;
}

@media (max-width: 1024px) {
  .modal-content {
    max-width: 55vw;
  }
}

@media (max-width: 640px) {
  .modal-content {
    max-width: 90vw;
    padding: 1.5vw;
  }

  .modal-title {
    font-size: 1.4vw;
  }

  .edit-form-group {
    margin-bottom: 1.2vw;
  }

  .edit-form-label {
    font-size: 0.9vw;
  }

  .edit-form-input,
  .edit-form-select {
    font-size: 0.9vw;
    padding: 0.7vw;
  }

  .modal-actions {
    flex-direction: column;
  }

  .modal-btn {
    width: 100%;
  }
}
</style>
