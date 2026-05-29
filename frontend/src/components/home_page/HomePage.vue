<template>
  <div class="dashboard">
    <!-- Header -->
    <header class="dashboard__header">
      <div class="dashboard__container">
        <div class="dashboard__header-content">
          <div class="dashboard__logo-section">
            <img src="/logo.png" alt="Logo" class="dashboard__logo" />
            <h1 class="dashboard__title">BudgetFlowFusion</h1>
          </div>
          <nav class="dashboard__nav">
            <button class="dashboard__nav-link active">Pulpit</button>
            <button class="dashboard__nav-link">Budżet</button>
            <button class="dashboard__nav-link">Wydatki</button>
            <button class="dashboard__nav-link">Raporty</button>
            <button class="dashboard__nav-link">Ustawienia</button>
          </nav>
          <div class="dashboard__user-section">
            <span class="dashboard__user-name">{{ user.firstName }} {{ user.lastName }}</span>
            <button class="dashboard__logout-btn" @click="handleLogout">Wyloguj się</button>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="dashboard__main">
      <div class="dashboard__container">
        <!-- Welcome Section -->
        <section class="dashboard__welcome">
          <h2 class="dashboard__welcome-title">
            Cześć {{ user.firstName }}!
          </h2>
        </section>

        <!-- User Info Cards -->
        <section class="dashboard__info-grid">
          <div class="dashboard__info-card">
            <div class="dashboard__card-icon">{{user.role === 'member' ? '🧩' : '💰'}}</div>
            <div class="dashboard__card-content">
              <p class="dashboard__card-label">Rola</p>
              <p class="dashboard__card-value">
                {{ user.role === 'member' ? 'Członek koła naukowego' : 'Skarbnik' }}
              </p>
            </div>
          </div>

          <div class="dashboard__info-card">
            <div class="dashboard__card-icon">📬</div>
            <div class="dashboard__card-content">
              <p class="dashboard__card-label">E-mail</p>
              <p class="dashboard__card-value">{{ user.email }}</p>
            </div>
          </div>

          <div class="dashboard__info-card">
            <div class="dashboard__card-icon">🏛️</div>
            <div class="dashboard__card-content">
              <p class="dashboard__card-label">Koło naukowe</p>
              <p class="dashboard__card-value">{{ user.circleName }}</p>
            </div>
          </div>
        </section>

        <!-- Main Dashboard Grid -->
        <section class="dashboard__grid">
          <!-- Budget Overview Card (Tylko dla skarbnika) -->
          <div v-if="user.role === 'treasurer'" class="dashboard__card budget-card">
            <div class="dashboard__card-header">
              <h3 class="dashboard__card-title">💰 Przegląd budżetu</h3>
              <span class="dashboard__card-badge">Miesiąc</span>
            </div>
            <div class="dashboard__card-body">
              <div class="budget-stat">
                <p class="budget-stat__label">Budżet dostępny</p>
                <p class="budget-stat__value">5 000,00 PLN</p>
              </div>
              <div class="budget-stat">
                <p class="budget-stat__label">Wydane</p>
                <p class="budget-stat__value warning">1 234,56 PLN</p>
              </div>
              <div class="budget-stat">
                <p class="budget-stat__label">Pozostało</p>
                <p class="budget-stat__value success">3 765,44 PLN</p>
              </div>
              <div class="budget-progress">
                <div class="budget-progress__bar">
                  <div class="budget-progress__fill" style="width: 24.7%"></div>
                </div>
                <p class="budget-progress__text">24.7% wydane</p>
              </div>
            </div>
          </div>

          <!-- Recent Transactions Card (Tylko dla skarbnika) -->
          <div v-if="user.role === 'treasurer'" class="dashboard__card transactions-card">
            <div class="dashboard__card-header">
              <h3 class="dashboard__card-title">📋 Ostatnie transakcje</h3>
              <button class="dashboard__card-link">Wszystkie →</button>
            </div>
            <div class="dashboard__card-body">
              <div class="transaction-item">
                <div class="transaction-item__info">
                  <p class="transaction-item__title">Zakup materiałów promocyjnych</p>
                  <p class="transaction-item__date">Dzisiaj</p>
                </div>
                <p class="transaction-item__amount">-450,00 PLN</p>
              </div>
              <div class="transaction-item">
                <div class="transaction-item__info">
                  <p class="transaction-item__title">Wpłata członkowska</p>
                  <p class="transaction-item__date">Wczoraj</p>
                </div>
                <p class="transaction-item__amount success-text">+200,00 PLN</p>
              </div>
              <div class="transaction-item">
                <div class="transaction-item__info">
                  <p class="transaction-item__title">Koszty wynajęcia sali</p>
                  <p class="transaction-item__date">3 dni temu</p>
                </div>
                <p class="transaction-item__amount">-784,56 PLN</p>
              </div>
              <button class="dashboard__btn-secondary">+ Nowa transakcja</button>
            </div>
          </div>

          <!-- Quick Actions Card -->
          <div class="dashboard__card actions-card">
            <div class="dashboard__card-header">
              <h3 class="dashboard__card-title">⚡ Szybkie akcje</h3>
            </div>
            <div class="dashboard__card-body">
              <button class="dashboard__quick-action">
                <span class="dashboard__quick-action-icon">➕</span>
                <span class="dashboard__quick-action-text">Dodaj wydatek</span>
              </button>
              <button class="dashboard__quick-action">
                <span class="dashboard__quick-action-icon">💵</span>
                <span class="dashboard__quick-action-text">Dodaj wpłatę</span>
              </button>
              <button class="dashboard__quick-action">
                <span class="dashboard__quick-action-icon">📊</span>
                <span class="dashboard__quick-action-text">Pokaż raport</span>
              </button>
              <button class="dashboard__quick-action">
                <span class="dashboard__quick-action-icon">👥</span>
                <span class="dashboard__quick-action-text">Członkowie koła</span>
              </button>
            </div>
          </div>

          <!-- Statistics Card (Tylko dla skarbnika) -->
          <div v-if="user.role === 'treasurer'" class="dashboard__card stats-card">
            <div class="dashboard__card-header">
              <h3 class="dashboard__card-title">📈 Statystyki</h3>
            </div>
            <div class="dashboard__card-body">
              <div class="stat-row">
                <p class="stat-row__label">Transakcje ten miesiąc</p>
                <p class="stat-row__value">12</p>
              </div>
              <div class="stat-row">
                <p class="stat-row__label">Średnia transakcji</p>
                <p class="stat-row__value">102,88 PLN</p>
              </div>
              <div class="stat-row">
                <p class="stat-row__label">Największy wydatek</p>
                <p class="stat-row__value">784,56 PLN</p>
              </div>
              <div class="stat-row">
                <p class="stat-row__label">Liczba członków</p>
                <p class="stat-row__value">8</p>
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>
  </div>
</template>

<script setup>
import { useAuth } from '@/composables/useAuth'
import { useRouter } from 'vue-router'

const router = useRouter()
const { user, logout } = useAuth()

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
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

/* Header */
.dashboard__header {
  background: rgba(9, 14, 32, 0.5);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(10px);
  position: sticky;
  top: 0;
  z-index: 100;
  padding: 1rem 0;
}

.dashboard__header-content {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 3rem;
}

.dashboard__logo-section {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.dashboard__logo {
  width: 50px;
  height: 50px;
  border-radius: 0.5rem;
  object-fit: contain;
}

.dashboard__title {
  font-size: 1.5rem;
  font-weight: 800;
  background: linear-gradient(135deg, #3b82f6, #60a5fa);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.dashboard__nav {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
}

.dashboard__nav-link {
  background: none;
  border: none;
  color: rgba(226, 232, 240, 0.6);
  font-size: 0.95rem;
  font-weight: 600;
  padding: 0.5rem 1rem;
  cursor: pointer;
  border-radius: 0.5rem;
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
  gap: 1.5rem;
  justify-self: end;
}

.dashboard__user-name {
  font-weight: 600;
  color: rgba(226, 232, 240, 0.8);
}

.dashboard__logout-btn {
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #fca5a5;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: 'Nunito', system-ui, sans-serif;
}

.dashboard__logout-btn:hover {
  background: rgba(239, 68, 68, 0.25);
  border-color: rgba(239, 68, 68, 0.5);
}

/* Main Content */
.dashboard__main {
  padding: 2rem 0;
}

.dashboard__welcome {
  margin-bottom: 3rem;
}

.dashboard__welcome-title {
  font-size: 2rem;
  font-weight: 800;
  margin-bottom: 0.5rem;
  color: #bfdbfe;
}

.dashboard__welcome-subtitle {
  font-size: 1.1rem;
  color: rgba(226, 232, 240, 0.7);
}

.highlight {
  color: #93c5fd;
  font-weight: 700;
}

/* Info Grid */
.dashboard__info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.dashboard__info-card {
  display: flex;
  gap: 1.5rem;
  padding: 1.5rem;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.15);
  border-radius: 1rem;
  transition: all 0.3s ease;
}

.dashboard__info-card:hover {
  background: rgba(15, 23, 42, 0.8);
  border-color: rgba(59, 130, 246, 0.3);
}

.dashboard__card-icon {
  font-size: 2rem;
}

.dashboard__card-content {
  flex: 1;
}

.dashboard__card-label {
  font-size: 0.85rem;
  color: rgba(226, 232, 240, 0.6);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.25rem;
}

.dashboard__card-value {
  font-size: 1.1rem;
  font-weight: 600;
  color: #bfdbfe;
}

/* Main Grid */
.dashboard__grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;
}

.dashboard__grid .actions-card:only-child {
  max-width: 27rem;
}

.dashboard__card {
  background: rgba(15, 23, 42, 0.5);
  border: 1px solid rgba(148, 163, 184, 0.15);
  border-radius: 1.25rem;
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
  padding: 1.5rem;
  border-bottom: 1px solid rgba(148, 163, 184, 0.1);
}

.dashboard__card-title {
  font-size: 1.2rem;
  font-weight: 700;
  color: #bfdbfe;
}

.dashboard__card-badge {
  background: rgba(59, 130, 246, 0.2);
  color: #93c5fd;
  padding: 0.35rem 0.75rem;
  border-radius: 0.4rem;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.dashboard__card-link {
  background: none;
  border: none;
  color: #93c5fd;
  font-weight: 600;
  cursor: pointer;
  transition: color 0.2s ease;
  font-family: 'Nunito', system-ui, sans-serif;
}

.dashboard__card-link:hover {
  color: #bfdbfe;
}

.dashboard__card-body {
  padding: 1.5rem;
}

/* Budget Card */
.budget-stat {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0;
  border-bottom: 1px solid rgba(148, 163, 184, 0.1);
}

.budget-stat:last-of-type {
  border-bottom: none;
}

.budget-stat__label {
  color: rgba(226, 232, 240, 0.7);
  font-size: 0.95rem;
}

.budget-stat__value {
  font-size: 1.5rem;
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
  margin-top: 1.5rem;
}

.budget-progress__bar {
  width: 100%;
  height: 8px;
  background: rgba(148, 163, 184, 0.2);
  border-radius: 9999px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.budget-progress__fill {
  height: 100%;
  background: linear-gradient(90deg, #fbbf24, #f59e0b);
  border-radius: 9999px;
  transition: width 0.3s ease;
}

.budget-progress__text {
  font-size: 0.85rem;
  color: rgba(226, 232, 240, 0.6);
}

/* Transactions Card */
.transaction-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0;
  border-bottom: 1px solid rgba(148, 163, 184, 0.1);
}

.transaction-item:last-of-type {
  border-bottom: none;
}

.transaction-item__info {
  flex: 1;
}

.transaction-item__title {
  font-weight: 600;
  color: #bfdbfe;
  margin-bottom: 0.25rem;
}

.transaction-item__date {
  font-size: 0.85rem;
  color: rgba(226, 232, 240, 0.6);
}

.transaction-item__amount {
  font-weight: 700;
  color: #fca5a5;
  font-size: 1.1rem;
}

.transaction-item__amount.success-text {
  color: #86efac;
}

/* Buttons */
.dashboard__btn-secondary {
  width: 100%;
  margin-top: 1rem;
  padding: 0.75rem;
  background: rgba(59, 130, 246, 0.15);
  border: 1px solid rgba(59, 130, 246, 0.3);
  color: #93c5fd;
  border-radius: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: 'Nunito', system-ui, sans-serif;
}

.dashboard__btn-secondary:hover {
  background: rgba(59, 130, 246, 0.25);
  border-color: rgba(59, 130, 246, 0.5);
}

/* Quick Actions */
.dashboard__quick-action {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  padding: 1rem;
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.2);
  color: #bfdbfe;
  border-radius: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: 'Nunito', system-ui, sans-serif;
  margin-bottom: 0.75rem;
}

.dashboard__quick-action:last-child {
  margin-bottom: 0;
}

.dashboard__quick-action:hover {
  background: rgba(59, 130, 246, 0.2);
  border-color: rgba(59, 130, 246, 0.4);
}

.dashboard__quick-action-icon {
  font-size: 1.2rem;
}

.dashboard__quick-action-text {
  font-size: 0.95rem;
}

/* Stats Card */
.stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0;
  border-bottom: 1px solid rgba(148, 163, 184, 0.1);
}

.stat-row:last-child {
  border-bottom: none;
}

.stat-row__label {
  color: rgba(226, 232, 240, 0.7);
}

.stat-row__value {
  font-size: 1.3rem;
  font-weight: 700;
  color: #bfdbfe;
}

/* Responsive */
@media (max-width: 1024px) {
  .dashboard__header-content {
    grid-template-columns: 1fr;
    gap: 1rem;
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
    padding: 0 1rem;
  }

  .dashboard__header {
    padding: 0.75rem 0;
  }

  .dashboard__header-content {
    gap: 1rem;
  }

  .dashboard__title {
    font-size: 1.2rem;
  }

  .dashboard__nav {
    overflow-x: auto;
    gap: 0.25rem;
  }

  .dashboard__nav-link {
    font-size: 0.85rem;
    padding: 0.4rem 0.8rem;
    white-space: nowrap;
  }

  .dashboard__welcome-title {
    font-size: 1.5rem;
  }

  .dashboard__welcome-subtitle {
    font-size: 0.95rem;
  }

  .dashboard__info-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
    margin-bottom: 2rem;
  }

  .dashboard__card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .dashboard__user-name {
    display: none;
  }
}
</style>
