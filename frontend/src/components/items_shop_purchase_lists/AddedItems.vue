<template>
  <div class="items-history">
    <div class="items-history__header">
      <div>
        <p class="items-history__eyebrow">Historia zakupów</p>
        <h2>Historia zakupów</h2>
        <p>Pozycje wpisane w koszykach, gotowe do przeszukiwania po projekcie, sklepie, kategorii i CPV.</p>
      </div>
      <button class="history-refresh" type="button" @click="fetchHistory">Odśwież</button>
    </div>

    <div class="history-filters">
      <label class="history-filter history-filter--search">
        <span>Szukaj</span>
        <input
          v-model="filters.search"
          type="text"
          placeholder="Nazwa, sklep, kategoria albo CPV..."
          class="history-input"
        />
      </label>
      <label class="history-filter">
        <span>Projekt</span>
        <select v-model="filters.project" class="history-input">
          <option value="">Wszystkie projekty</option>
          <option v-for="project in projectOptions" :key="project" :value="project">{{ project }}</option>
        </select>
      </label>
      <label class="history-filter">
        <span>Sklep</span>
        <select v-model="filters.shop" class="history-input">
          <option value="">Wszystkie sklepy</option>
          <option v-for="shop in shopOptions" :key="shop" :value="shop">{{ shop }}</option>
        </select>
      </label>
      <label class="history-filter">
        <span>Kategoria</span>
        <select v-model="filters.category" class="history-input">
          <option value="">Wszystkie kategorie</option>
          <option v-for="category in categoryOptions" :key="category" :value="category">{{ category }}</option>
        </select>
      </label>
      <label class="history-filter">
        <span>CPV</span>
        <select v-model="filters.cpv" class="history-input">
          <option value="">Wszystkie CPV</option>
          <option v-for="cpv in cpvOptions" :key="cpv" :value="cpv">{{ cpv }}</option>
        </select>
      </label>
    </div>

    <div class="history-summary">
      <div>
        <span>Pozycji</span>
        <strong>{{ filteredItems.length }}</strong>
      </div>
      <div>
        <span>Łączna wartość</span>
        <strong>{{ formatMoney(historyTotal) }} PLN</strong>
      </div>
      <div>
        <span>Sklepów</span>
        <strong>{{ shopOptions.length }}</strong>
      </div>
      <div>
        <span>Projektów</span>
        <strong>{{ projectOptions.length }}</strong>
      </div>
      <div>
        <span>Kategorii</span>
        <strong>{{ categoryOptions.length }}</strong>
      </div>
    </div>

    <div class="history-table-wrap">
      <table class="history-table">
        <thead>
          <tr>
            <th>Nazwa</th>
            <th>Projekt</th>
            <th>Sklep</th>
            <th>Kategoria</th>
            <th>Podkategoria</th>
            <th>CPV</th>
            <th>Cena</th>
            <th>Dodano</th>
            <th>Link</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in filteredItems" :key="item.item_id">
            <td>
              <div class="history-product">
                <strong>{{ item.name }}</strong>
                <span v-if="item.link">{{ compactLink(item.link) }}</span>
              </div>
            </td>
            <td><span class="history-chip history-chip--project">{{ formatProjects(item.project_names) }}</span></td>
            <td><span class="history-chip history-chip--shop">{{ item.shop_name || '-' }}</span></td>
            <td>{{ item.category_name || '-' }}</td>
            <td>{{ item.subcategory_name || '-' }}</td>
            <td><span class="history-chip history-chip--cpv">{{ item.cpv || '-' }}</span></td>
            <td class="history-price">{{ formatMoney(item.price) }} {{ item.currency || 'PLN' }}</td>
            <td>{{ formatDate(item.created_at) }}</td>
            <td>
              <a v-if="item.link" :href="item.link" target="_blank" rel="noreferrer" class="history-link">Otwórz</a>
              <span v-else>-</span>
            </td>
          </tr>
          <tr v-if="!filteredItems.length">
            <td colspan="9" class="history-empty">Brak pozycji dla wybranych filtrów.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'

const historyItems = ref([])
const filters = ref({
  search: '',
  project: '',
  shop: '',
  category: '',
  cpv: ''
})

const normalize = value => String(value || '').toLowerCase().trim()

const uniqueOptions = values =>
  [...new Set(values.filter(Boolean))].sort((a, b) => a.localeCompare(b, 'pl'))

const shopOptions = computed(() => uniqueOptions(historyItems.value.map(item => item.shop_name)))
const projectOptions = computed(() =>
  uniqueOptions(historyItems.value.flatMap(item => item.project_names || []))
)
const categoryOptions = computed(() => uniqueOptions(historyItems.value.map(item => item.category_name)))
const cpvOptions = computed(() => uniqueOptions(historyItems.value.map(item => item.cpv)))

const filteredItems = computed(() => {
  const query = normalize(filters.value.search)
  return historyItems.value.filter(item => {
    const text = normalize([
      item.name,
      ...(item.project_names || []),
      item.shop_name,
      item.category_name,
      item.subcategory_name,
      item.cpv
    ].filter(Boolean).join(' '))
    return (!query || text.includes(query))
      && (!filters.value.project || (item.project_names || []).includes(filters.value.project))
      && (!filters.value.shop || item.shop_name === filters.value.shop)
      && (!filters.value.category || item.category_name === filters.value.category)
      && (!filters.value.cpv || item.cpv === filters.value.cpv)
  })
})

const historyTotal = computed(() =>
  filteredItems.value.reduce((sum, item) => sum + Number(item.price || 0), 0)
)

const formatMoney = value => Number(value || 0).toLocaleString('pl-PL', {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2
})

const formatDate = value => {
  if (!value) return '-'
  return new Intl.DateTimeFormat('pl-PL').format(new Date(value))
}

const compactLink = value => {
  try {
    return new URL(value).hostname.replace(/^www\./, '')
  } catch {
    return value
  }
}

const formatProjects = projects => {
  if (!projects || !projects.length) return '-'
  return projects.join(', ')
}

const fetchHistory = async () => {
  try {
    const response = await fetch('http://localhost:8080/api/items', { cache: 'no-store' })
    if (!response.ok) throw new Error('Nie udalo sie pobrac historii')
    historyItems.value = await response.json()
  } catch (error) {
    console.error(error)
    historyItems.value = []
  }
}

onMounted(fetchHistory)
</script>

<style scoped>
.items-history {
  display: grid;
  gap: 1.4vw;
  width: 100%;
  padding: 2vh 0;
  color: #e2e8f0;
  font-family: 'Nunito', system-ui, sans-serif;
}

.items-history__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 2vw;
  padding-bottom: 1.2vw;
  border-bottom: 0.08vw solid rgba(148, 163, 184, 0.16);
}

.items-history__header h2 {
  margin: 0 0 0.5vw;
  color: #bfdbfe;
  font-size: 2vw;
  font-weight: 800;
}

.items-history__header p {
  margin: 0;
  color: rgba(226, 232, 240, 0.64);
  font-size: 1vw;
  line-height: 1.5;
}

.items-history__eyebrow {
  margin: 0 0 0.35vw 0 !important;
  color: #93c5fd !important;
  font-size: 0.78vw !important;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.history-refresh {
  border: 0.08vw solid rgba(96, 165, 250, 0.35);
  border-radius: 0.6vw;
  background: rgba(59, 130, 246, 0.16);
  color: #93c5fd;
  padding: 0.75vw 1.2vw;
  font-weight: 800;
  font-size: 0.9vw;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.2s ease;
}

.history-refresh:hover {
  background: rgba(59, 130, 246, 0.28);
  border-color: rgba(96, 165, 250, 0.55);
}

.history-filters {
  display: grid;
  grid-template-columns: minmax(18vw, 1.6fr) repeat(4, minmax(10vw, 1fr));
  gap: 0.9vw;
  padding: 1vw;
  border: 0.08vw solid rgba(148, 163, 184, 0.15);
  border-radius: 0.9vw;
  background: rgba(15, 23, 42, 0.5);
}

.history-filter {
  display: grid;
  gap: 0.45vw;
}

.history-filter span {
  color: rgba(226, 232, 240, 0.68);
  font-size: 0.8vw;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.history-input {
  width: 100%;
  padding: 0.8vw 0.9vw;
  border: 0.08vw solid rgba(148, 163, 184, 0.22);
  border-radius: 0.65vw;
  background: rgba(15, 23, 42, 0.68);
  color: #ffffff;
  font-size: 0.92vw;
  font-family: inherit;
  transition: border-color 0.2s ease, background 0.2s ease;
}

.history-input:focus {
  outline: none;
  border-color: rgba(96, 165, 250, 0.62);
  background: rgba(15, 23, 42, 0.92);
}

.history-input option {
  background: #0f172a;
}

.history-summary {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 1vw;
}

.history-summary > div {
  display: grid;
  gap: 0.45vw;
  padding: 1vw;
  border: 0.08vw solid rgba(148, 163, 184, 0.16);
  border-radius: 0.8vw;
  background: rgba(15, 23, 42, 0.56);
  transition: border-color 0.2s ease, background 0.2s ease;
}

.history-summary > div:hover {
  border-color: rgba(59, 130, 246, 0.32);
  background: rgba(15, 23, 42, 0.72);
}

.history-summary span {
  color: rgba(226, 232, 240, 0.62);
  font-size: 0.82vw;
  font-weight: 700;
}

.history-summary strong {
  color: #ffffff;
  font-size: 1.25vw;
}

.history-table-wrap {
  overflow-x: auto;
  border: 0.08vw solid rgba(148, 163, 184, 0.16);
  border-radius: 0.9vw;
  background: rgba(15, 23, 42, 0.42);
  box-shadow: 0 1.2vw 3vw rgba(0, 0, 0, 0.18);
}

.history-table {
  width: 100%;
  min-width: 1040px;
  border-collapse: collapse;
}

.history-table th,
.history-table td {
  padding: 0.9vw 1vw;
  border-bottom: 0.08vw solid rgba(148, 163, 184, 0.1);
  text-align: left;
  font-size: 0.88vw;
  vertical-align: middle;
}

.history-table th {
  background: rgba(30, 41, 59, 0.76);
  color: #93c5fd;
  font-size: 0.72vw;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  white-space: nowrap;
}

.history-table tr:hover {
  background: rgba(59, 130, 246, 0.035);
}

.history-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.35vw 0.65vw;
  border: 0.08vw solid rgba(96, 165, 250, 0.25);
  border-radius: 0.45vw;
  background: rgba(59, 130, 246, 0.12);
  color: #60a5fa;
  font-weight: 800;
  text-decoration: none;
}

.history-product {
  display: grid;
  gap: 0.25vw;
}

.history-product strong {
  color: #ffffff;
  font-weight: 800;
}

.history-product span {
  color: rgba(226, 232, 240, 0.55);
  font-size: 0.78vw;
}

.history-chip {
  display: inline-flex;
  align-items: center;
  max-width: 14vw;
  padding: 0.32vw 0.6vw;
  border-radius: 999px;
  font-size: 0.78vw;
  font-weight: 800;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.history-chip--shop {
  border: 0.08vw solid rgba(59, 130, 246, 0.22);
  background: rgba(59, 130, 246, 0.12);
  color: #bfdbfe;
}

.history-chip--project {
  border: 0.08vw solid rgba(34, 197, 94, 0.24);
  background: rgba(34, 197, 94, 0.12);
  color: #bbf7d0;
}

.history-chip--cpv {
  border: 0.08vw solid rgba(245, 158, 11, 0.24);
  background: rgba(245, 158, 11, 0.12);
  color: #fcd34d;
}

.history-price {
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  color: #86efac;
  font-weight: 800;
}

.history-empty {
  color: rgba(226, 232, 240, 0.64);
  text-align: center;
  padding: 2vw !important;
}

@media (max-width: 900px) {
  .items-history__header,
  .history-filters,
  .history-summary {
    grid-template-columns: 1fr;
  }

  .items-history__header {
    display: grid;
  }

  .items-history__header h2 {
    font-size: 24px;
  }

  .items-history__header p,
  .history-input,
  .history-table th,
  .history-table td {
    font-size: 14px;
  }

  .items-history__eyebrow,
  .history-filter span {
    font-size: 12px !important;
  }

  .history-summary span,
  .history-product span,
  .history-chip {
    font-size: 12px;
  }

  .history-summary strong {
    font-size: 18px;
  }

  .history-filters,
  .history-summary > div {
    padding: 14px;
    border-radius: 10px;
  }

  .history-table th,
  .history-table td {
    padding: 12px 14px;
  }

  .history-refresh {
    width: fit-content;
    padding: 10px 16px;
    border-radius: 8px;
    font-size: 14px;
  }
}
</style>
