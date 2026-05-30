<template>
  <div class="validation-section">
    <div class="validation-header">
      <div>
        <h2 class="validation-title">Panel Skarbnika: Akceptacja przedmiotów</h2>
        <p class="validation-subtitle">Weryfikacja nowych przedmiotów dodanych do katalogu przez członków koła</p>
      </div>
      <div class="stats-badges">
        <span class="badge pending">Do weryfikacji: {{ pendingItems.length }}</span>
      </div>
    </div>

    <div v-if="pendingItems.length === 0" class="validation-empty">
      <p class="empty-icon">✅</p>
      <p class="empty-text">Wszystkie przedmioty zostały zweryfikowane!</p>
      <p class="empty-subtext">Dobra robota, katalog jest aktualny.</p>
    </div>

    <div v-else class="table-container">
      <table class="validation-table">
        <thead>
          <tr>
            <th>Nazwa przedmiotu</th>
            <th>Zgłaszający</th>
            <th>Cena bazowa</th>
            <th>Kategoria CPV</th>
            <th>Link</th>
            <th>Akcje</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in pendingItems" :key="item.id">
            <td class="item-name">{{ item.name }}</td>
            <td class="item-student">{{ item.addedBy }}</td>
            <td class="item-price">{{ item.price }} {{ item.currency }}</td>
            <td class="item-cpv">
              <div class="cpv-info">
                <span class="category">{{ item.categoryName }}</span>
                <span class="cpv-code">CPV: {{ item.cpvCode }}</span>
              </div>
            </td>
            <td>
              <a :href="item.link" target="_blank" class="link-btn">Sprawdź sklep ↗</a>
            </td>
            <td class="actions-cell">
              <button class="action-btn accept" @click="handleAccept(item.id)">
                ✓ Akceptuj
              </button>
              <button class="action-btn reject" @click="handleReject(item.id)">
                ✕ Odrzuć
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const pendingItems = ref([
  {
    id: 1,
    name: 'Kontroler Lotu Pixhawk 4',
    addedBy: 'Jan Kowalski',
    price: 850.00,
    currency: 'PLN',
    categoryName: 'Elektronika i Zasilanie',
    cpvCode: '31700000-3',
    link: 'https://botland.com.pl/...'
  },
  {
    id: 2,
    name: 'Włókno węglowe rurka 10mm',
    addedBy: 'Anna Nowak',
    price: 45.50,
    currency: 'PLN',
    categoryName: 'Materiały Konstrukcyjne',
    cpvCode: '44000000-0',
    link: 'https://modele.sklep.pl/...'
  }
])

const handleAccept = (itemId) => {
  pendingItems.value = pendingItems.value.filter(item => item.id !== itemId)
  console.log(`Zatwierdzono przedmiot ID: ${itemId}`)
  alert('Przedmiot został zatwierdzony i dodany do globalnego katalogu!')
}

const handleReject = (itemId) => {
  const reason = prompt("Podaj powód odrzucenia (np. zły kod CPV):")
  if (reason !== null) {
    pendingItems.value = pendingItems.value.filter(item => item.id !== itemId)
    console.log(`Odrzucono przedmiot ID: ${itemId}, powód: ${reason}`)
  }
}
</script>

<style scoped>
.validation-section {
  color: #ffffff;
  padding: 1vw 0;
}

.validation-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2vw;
}

.validation-title {
  font-size: 1.8vw;
  color: #bfdbfe;
  margin: 0 0 0.5vw 0;
}

.validation-subtitle {
  color: rgba(226, 232, 240, 0.6);
  margin: 0;
  font-size: 0.95vw;
}

.badge {
  padding: 0.5vw 1vw;
  border-radius: 2vw;
  font-size: 0.85vw;
  font-weight: 700;
}
.badge.pending { background: rgba(245, 158, 11, 0.15); color: #fef08a; border: 1px solid rgba(245, 158, 11, 0.3); }

.table-container {
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.15);
  border-radius: 1vw;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.validation-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.9vw;
}

.validation-table th, .validation-table td {
  padding: 1.2vw;
  border-bottom: 1px solid rgba(148, 163, 184, 0.1);
}

.validation-table th {
  background: rgba(30, 41, 59, 0.8);
  color: #93c5fd;
  font-weight: 700;
  text-transform: uppercase;
  font-size: 0.75vw;
  letter-spacing: 0.05em;
}

.validation-table tr:hover { background: rgba(30, 41, 59, 0.4); }

.item-name { font-weight: 700; color: #f8fafc; }
.item-student { color: #cbd5e1; }
.item-price { font-family: monospace; font-size: 1vw; }

.cpv-info { display: flex; flex-direction: column; gap: 0.3vw; }
.category { color: #e2e8f0; }
.cpv-code { font-size: 0.8vw; color: #fbbf24; font-family: monospace; }

.link-btn {
  color: #60a5fa;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.2s;
}
.link-btn:hover { color: #93c5fd; text-decoration: underline; }

.actions-cell {
  display: flex;
  gap: 0.5vw;
}

.action-btn {
  padding: 0.6vw 1vw;
  border: none;
  border-radius: 0.4vw;
  font-size: 0.8vw;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn.accept { background: rgba(34, 197, 94, 0.15); color: #86efac; border: 1px solid rgba(34, 197, 94, 0.3); }
.action-btn.accept:hover { background: rgba(34, 197, 94, 0.3); }

.action-btn.reject { background: rgba(239, 68, 68, 0.15); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.3); }
.action-btn.reject:hover { background: rgba(239, 68, 68, 0.3); }

.validation-empty {
  text-align: center;
  padding: 4vw;
  background: rgba(15, 23, 42, 0.4);
  border: 1px dashed rgba(148, 163, 184, 0.2);
  border-radius: 1vw;
}
.empty-icon { font-size: 3vw; margin-bottom: 1vw; }
.empty-text { font-size: 1.2vw; font-weight: 700; color: #e2e8f0; margin-bottom: 0.5vw; }
.empty-subtext { color: #94a3b8; font-size: 0.95vw; }
</style>