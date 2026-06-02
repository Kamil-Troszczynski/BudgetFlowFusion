```vue
<template>
  <div v-if="!activeSettlement" class="settlements-section">

    <div class="settlements-header">

      <div class="settlements-title-section">
        <h2 class="settlements-title">
          Rozliczenia zakupów
        </h2>

        <p class="settlements-subtitle">
          Opłacone wnioski wymagające rozliczenia
        </p>
      </div>

      <button
        class="settlements-add-button"
      >
        + Dodaj rozliczenie
      </button>

    </div>

    <div
      v-if="settlements.length === 0"
      class="settlements-empty"
    >
      <p class="settlements-empty-icon">🧾</p>

      <p class="settlements-empty-text">
        Nie masz jeszcze żadnych rozliczeń
      </p>

      <p class="settlements-empty-subtext">
        Dodaj pierwsze rozliczenie opłaconego wniosku
      </p>
    </div>

    <div
      v-else
      class="settlements-grid"
    >

      <div
        v-for="settlement in settlements"
        :key="settlement.id"
        class="settlement-card"
      >

        <div class="settlement-card__header">

          <div>
            <h3 class="settlement-card__title">
              {{ settlement.requestName }}
            </h3>

            <p class="settlement-card__category">
              {{ settlement.category }}
            </p>
          </div>

          <span
            class="settlement-card__badge"
            :class="settlement.status"
          >
            {{ formatStatus(settlement.status) }}
          </span>

        </div>

        <div class="settlement-card__content">

          <p class="settlement-card__detail">
            <span class="settlement-card__label">
              Budżet:
            </span>

            <span class="settlement-card__value">
              {{ settlement.budget }} PLN
            </span>
          </p>

          <p class="settlement-card__detail">
            <span class="settlement-card__label">
              Wydano:
            </span>

            <span class="settlement-card__value">
              {{ settlement.spent }} PLN
            </span>
          </p>

          <p class="settlement-card__detail">
            <span class="settlement-card__label">
              Faktury:
            </span>

            <span class="settlement-card__value">
              {{ settlement.invoiceCount }}
            </span>
          </p>

          <p class="settlement-card__detail">
            <span class="settlement-card__label">
              Data płatności:
            </span>

            <span class="settlement-card__value">
              {{ formatDate(settlement.paidAt) }}
            </span>
          </p>

        </div>

        <div class="settlement-card__progress">

          <div class="settlement-card__progress-bar">

            <div
              class="settlement-card__progress-fill"
              :style="{ width: settlement.progress + '%' }"
            ></div>

          </div>

          <p class="settlement-card__progress-text">
            Rozliczono {{ settlement.progress }}%
          </p>

        </div>

        <div class="settlement-card__actions">

          <button
            class="settlement-card__button view"
            @click="activeSettlement = settlement"
          >
            Szczegóły
          </button>

          <button
            class="settlement-card__button upload"
          >
            Dodaj fakturę
          </button>

        </div>

      </div>

    </div>

  </div>

  <!-- SZCZEGÓŁY -->

  <div
    v-else
    class="settlement-details"
  >

    <button
      class="settlement-details__back"
      @click="activeSettlement = null"
    >
      ← Powrót
    </button>

    <div class="settlement-details__card">

      <div class="settlement-details__top">

        <div>
          <h2 class="settlement-details__title">
            {{ activeSettlement.requestName }}
          </h2>

          <p class="settlement-details__subtitle">
            Rozliczenie opłaconego wniosku
          </p>
        </div>

        <span
          class="settlement-card__badge"
          :class="activeSettlement.status"
        >
          {{ formatStatus(activeSettlement.status) }}
        </span>

      </div>

      <div class="settlement-details__grid">

        <div class="settlement-info">
          <p>Budżet</p>
          <strong>{{ activeSettlement.budget }} PLN</strong>
        </div>

        <div class="settlement-info">
          <p>Wydano</p>
          <strong>{{ activeSettlement.spent }} PLN</strong>
        </div>

        <div class="settlement-info">
          <p>Faktury</p>
          <strong>{{ activeSettlement.invoiceCount }}</strong>
        </div>

        <div class="settlement-info">
          <p>Data płatności</p>
          <strong>{{ formatDate(activeSettlement.paidAt) }}</strong>
        </div>

      </div>

      <div class="settlement-details__invoices">

        <h3>Załączone faktury</h3>

        <div
          v-for="invoice in activeSettlement.invoices"
          :key="invoice.id"
          class="invoice-card"
        >

          <div>
            <p class="invoice-title">
              {{ invoice.name }}
            </p>

            <p class="invoice-date">
              {{ invoice.date }}
            </p>
          </div>

          <div class="invoice-price">
            {{ invoice.amount }} PLN
          </div>

        </div>

      </div>

    </div>

  </div>
</template>

<script setup>
import { ref } from 'vue'

const activeSettlement = ref(null)

const settlements = ref([
  {
    id: 1,
    requestName: 'Zakup elektroniki',
    category: 'Sprzęt IT',
    budget: 3000,
    spent: 2400,
    invoiceCount: 3,
    paidAt: '2026-06-01',
    progress: 100,
    status: 'completed',

    invoices: [
      {
        id: 1,
        name: 'Faktura Media Expert',
        amount: 1200,
        date: '01.06.2026'
      },
      {
        id: 2,
        name: 'Faktura x-kom',
        amount: 800,
        date: '02.06.2026'
      },
      {
        id: 3,
        name: 'Faktura Allegro',
        amount: 400,
        date: '03.06.2026'
      }
    ]
  },

  {
    id: 2,
    requestName: 'Materiały promocyjne',
    category: 'Marketing',
    budget: 1500,
    spent: 850,
    invoiceCount: 1,
    paidAt: '2026-05-28',
    progress: 50,
    status: 'partial',

    invoices: [
      {
        id: 1,
        name: 'Druk ulotek',
        amount: 850,
        date: '28.05.2026'
      }
    ]
  }
])

const formatStatus = (status) => {
  const map = {
    pending: 'Oczekuje',
    partial: 'Częściowo',
    completed: 'Rozliczony',
    rejected: 'Odrzucony'
  }

  return map[status] || status
}

const formatDate = (dateStr) => {
  if (!dateStr) return '—'

  return new Date(dateStr).toLocaleDateString('pl-PL')
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;500;600;700;800&display=swap');

.settlements-section {
  width: 100%;
  padding: 3vh 0;
  font-family: 'Nunito', sans-serif;
}

.settlements-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 3vh;
}

.settlements-title {
  font-size: 2vw;
  color: #bfdbfe;
  margin: 0;
  font-weight: 800;
}

.settlements-subtitle {
  color: rgba(226,232,240,0.6);
  margin-top: 0.5vh;
}

.settlements-add-button {
  padding: 0.8vw 1.4vw;
  border: none;
  border-radius: 0.8vw;
  background: linear-gradient(135deg,#3b82f6,#2563eb);
  color: white;
  font-weight: 700;
  cursor: pointer;
}

.settlements-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill,minmax(26vw,1fr));
  gap: 2vw;
}

.settlement-card {
  background: rgba(15,23,42,0.6);
  border: 0.08vw solid rgba(148,163,184,0.15);
  border-radius: 1vw;
  padding: 2vw;
  transition: 0.3s ease;
}

.settlement-card:hover {
  transform: translateY(-0.4vh);
  border-color: rgba(59,130,246,0.4);
}

.settlement-card__header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1.5vw;
}

.settlement-card__title {
  color: white;
  margin: 0;
  font-size: 1.2vw;
}

.settlement-card__category {
  color: rgba(226,232,240,0.5);
  font-size: 0.85vw;
}

.settlement-card__badge {
  padding: 0.4vw 0.8vw;
  border-radius: 0.5vw;
  font-size: 0.8vw;
  font-weight: 700;
}

.completed {
  background: rgba(34,197,94,0.2);
  color: #86efac;
}

.partial {
  background: rgba(251,191,36,0.2);
  color: #fde68a;
}

.pending {
  background: rgba(59,130,246,0.2);
  color: #93c5fd;
}

.settlement-card__content {
  display: flex;
  flex-direction: column;
  gap: 0.7vw;
  margin-bottom: 1.5vw;
}

.settlement-card__detail {
  display: flex;
  justify-content: space-between;
}

.settlement-card__label {
  color: rgba(226,232,240,0.6);
}

.settlement-card__value {
  color: white;
  font-weight: 600;
}

.settlement-card__progress-bar {
  width: 100%;
  height: 0.6vw;
  background: rgba(148,163,184,0.2);
  border-radius: 999px;
  overflow: hidden;
}

.settlement-card__progress-fill {
  height: 100%;
  background: linear-gradient(90deg,#3b82f6,#60a5fa);
}

.settlement-card__progress-text {
  color: rgba(226,232,240,0.6);
  margin-top: 0.6vh;
  font-size: 0.85vw;
}

.settlement-card__actions {
  display: flex;
  gap: 0.8vw;
  margin-top: 1.5vw;
}

.settlement-card__button {
  flex: 1;
  padding: 0.8vw;
  border: none;
  border-radius: 0.6vw;
  cursor: pointer;
  font-weight: 700;
}

.view {
  background: rgba(59,130,246,0.2);
  color: #93c5fd;
}

.upload {
  background: rgba(34,197,94,0.2);
  color: #86efac;
}

.settlement-details__back {
  margin-bottom: 2vh;
  background: none;
  border: none;
  color: #93c5fd;
  cursor: pointer;
  font-size: 1vw;
}

.settlement-details__card {
  background: rgba(15,23,42,0.6);
  border-radius: 1vw;
  padding: 2vw;
}

.settlement-details__top {
  display: flex;
  justify-content: space-between;
  margin-bottom: 2vw;
}

.settlement-details__title {
  color: white;
  margin: 0;
}

.settlement-details__subtitle {
  color: rgba(226,232,240,0.5);
}

.settlement-details__grid {
  display: grid;
  grid-template-columns: repeat(4,1fr);
  gap: 1vw;
  margin-bottom: 2vw;
}

.settlement-info {
  background: rgba(30,41,59,0.6);
  padding: 1vw;
  border-radius: 0.8vw;
}

.settlement-info p {
  color: rgba(226,232,240,0.5);
  margin-bottom: 0.5vh;
}

.settlement-info strong {
  color: white;
}

.invoice-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(30,41,59,0.5);
  padding: 1vw;
  border-radius: 0.8vw;
  margin-top: 1vh;
}

.invoice-title {
  color: white;
  margin: 0;
}

.invoice-date {
  color: rgba(226,232,240,0.5);
  font-size: 0.85vw;
}

.invoice-price {
  color: #86efac;
  font-weight: 700;
}

.settlements-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 6vh;
  border: 0.08vw dashed rgba(148,163,184,0.3);
  border-radius: 1vw;
}

.settlements-empty-icon {
  font-size: 4vw;
}

.settlements-empty-text {
  color: white;
  font-size: 1.2vw;
}

.settlements-empty-subtext {
  color: rgba(226,232,240,0.5);
}
</style>
```
