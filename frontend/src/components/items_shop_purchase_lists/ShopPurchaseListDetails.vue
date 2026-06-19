<template>
  <div class="details-page-wrapper">
    <div class="list-details">
      <button class="back-btn" @click="$emit('back')">← Powrót do list</button>

      <div class="list-details__header">
        <div>
          <h2 class="list-details__title" :class="{ 'list-title--closed': !isListOpen }">
            <span v-if="!isListOpen" class="lock-icon">🔒</span>
            {{ list?.name || 'Nowe zamówienie' }}
          </h2>
          <div class="list-details__meta-grid">
            <p class="list-details__subtitle">
              Sklep: <span class="text-white">{{ list?.shopName || 'Brak' }}</span>
            </p>
            <div class="list-details__subtitle">
              Dostawa: 
              <template v-if="isListOpen">
                <input 
                  v-model.number="shippingCostInput" 
                  type="number" 
                  step="0.01" 
                  min="0" 
                  class="excel-inline-input shipping-cost-editable-input"
                  :disabled="isFreeDelivery"
                />
                <span class="currency-append-label">{{ currentCurrency }}</span>
              </template>
              <span v-else :class="isFreeDelivery ? 'text-emerald strike-through' : 'text-blue'">
                {{ Number(shippingCostInput).toFixed(2) }} {{ currentCurrency }}
              </span>
              <span v-if="isFreeDelivery" class="delivery-free-badge">Darmowa dostawa!</span>
            </div>
            <p v-if="list?.freeDeliveryThreshold" class="list-details__subtitle">
              Próg darmowej dostawy: <span class="text-amber">{{ (Number(list.freeDeliveryThreshold) * exchangeRate).toFixed(2) }} {{ currentCurrency }}</span>
            </p>
          </div>
        </div>
        <div class="list-details__actions">
          <div class="currency-select-container">
            <label class="sort-label">Waluta:</label>
            <select v-model="currentCurrency" class="excel-sort-select currency-dropdown" @change="handleCurrencyChange">
              <option value="PLN">PLN (zł)</option>
              <option value="EUR">EUR (€)</option>
              <option value="USD">USD ($)</option>
            </select>
            <div v-if="currentCurrency !== 'PLN'" class="currency-rate-input-block">
              <label class="sort-label rate-label">Kurs:</label>
              <input 
                v-model.number="exchangeRateInput" 
                type="number" 
                step="0.0001" 
                min="0.0001" 
                class="excel-inline-input currency-rate-input"
              />
            </div>
          </div>

          <div class="sort-select-container">
            <label class="sort-label">Sortuj:</label>
            <select v-model="sortBy" class="excel-sort-select">
              <option value="default">Kolejność dodawania</option>
              <option value="price-asc">Cena jednostkowa: rosnąco</option>
              <option value="price-desc">Cena jednostkowa: malejąco</option>
              <option value="total-asc">Suma brutto: rosnąco</option>
              <option value="total-desc">Suma brutto: malejąco</option>
              <option value="modified">Ostatnia modyfikacja</option>
              <option value="author">Współtwórca (alfabetycznie)</option>
            </select>
          </div>

          <div class="view-toggle-container">
            <button 
              class="toggle-view-btn" 
              :class="{ 'toggle-view-btn--active': currentView === 'basic' }"
              @click="setView('basic')"
            >
              Podstawowy
            </button>
            <button 
              class="toggle-view-btn" 
              :class="{ 'toggle-view-btn--active': currentView === 'accounting' }"
              @click="setView('accounting')"
            >
              Księgowy
            </button>
            <button 
              class="toggle-view-btn" 
              :class="{ 'toggle-view-btn--active': currentView === 'detailed' }"
              @click="setView('detailed')"
            >
              Szczegółowy
            </button>
          </div>
          <button class="columns-toggle-btn" @click="showColumnPicker = !showColumnPicker">⚙ Kolumny</button>
          <button v-if="isListOpen" class="add-item-btn" @click="showModal = true">Dodaj pozycję</button>
          <button v-if="canCloseList" class="close-list-btn" @click="$emit('close-list')">Zamknij koszyk i zablokuj dodawanie</button>
          <button v-else-if="canReopenList" class="reopen-list-btn" @click="$emit('reopen-list')">Otwórz ponownie do edycji</button>
          <span v-else-if="!isListOpen" class="closed-badge">Zamknięta</span>
        </div>
      </div>

      <div v-if="!isListOpen && settledInfo" class="closed-list-banner">
        <div class="closed-banner-content">
          <span class="closed-banner-icon">🔒</span>
          <div class="closed-banner-text">
            <strong>Ta lista jest zamknięta</strong>
            <span class="closed-banner-details">
              przez {{ settledInfo.closedByName }}
              <span v-if="settledInfo.closedAt">
                • {{ formatTimeAgo(settledInfo.closedAt) }}
              </span>
            </span>
          </div>
        </div>
        <span class="closed-banner-status">READ-ONLY</span>
      </div>

      <div class="procurement-tracker-banner" :class="{ 'procurement-tracker-banner--active': currentTotal > 500 }">
        <div class="procurement-banner-info">
          <span class="banner-status-icon">{{ currentTotal > 500 ? '⚠' : 'ℹ' }}</span>
          <span v-if="currentTotal > 500">
            <strong>Przekroczono próg 500 zł (Obecnie: {{ (currentTotal * exchangeRate).toFixed(2) }} {{ currentCurrency }}).</strong> Wymagane uzupełnienie rozeznania rynkowego.
          </span>
          <span v-else>
            Pamiętaj, że przy koszyku przekraczającym 500 zł konieczne jest uzupełnienie rozeznania rynkowego, aby spełnić wymogi formalne i zapewnić transparentność wyboru dostawcy.
          </span>
        </div>
        <button 
          v-if="currentTotal > 500" 
          class="procurement-action-btn" 
          @click="showProcurementModal = true"
        >
          {{ hasSavedProcurement ? 'Edytuj rozeznanie' : 'Uzupełnij rozeznanie rynkowe' }}
        </button>
      </div>

      <div v-if="showColumnPicker" class="column-picker-panel">
        <span class="column-picker-title">Widoczne kolumny:</span>
        <div class="column-picker-grid">
          <label v-for="(visible, key) in visibleColumns" :key="key" class="column-checkbox-label">
            <input type="checkbox" v-model="visibleColumns[key]" class="column-checkbox" />
            {{ columnLabels[key] }}
          </label>
        </div>
      </div>

      <div class="items-table-container custom-scrollbar">
        <table class="items-table">
          <thead>
            <tr>
              <th v-if="visibleColumns.name">Przedmiot z katalogu</th>
              <th v-if="visibleColumns.net">Jedn. Netto</th>
              <th v-if="visibleColumns.taxRate">Stawka VAT</th>
              <th v-if="visibleColumns.taxVal">Wartość VAT</th>
              <th v-if="visibleColumns.gross">Jedn. Brutto</th>
              <th v-if="visibleColumns.amount">Ilość</th>
              <th v-if="visibleColumns.totalNet">Suma Netto</th>
              <th v-if="visibleColumns.totalGross">Suma Brutto</th>
              <th v-if="visibleColumns.link">Link</th>
              <th v-if="visibleColumns.notes">Uwagi / Szczegóły</th>
              <th v-if="visibleColumns.modified">Ostatnia modyfikacja</th>
              <th v-if="canShowActions">Akcje</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in sortedListItems" :key="item.id" :class="{ 'excel-row--editing': editingItemId === item.id }">
              <td v-if="visibleColumns.name" class="font-bold excel-cell--left">
                <template v-if="editingItemId === item.id">
                  <input 
                    v-model="editFormData.name" 
                    type="text" 
                    class="excel-inline-input text-left font-bold" 
                    placeholder="Nazwa przedmiotu..."
                  />
                </template>
                <div v-else class="excel-product-cell">
                  <span class="product-name">{{ item.name }}</span>
                  <span v-if="currentView === 'detailed' && item.description" class="product-desc">{{ item.description }}</span>
                </div>
              </td>

              <td v-if="visibleColumns.net" class="excel-cell--price excel-cell--muted">
                <template v-if="editingItemId === item.id">
                  <input
                    v-model.number="editFormData.netPrice"
                    type="number"
                    step="0.01"
                    min="0"
                    class="excel-inline-input text-right text-amber"
                    @input="onNetInput"
                  />
                </template>
                <template v-else>
                  {{ Number(calculateNet(item.price, item.tax_rate) * exchangeRate).toFixed(2) }} {{ currentCurrency }}
                </template>
              </td>

              <td v-if="visibleColumns.taxRate" class="excel-cell--center excel-cell--muted">
                <template v-if="editingItemId === item.id">
                  <div class="excel-tax-input-wrapper">
                    <input 
                      v-model.number="editFormData.taxRate" 
                      type="number" 
                      min="0" 
                      max="100" 
                      step="0.01"
                      class="excel-inline-input text-center font-bold"
                      style="width: 4.5vw;"
                      @input="onTaxRateChange"
                    />
                    <span class="tax-percent-sign">%</span>
                  </div>
                </template>
                <template v-else>
                  {{ item.tax_rate ?? 23 }}%
                </template>
              </td>

              <td v-if="visibleColumns.taxVal" class="excel-cell--price excel-cell--muted">
                <template v-if="editingItemId === item.id">
                  {{ Number(editFormData.price - calculateNet(editFormData.price, editFormData.taxRate)).toFixed(2) }} {{ currentCurrency }}
                </template>
                <template v-else>
                  {{ Number((item.price - calculateNet(item.price, item.tax_rate)) * exchangeRate).toFixed(2) }} {{ currentCurrency }}
                </template>
              </td>

              <td v-if="visibleColumns.gross" class="excel-cell--price">
                <template v-if="editingItemId === item.id">
                  <input 
                    v-model.number="editFormData.price" 
                    type="number" 
                    step="0.01" 
                    min="0"
                    class="excel-inline-input text-right text-blue"
                    @input="onGrossInput"
                  />
                </template>
                <template v-else>
                  {{ Number(item.price * exchangeRate).toFixed(2) }} {{ currentCurrency }}
                </template>
              </td>

              <td v-if="visibleColumns.amount" class="excel-cell--center">
                <template v-if="editingItemId === item.id">
                  <input 
                    v-model.number="editFormData.amount" 
                    type="number" 
                    min="1"
                    class="excel-inline-input text-center"
                    @keyup.enter="saveItemEdit(item)" 
                  />
                </template>
                <template v-else>
                  {{ item.amount }} szt.
                </template>
              </td>

              <td v-if="visibleColumns.totalNet" class="excel-cell--price font-medium text-amber">
                <template v-if="editingItemId === item.id">
                  {{ Number(editFormData.netPrice * editFormData.amount).toFixed(2) }} {{ currentCurrency }}
                </template>
                <template v-else>
                  {{ Number(calculateNet(item.price, item.tax_rate) * item.amount * exchangeRate).toFixed(2) }} {{ currentCurrency }}
                </template>
              </td>

              <td v-if="visibleColumns.totalGross" class="font-bold text-blue excel-cell--price">
                <template v-if="editingItemId === item.id">
                  {{ (editFormData.price * editFormData.amount).toFixed(2) }} {{ currentCurrency }}
                </template>
                <template v-else>
                  {{ Number(item.totalPrice * exchangeRate).toFixed(2) }} {{ currentCurrency }}
                </template>
              </td>

              <td v-if="visibleColumns.link" class="excel-cell--center">
                <template v-if="editingItemId === item.id">
                  <input 
                    v-model="editFormData.link" 
                    type="text" 
                    class="excel-inline-input text-left" 
                    placeholder="URL przedmiotu..."
                  />
                </template>
                <template v-else>
                  <a v-if="item.link" :href="item.link" target="_blank" class="excel-hyperlink">Otwórz ↗</a>
                  <span v-else class="excel-cell--muted">-</span>
                </template>
              </td>

              <td v-if="visibleColumns.notes" class="excel-cell--left">
                <template v-if="editingItemId === item.id">
                  <textarea 
                    v-model="editFormData.notes" 
                    rows="1" 
                    placeholder="Dodaj uwagi..." 
                    class="excel-inline-textarea"
                  ></textarea>
                </template>
                <template v-else>
                  <span v-if="item.notes" class="excel-notes-text">{{ item.notes }}</span>
                  <span v-else class="excel-cell--muted font-italic">- brak uwag -</span>
                </template>
              </td>

              <td v-if="visibleColumns.modified" class="excel-cell--muted text-center">
                <div v-if="item.lastEditedAt" class="excel-modification-cell">
                  <span class="excel-time-ago">{{ formatTimeAgo(item.lastEditedAt) }}</span>
                  <span v-if="item.lastEditedByName" class="excel-user-id-badge">{{ item.lastEditedByName }}</span>
                </div>
                <span v-else>-</span>
              </td>

              <td v-if="canShowActions" class="excel-cell--center">
                <div class="excel-row-actions">
                  <template v-if="editingItemId === item.id">
                    <button class="save-btn" @click="saveItemEdit(item)">Zapisz</button>
                    <button class="cancel-btn" @click="cancelEdit">X</button>
                  </template>
                  <template v-else>
                    <button class="edit-btn" @click="startEdit(item)">Edytuj</button>
                    <button class="delete-btn" @click="promptRemoveItem(item)">Usuń</button>
                  </template>
                </div>
              </td>
            </tr>
            <tr v-if="listItems.length === 0">
              <td :colspan="getDynamicColspan()" class="empty-table">
                Koszyk jest pusty. Kliknij "Dodaj pozycję".
              </td>
            </tr>

            <tr v-if="listItems.length > 0" class="excel-summary-row">
              <td v-if="visibleColumns.name" class="excel-cell--left">RAZEM (SUMA)</td>
              <td v-if="visibleColumns.net"></td>
              <td v-if="visibleColumns.taxRate"></td>
              <td v-if="visibleColumns.taxVal"></td>
              <td v-if="visibleColumns.gross"></td>
              <td v-if="visibleColumns.amount" class="excel-cell--center font-bold">
                {{ listItems.reduce((sum, item) => sum + item.amount, 0) }} szt.
              </td>
              <td v-if="visibleColumns.totalNet" class="font-bold excel-cell--price excel-cell--price-net">
                {{ (totalNet * exchangeRate).toFixed(2) }} {{ currentCurrency }}
              </td>
              <td v-if="visibleColumns.totalGross" class="font-bold excel-cell--price-total">
                {{ (actualTotalWithShipping * exchangeRate).toFixed(2) }} {{ currentCurrency }}
              </td>
              <td v-if="visibleColumns.link"></td>
              <td v-if="visibleColumns.notes"></td>
              <td v-if="visibleColumns.modified"></td>
              <td v-if="canShowActions"></td>
            </tr>
          </tbody>
        </table>
      </div>

      <AddItemToListModal
        v-if="isListOpen"
        :isOpen="showModal"
        :currentTotal="currentTotal"
        :maxBudget="list?.maxBudget || 0"
        @close="showModal = false"
        @add-to-list="addItemToList"
      />
    </div>

    <div v-if="showDeleteModal" class="confirm-modal-overlay" @click="showDeleteModal = false">
      <div class="confirm-modal-content" @click.stop>
        <h2 class="confirm-modal-title">Usuwanie przedmiotu</h2>
        <p class="confirm-modal-text">Czy na pewno chcesz usunąć tę pozycję z koszyka?</p>
        <div class="confirm-modal-actions">
          <button class="confirm-btn confirm-btn-cancel" @click="showDeleteModal = false">Anuluj</button>
          <button class="confirm-btn confirm-btn-danger" @click="executeRemoveItem">Tak, usuń</button>
        </div>
      </div>
    </div>

    <div v-if="showProcurementModal" class="confirm-modal-overlay" @click="showProcurementModal = false">
      <div class="confirm-modal-content confirm-modal-content--procurement" @click.stop>
        <h2 class="confirm-modal-title text-amber">Rozeznanie Rynkowe</h2>
        
        <div class="procurement-dashboard">
          <div class="dashboard-card">
            <span class="card-icon">📸</span>
            <span class="card-title">Przynajmnniej 3 screeny</span>
            <p class="card-desc">Porównaj ceny tej samej zawartości w <strong>minimum 3 różnych sklepach</strong> konkurencyjnych.</p>
          </div>
          <div class="dashboard-card">
            <span class="card-icon">🔄</span>
            <span class="card-title">Koszyk nie musi być 1:1</span>
            <p class="card-desc">Możesz porównać część produktów w różnych sklepach. Np. przy zamówieniu różnych 10 produktów, 6 może być porównywanych w sklepach A i B, a 4 w sklepach C i D.</p>
          </div>
          <div class="dashboard-card">
            <span class="card-icon">⚖</span>
            <span class="card-title">Częściowo drożej?</span>
            <p class="card-desc">W koszyku jest bulbulator za 450 zł oraz 20 różnych produktów o sumie 60 zł. Możesz porównać tylko bulbulator i napisać, że reszta produktów ma porównywalne ceny w innych sklepach.</p>
          </div>
          <div class="dashboard-card">
            <span class="card-icon">🚚</span>
            <span class="card-title">Inne argumenty</span>
            <p class="card-desc">Brak produktów w innych sklepach na terenie UE, brak produktów na magazynie mimo niskiej ceny, czy inne okoliczności, to też argumenty, które można przytoczyć w rozeznaniu.</p>
          </div>
        </div>

        <div class="procurement-form-body">
          <div class="form-group">
            <label class="form-label">Komentarz do rozeznania<span class="text-danger">*</span></label>
            <textarea 
              v-model="procurementComment" 
              placeholder="Jeśli sprawa wymaga dodatkowego komentarza, tutaj możesz go zamieścić" 
              rows="3" 
              class="excel-inline-textarea procurement-textarea"
            ></textarea>
          </div>

          <div class="form-group">
            <label class="form-label">Zrzuty ekranu / Zestawienie cenowe (najlepiej w docx)</label>
            <div class="file-upload-dropzone">
              <input type="file" accept=".pdf,.docx,.doc" @change="handleProcurementFileChange" class="hidden-file-input" id="procurementFile" />
              <label for="procurementFile" class="file-upload-label" @click="$el.querySelector('#procurementFile').click()">
                <span class="upload-icon">📁</span>
                <span v-if="procurementFile" class="text-white font-bold">{{ procurementFile.name }}</span>
                <span v-else class="text-muted">Kliknij, aby podpiąć plik</span>
              </label>
            </div>
          </div>
        </div>

        <div class="confirm-modal-actions">
          <button class="confirm-btn confirm-btn-cancel" @click="showProcurementModal = false">Anuluj</button>
          <button class="confirm-btn confirm-btn-save-procurement" :disabled="!isProcurementValid" @click="saveProcurementData">Zatwierdź rozeznanie</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import AddItemToListModal from './AddItemToListModal.vue'
import { useToast } from '@/composables/useToast'
import { useAuth } from '@/composables/useAuth'

const toast = useToast()
const { user } = useAuth()
const showDeleteModal = ref(false)
const itemToDeleteId = ref(null)
const currentView = ref('basic')
const sortBy = ref('default')
const showColumnPicker = ref(false)

const shippingCostInput = ref(0)
const showProcurementModal = ref(false)
const procurementFile = ref(null)
const procurementComment = ref('')
const hasSavedProcurement = ref(false)

const currentCurrency = ref('PLN')
const exchangeRateInput = ref(1.0000)

const props = defineProps({
  list: { type: Object, required: true },
  canManageItems: { type: Boolean, default: false },
  canCloseList: { type: Boolean, default: false },
  canReopenList: { type: Boolean, default: false }
})

const emit = defineEmits(['back', 'close-list', 'reopen-list', 'market-research-saved'])

const showModal = ref(false)
const listItems = ref([])
const students = ref({})
const isListOpen = computed(() => props.list?.isOpen !== false)
const canShowActions = computed(() => isListOpen.value)

const settledInfo = computed(() => {
  if (isListOpen.value) return null
  
  return {
    closedByName: props.list?.closedByName || props.list?.settledByName || 'Skarbnik',
    closedAt: props.list?.closedAt || props.list?.settlementDate || null
  }
})

const currentStudentId = computed(() => user.value?.id)

const visibleColumns = ref({
  name: true,
  net: false,
  taxRate: false,
  taxVal: false,
  gross: true,
  amount: true,
  totalNet: false,
  totalGross: true,
  link: true,
  notes: true,
  modified: false
})

const columnLabels = {
  name: 'Nazwa przedmiotu',
  net: 'Cena Netto',
  taxRate: 'Stawka VAT',
  taxVal: 'Wartość VAT',
  gross: 'Cena Brutto',
  amount: 'Ilość',
  totalNet: 'Suma Netto',
  totalGross: 'Suma Brutto',
  link: 'Link',
  notes: 'Uwagi',
  modified: 'Ostatnia modyfikacja'
}

const exchangeRate = computed(() => {
  if (currentCurrency.value === 'PLN') return 1.0000
  return Number(exchangeRateInput.value) || 1.0000
})

const handleCurrencyChange = () => {
  if (currentCurrency.value === 'PLN') {
    exchangeRateInput.value = 1.0000
  } else if (currentCurrency.value === 'EUR') {
    exchangeRateInput.value = 0.2300 
  } else if (currentCurrency.value === 'USD') {
    exchangeRateInput.value = 0.2500
  }
}

const setView = (view) => {
  currentView.value = view
  if (view === 'basic') {
    visibleColumns.value = { name: true, net: false, taxRate: false, taxVal: false, gross: true, amount: true, totalNet: false, totalGross: true, link: true, notes: true, modified: false }
  } else if (view === 'accounting') {
    visibleColumns.value = { name: true, net: true, taxRate: true, taxVal: true, gross: true, amount: true, totalNet: true, totalGross: true, link: true, notes: true, modified: false }
  } else if (view === 'detailed') {
    visibleColumns.value = { name: true, net: false, taxRate: false, taxVal: false, gross: true, amount: true, totalNet: false, totalGross: true, link: true, notes: true, modified: true }
  }
}

const sortedListItems = computed(() => {
  const itemsCopy = [...listItems.value]
  if (sortBy.value === 'price-asc') return itemsCopy.sort((a, b) => Number(a.price) - Number(b.price))
  if (sortBy.value === 'price-desc') return itemsCopy.sort((a, b) => Number(b.price) - Number(a.price))
  if (sortBy.value === 'total-asc') return itemsCopy.sort((a, b) => Number(a.totalPrice) - Number(b.totalPrice))
  if (sortBy.value === 'total-desc') return itemsCopy.sort((a, b) => Number(b.totalPrice) - Number(a.totalPrice))
  if (sortBy.value === 'modified') {
    return itemsCopy.sort((a, b) => {
      const timeA = a.lastEditedAt ? new Date(a.lastEditedAt).getTime() : 0
      const timeB = b.lastEditedAt ? new Date(b.lastEditedAt).getTime() : 0
      return timeB - timeA
    })
  }
  if (sortBy.value === 'author') {
    return itemsCopy.sort((a, b) => {
      return (a.lastEditedByName || '').toLowerCase().localeCompare((b.lastEditedByName || '').toLowerCase(), 'pl')
    })
  }
  return itemsCopy
})

const calculateNet = (grossPrice, taxRate) => {
  const rate = taxRate !== undefined ? (Number(taxRate) / 100) : 0.23
  return Number(grossPrice) / (1 + rate)
}

const totalNet = computed(() => {
  return listItems.value.reduce((sum, item) => sum + (calculateNet(item.price, item.tax_rate) * item.amount), 0)
})

const isFreeDelivery = computed(() => {
  if (!props.list?.freeDeliveryThreshold) return false
  return currentTotal.value >= Number(props.list.freeDeliveryThreshold)
})

const actualTotalWithShipping = computed(() => {
  const base = currentTotal.value
  if (isFreeDelivery.value) return base
  return base + Number(shippingCostInput.value || 0)
})

const isProcurementValid = computed(() => {
  return procurementComment.value.trim().length >= 10
})

const getDynamicColspan = () => {
  let count = Object.values(visibleColumns.value).filter(Boolean).length
  if (canShowActions.value) count += 1
  return count
}

const handleProcurementFileChange = (e) => {
  const files = e.target.files
  if (files && files.length > 0) {
    procurementFile.value = files[0]
  }
}

const hydrateProcurementData = () => {
  procurementComment.value = props.list?.market_research_comment || ''
  const fileName = props.list?.market_research_file_name
  procurementFile.value = fileName ? { name: fileName } : null
  hasSavedProcurement.value = Boolean(procurementComment.value || fileName)
}

const saveProcurementData = async () => {
  if (!isProcurementValid.value) return
  try {
    const response = await fetch(`http://localhost:8080/api/lists/${props.list.shop_purchase_list_id}/market_research`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        market_research_comment: procurementComment.value,
        market_research_file_name: procurementFile.value?.name || null
      })
    })
    const data = await response.json()
    if (!response.ok) throw new Error(data.detail || 'Nie udało się zapisać rozeznania.')

    hasSavedProcurement.value = true
    showProcurementModal.value = false
    emit('market-research-saved', data)
    toast.success('Uproszczone rozeznanie rynkowe zostało zatwierdzone.')
  } catch (error) {
    console.error(error)
    toast.error(error.message || 'Nie udało się zapisać rozeznania.')
  }
}

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

const fetchStudents = async () => {
  try {
    const response = await fetch('http://localhost:8080/api/students', { cache: 'no-store' })
    if (!response.ok) throw new Error('Błąd pobierania studentów')
    const data = await response.json()
    const map = {}
    ;(data || []).forEach(s => {
      const id = s.student_id ?? s.id
      const name = [s.name, s.surname].filter(Boolean).join(' ') || null
      if (id) map[id] = name || `ID: ${id}`
    })
    students.value = map
  } catch (error) {
    console.error(error)
  }
}

const fetchListItems = async () => {
  try {
    const timestamp = new Date().getTime()
    const params = new URLSearchParams({ t: String(timestamp) })
    if (currentStudentId.value) params.set('student_id', currentStudentId.value)
    const response = await fetch(`http://localhost:8080/api/lists/${props.list.id}/items?${params.toString()}`, { cache: 'no-store' })
    if (!response.ok) throw new Error('Błąd sieci')
    const data = await response.json()
    listItems.value = data.map(item => {
      const byId = item.student_id
      return {
        ...item,
        id: item.line_item_id,
        amount: item.amount,
        totalPrice: item.total_price,
        notes: item.notes || '',
        currentStudentAmount: item.current_student_amount || 0,
        canRemoveByCurrentStudent: true,
        lastEditedAt: item.updated_at || item.created_at,
        lastEditedById: byId,
        lastEditedByName: byId ? (students.value?.[byId] || `ID: ${byId}`) : null
      }
    })
  } catch (error) {
    console.error(error)
  }
}

const addItemToList = async (arg1, arg2) => {
  try {
    const isInlineItem = arg1 && typeof arg1 === 'object' && !arg1.item_id && !arg1.id
    const targetItemId = arg1 && typeof arg1 === 'object' ? (arg1.item_id || arg1.id) : arg1
    const targetAmount = arg1 && typeof arg1 === 'object' ? (arg1.amount || arg1.quantity || 1) : (arg2 || 1)
    if (!isInlineItem && !targetItemId) return
    const payload = isInlineItem
      ? {
          name: arg1.name,
          link: arg1.link || null,
          price: Number(arg1.price),
          currency: arg1.currency || 'PLN',
          product_subcategory_id: Number(arg1.product_subcategory_id),
          amount: parseInt(targetAmount),
          student_id: currentStudentId.value,
          notes: arg1.notes || ''
        }
      : {
          item_id: parseInt(targetItemId),
          amount: parseInt(targetAmount),
          student_id: currentStudentId.value,
          notes: ''
        }
    const response = await fetch(`http://localhost:8080/api/lists/${props.list.id}/items`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    if (!response.ok) throw new Error('Nie udalo sie dodac pozycji')
    await fetchListItems()
    showModal.value = false
    toast.success('Dodano do koszyka!')
  } catch (error) {
    console.error(error)
    toast.error(error.message || 'Nie udalo sie dodac pozycji.')
  }
}

const promptRemoveItem = (item) => { if (canRemoveItem()) { itemToDeleteId.value = item.id; showDeleteModal.value = true; } }

const executeRemoveItem = async () => {
  if (!itemToDeleteId.value) return
  try {
    const params = new URLSearchParams()
    if (currentStudentId.value) params.set('student_id', currentStudentId.value)
    const response = await fetch(`http://localhost:8080/api/lists/${props.list.id}/items/${itemToDeleteId.value}?${params.toString()}`, { method: 'DELETE' })
    if (response.ok) { await fetchListItems(); toast.info('Usunięto przedmiot.'); }
  } catch (error) {
    console.error(error)
  } finally { showDeleteModal.value = false; itemToDeleteId.value = null; }
}

const currentTotal = computed(() => listItems.value.reduce((sum, item) => sum + item.totalPrice, 0))

const editingItemId = ref(null)
const editFormData = ref({ name: '', price: 0, netPrice: 0, taxRate: 23, amount: 0, link: '', notes: '' })
const editLastEditedPriceField = ref('net')

const startEdit = (item) => {
  editingItemId.value = item.id
  const localGross = item.price * exchangeRate.value
  const localNet = calculateNet(item.price, item.tax_rate) * exchangeRate.value
  editFormData.value = {
    name: item.name || '',
    price: parseFloat(localGross.toFixed(2)),
    netPrice: parseFloat(localNet.toFixed(2)),
    taxRate: item.tax_rate !== undefined ? item.tax_rate : 23,
    amount: item.amount,
    link: item.link || '',
    notes: item.notes || ''
  }
}

const cancelEdit = () => { editingItemId.value = null }

const onNetInput = () => {
  editLastEditedPriceField.value = 'net'
  const factor = 1 + (editFormData.value.taxRate / 100)
  const calculatedGross = editFormData.value.netPrice * factor
  editFormData.value.price = parseFloat(calculatedGross.toFixed(2))
}

const onGrossInput = () => {
  editLastEditedPriceField.value = 'gross'
  const factor = 1 + (editFormData.value.taxRate / 100)
  const calculatedNetVal = editFormData.value.price / factor
  editFormData.value.netPrice = parseFloat(calculatedNetVal.toFixed(2))
}

const onTaxRateChange = () => {
  const factor = 1 + (editFormData.value.taxRate / 100)
  if (editLastEditedPriceField.value === 'gross') {
    const calculatedNetVal = editFormData.value.price / factor
    editFormData.value.netPrice = parseFloat(calculatedNetVal.toFixed(2))
  } else {
    const calculatedGross = editFormData.value.netPrice * factor
    editFormData.value.price = parseFloat(calculatedGross.toFixed(2))
  }
}

const saveItemEdit = async (item) => {
  try {
    const basePriceInPln = editFormData.value.price / exchangeRate.value
    const payload = {
      item_id: item.item_id,
      name: editFormData.value.name,
      price: parseFloat(basePriceInPln.toFixed(4)),
      tax_rate: parseFloat(editFormData.value.taxRate || 0),
      amount: parseInt(editFormData.value.amount),
      link: editFormData.value.link,
      product_subcategory_id: item.product_subcategory_id,
      student_id: currentStudentId.value,
      notes: editFormData.value.notes
    }
    const response = await fetch(`http://localhost:8080/api/lists/${props.list.id}/items/${item.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    if (response.ok) { toast.success('Zapisano zmiany!'); editingItemId.value = null; await fetchListItems(); }
  } catch (error) {
    console.error(error)
  }
}

onMounted(async () => {
  hydrateProcurementData()
  await fetchStudents()
  await fetchListItems()
  if (props.list?.shippingCost) {
    shippingCostInput.value = props.list.shippingCost
  }
})

watch(
  () => props.list?.shop_purchase_list_id,
  () => hydrateProcurementData()
)
</script>

<style scoped>
.details-page-wrapper { width: 100%; }
.list-details { color: rgb(var(--rgb-text)); padding: 1vw 0; animation: fadeIn 0.3s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(1vh); } to { opacity: 1; transform: translateY(0); } }

.back-btn { background: none; border: none; color: var(--color-link); cursor: pointer; font-size: 1vw; margin-bottom: 2vh; font-weight: 700; transition: color 0.2s; }
.back-btn:hover { color: rgb(var(--rgb-text)); }

.list-details__header { display: flex; justify-content: space-between; align-items: center; gap: 2vw; margin-bottom: 2vh; }
.list-details__title { font-size: 2vw; color: var(--color-heading); margin: 0 0 0.5vh 0; }
.list-details__meta-grid { display: grid; grid-template-columns: repeat(2, auto); gap: 0.4vw 2vw; margin-top: 0.5vh; }
.list-details__subtitle { color: rgba(var(--rgb-muted), 0.6); margin: 0; font-size: 1vw; font-weight: 600; display: flex; align-items: center; gap: 0.4vw; }

.shipping-cost-editable-input { width: 5.5vw !important; padding: 0.1vw 0.3vw !important; text-align: center; font-family: monospace; color: #60a5fa !important; font-weight: 700; }
.currency-append-label { font-size: 0.8vw; color: #64748b; font-weight: 700; margin-left: -0.2vw; }
.delivery-free-badge { background: rgba(52, 211, 153, 0.15); color: #34d399; font-size: 0.75vw; font-weight: 800; padding: 0.15vw 0.5vw; border-radius: 0.3vw; border: 1px solid rgba(52, 211, 153, 0.25); text-transform: uppercase; letter-spacing: 0.03em; margin-left: 0.2vw; display: inline-block; }
.strike-through { text-decoration: line-through; opacity: 0.5; }

.procurement-tracker-banner { display: flex; align-items: center; justify-content: space-between; gap: 1vw; padding: 0.8vw 1.2vw; background: rgba(var(--rgb-raised), 0.5); border: 1px solid rgba(148, 163, 184, 0.15); border-radius: 0.6vw; margin-bottom: 3vh; font-size: 0.9vw; color: #94a3b8; transition: all 0.3s ease; }
.procurement-tracker-banner--active { background: rgba(245, 158, 11, 0.08); border-color: rgba(245, 158, 11, 0.25); color: rgb(var(--rgb-muted)); }
.procurement-banner-info { display: flex; align-items: center; gap: 0.5vw; }
.banner-status-icon { font-size: 1.2vw; font-weight: 800; line-height: 1; }
.procurement-tracker-banner--active .banner-status-icon { color: #fbbf24; }
.procurement-action-btn { padding: 0.4vw 1vw; background: rgba(245, 158, 11, 0.15); color: #fcd34d; border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 0.5vw; font-size: 0.8vw; font-weight: 800; cursor: pointer; transition: all 0.2s; white-space: nowrap; }
.procurement-action-btn:hover { background: #d97706; color: rgb(var(--rgb-text)); border-color: #d97706; }

.list-details__actions { display: flex; align-items: center; justify-content: flex-end; gap: 0.8vw; flex-wrap: wrap; }

.currency-select-container { display: flex; align-items: center; gap: 0.4vw; background: rgba(var(--rgb-raised), 0.8); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 0.6vw; padding: 0.2vw 0.6vw; }
.currency-dropdown { width: 5.5vw; }
.currency-rate-input-block { display: flex; align-items: center; gap: 0.3vw; margin-left: 0.4vw; border-left: 1px solid rgba(148, 163, 184, 0.2); padding-left: 0.6vw; }
.rate-label { color: #34d399 !important; }
.currency-rate-input { width: 4.8vw; padding: 0.15vw 0.3vw; font-family: monospace; font-size: 0.8vw; color: #34d399 !important; font-weight: 700; text-align: center; }

.sort-select-container { display: flex; align-items: center; gap: 0.4vw; background: rgba(var(--rgb-raised), 0.8); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 0.6vw; padding: 0.2vw 0.6vw; }
.sort-label { font-size: 0.8vw; color: #94a3b8; font-weight: 700; text-transform: uppercase; }
.excel-sort-select { background: transparent; border: none; color: #60a5fa; font-size: 0.85vw; font-weight: 700; cursor: pointer; outline: none; font-family: 'Nunito', system-ui, sans-serif; }
.excel-sort-select option { background: #0f172a; color: rgb(var(--rgb-text)); }

.view-toggle-container { display: flex; background: rgba(var(--rgb-raised), 0.8); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 0.6vw; padding: 0.2vw; }
.toggle-view-btn { background: transparent; border: none; color: #94a3b8; padding: 0.5vw 1vw; font-size: 0.85vw; font-weight: 700; border-radius: 0.4vw; cursor: pointer; transition: all 0.2s ease; font-family: 'Nunito', system-ui, sans-serif; }
.toggle-view-btn--active { background: rgba(59, 130, 246, 0.2); color: #60a5fa; }

.columns-toggle-btn { padding: 0.6vw 1.2vw; background: rgba(var(--rgb-raised), 0.8); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 0.6vw; color: rgb(var(--rgb-muted)); font-size: 0.85vw; font-weight: 700; cursor: pointer; transition: all 0.2s; font-family: 'Nunito', system-ui, sans-serif; }
.columns-toggle-btn:hover { background: rgba(148, 163, 184, 0.15); }

.column-picker-panel { background: rgba(var(--rgb-surface), 0.7); border: 1px solid rgba(59, 130, 246, 0.2); border-radius: 0.8vw; padding: 1.2vw; margin-bottom: 2vh; animation: fadeIn 0.2s ease; backdrop-filter: blur(5px); }
.column-picker-title { display: block; font-size: 0.85vw; font-weight: 800; color: #94a3b8; text-transform: uppercase; margin-bottom: 0.8vw; letter-spacing: 0.05em; }
.column-picker-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(11vw, 1fr)); gap: 0.8vw; }
.column-checkbox-label { display: flex; align-items: center; gap: 0.5vw; color: rgb(var(--rgb-muted)); font-size: 0.9vw; font-weight: 600; cursor: pointer; transition: color 0.2s; }
.column-checkbox-label:hover { color: #60a5fa; }
.column-checkbox { width: 0.95vw; height: 0.95vw; accent-color: #3b82f6; cursor: pointer; }

.add-item-btn { padding: 0.8vw 1.5vw; background: linear-gradient(135deg, #3b82f6, #2563eb); border: none; border-radius: 0.8vw; color: rgb(var(--rgb-text)); font-weight: 700; cursor: pointer; font-size: 0.95vw; box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3); transition: all 0.2s; }
.add-item-btn:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4); }

.close-list-btn { padding: 0.8vw 1.3vw; background: rgba(245, 158, 11, 0.18); border: 1px solid rgba(245, 158, 11, 0.35); border-radius: 0.8vw; color: #fcd34d; font-weight: 800; cursor: pointer; font-size: 0.95vw; transition: all 0.2s; }
.close-list-btn:hover { background: rgba(245, 158, 11, 0.3); transform: translateY(-2px); }
.reopen-list-btn { padding: 0.8vw 1.3vw; background: rgba(16, 185, 129, 0.18); border: 1px solid rgba(16, 185, 129, 0.35); border-radius: 0.8vw; color: #6ee7b7; font-weight: 800; cursor: pointer; font-size: 0.95vw; transition: all 0.2s; }
.reopen-list-btn:hover { background: rgba(16, 185, 129, 0.32); transform: translateY(-2px); }
.closed-badge { padding: 0.7vw 1vw; border-radius: 0.7vw; background: rgba(148, 163, 184, 0.14); color: var(--color-subtle); font-size: 0.9vw; font-weight: 800; }

.items-table-container { background: rgba(var(--rgb-surface), 0.4); border: 1px solid rgba(148, 163, 184, 0.15); border-radius: 0.8vw; overflow-x: auto; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2); width: 100%; max-width: 100%; box-sizing: border-box; }
.items-table-container::-webkit-scrollbar { height: 7px; background: rgba(var(--rgb-raised), 0.5); border-radius: 10px; }
.items-table-container::-webkit-scrollbar-thumb { background: rgba(59, 130, 246, 0.3); border-radius: 10px; border: 1px solid transparent; background-clip: padding-box; transition: background 0.2s ease; }
.items-table-container::-webkit-scrollbar-thumb:hover { background: rgba(59, 130, 246, 0.7); }

.items-table { width: 100%; border-collapse: collapse; text-align: left; font-size: 0.85vw; table-layout: auto; }
.items-table th, .items-table td { padding: 0.8vw 1.2vw; border-bottom: 1px solid rgba(148, 163, 184, 0.1); vertical-align: middle; }
.items-table th { background: rgba(var(--rgb-raised), 0.8); color: #94a3b8; font-weight: 700; text-transform: uppercase; font-size: 0.75vw; letter-spacing: 0.05em; border-bottom: 2px solid rgba(148, 163, 184, 0.2); white-space: nowrap; }
.items-table tr:hover { background: rgba(59, 130, 246, 0.03); }

.items-table--view-accounting { min-width: 1200px; }
.items-table--view-accounting th, .items-table--view-accounting td { font-size: 0.8vw !important; padding: 0.7vw 0.8vw !important; }

.excel-cell--left { text-align: left; }
.excel-cell--center { text-align: center; }
.excel-cell--price { text-align: right; font-family: monospace; font-size: 0.9vw; color: rgb(var(--rgb-muted)); white-space: nowrap; }
.excel-cell--muted { color: #64748b; font-size: 0.85vw; }
.text-amber { color: #fbbf24 !important; }
.text-blue { color: #60a5fa !important; }
.text-emerald { color: #34d399 !important; }
.text-white { color: rgb(var(--rgb-text)) !important; }

.excel-product-cell { display: flex; flex-direction: column; gap: 0.2vw; }
.product-name { color: rgb(var(--rgb-text)); white-space: nowrap; }
.product-desc { font-size: 0.75vw; color: #64748b; font-weight: 500; }

.excel-hyperlink { color: #38bdf8; text-decoration: none; font-weight: 700; font-size: 0.85vw; padding: 0.2vw 0.5vw; background: rgba(56, 189, 248, 0.1); border-radius: 0.3vw; transition: all 0.2s; display: inline-block; white-space: nowrap; }
.excel-hyperlink:hover { background: #38bdf8; color: #0f172a; }

.excel-notes-text { font-size: 0.8vw; color: var(--color-subtle); word-break: break-word; max-width: 15vw; display: inline-block; }
.excel-inline-textarea { width: 100%; box-sizing: border-box; background: #1e293b; border: 1px solid #3b82f6; border-radius: 0.3vw; color: rgb(var(--rgb-text)); padding: 0.4vw 0.6vw; font-family: inherit; font-size: 0.8vw; outline: none; resize: none; }

.excel-modification-cell { display: flex; flex-direction: column; align-items: center; gap: 0.1vw; white-space: nowrap; }
.excel-time-ago { font-size: 0.75vw; color: #94a3b8; }
.excel-user-id-badge { display: inline-block; padding: 0.15vw 0.4vw; background: rgba(59, 130, 246, 0.12); color: #60a5fa; border-radius: 0.3vw; font-size: 0.7vw; font-weight: 700; border: 1px solid rgba(59, 130, 246, 0.2); }

.excel-summary-row { background: rgba(var(--rgb-raised), 0.5) !important; }
.excel-summary-row td { border-top: 2px solid rgba(148, 163, 184, 0.3); border-bottom: 2px double rgba(148, 163, 184, 0.4) !important; color: #94a3b8; font-weight: 700; font-size: 0.85vw; }
.excel-cell--price-net { text-align: right; font-family: monospace; font-size: 0.95vw; color: #fbbf24 !important; }
.excel-cell--price-total { text-align: right; font-family: monospace; font-size: 1vw; color: #38bdf8 !important; }

.excel-inline-input { box-sizing: border-box; background: #1e293b; border: 1px solid #3b82f6; border-radius: 0.3vw; color: rgb(var(--rgb-text)); padding: 0.2vw 0.4vw; font-size: 0.85vw; outline: none; }
.excel-inline-input:focus { box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.4); }
.excel-inline-input.text-right { font-family: monospace; width: 6.5vw; }
.excel-inline-input.text-center { width: 3.5vw; }
.excel-inline-input.text-left { width: 100%; font-family: inherit; }

.excel-tax-input-wrapper { display: flex; align-items: center; justify-content: center; gap: 0.1vw; }
.tax-percent-sign { color: #64748b; font-size: 0.85vw; font-weight: 700; font-family: monospace; }

.procurement-dashboard { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1vw; margin-bottom: 1.5vw; }
.dashboard-card { background: rgba(var(--rgb-surface), 0.6); border: 1px solid rgba(148, 163, 184, 0.1); border-radius: 0.8vw; padding: 1vw; text-align: left; display: flex; flex-direction: column; gap: 0.3vw; }
.card-icon { font-size: 1.3vw; margin-bottom: 0.2vw; }
.card-title { font-weight: 800; font-size: 0.9vw; color: var(--color-heading); text-transform: uppercase; letter-spacing: 0.02em; }
.card-desc { font-size: 0.8vw; color: rgba(var(--rgb-muted), 0.65); margin: 0; line-height: 1.4; }

.procurement-form-body { display: flex; flex-direction: column; gap: 1.5vw; text-align: left; }
.procurement-textarea { font-family: inherit !important; font-size: 0.9vw !important; line-height: 1.4; }
.form-group { display: flex; flex-direction: column; gap: 0.5vw; }
.form-label { color: #94a3b8; font-size: 0.85vw; font-weight: 700; text-transform: uppercase; }
.file-upload-dropzone { background: rgba(var(--rgb-raised), 0.5); border: 2px dashed rgba(148, 163, 184, 0.3); border-radius: 0.8vw; padding: 1.5vw; text-align: center; cursor: pointer; transition: border-color 0.2s; }
.file-upload-dropzone:hover { border-color: #3b82f6; }
.file-upload-label { cursor: pointer; display: flex; flex-direction: column; align-items: center; gap: 0.5vw; }
.upload-icon { font-size: 2vw; }
.hidden-file-input { display: none; }

.confirm-modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background-color: rgba(5, 8, 22, 0.85); display: flex; align-items: center; justify-content: center; z-index: 9999; backdrop-filter: blur(8px); }
.confirm-modal-content { background: #0f172a; border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 1.5vw; padding: 3vw; width: 90%; max-width: 32vw; text-align: center; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7); animation: modalPop 0.3s cubic-bezier(0.34, 1.56, 0.64, 1); }
.confirm-modal-content--procurement { border-color: rgba(148, 163, 184, 0.15); max-width: 36vw; padding: 2.2vw; }
@keyframes modalPop { 0% { transform: scale(0.9); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }
.confirm-modal-title { font-size: 1.6vw; font-weight: 800; margin: 0 0 1vw 0; }

.confirm-btn { padding: 0.9vw 2.5vw; border-radius: 0.8vw; font-size: 1.1vw; font-weight: 800; cursor: pointer; border: none; transition: all 0.2s ease; }
.confirm-btn-cancel { background: rgba(148, 163, 184, 0.15); color: rgb(var(--rgb-muted)); }
.confirm-btn-cancel:hover { background: rgba(148, 163, 184, 0.3); color: rgb(var(--rgb-text)); }
.confirm-btn-danger { background: linear-gradient(135deg, #ef4444, #dc2626); color: rgb(var(--rgb-text)); box-shadow: 0 10px 20px rgba(239, 68, 68, 0.3); }
.confirm-btn-danger:hover { transform: translateY(-0.3vh); filter: brightness(1.1); box-shadow: 0 14px 28px rgba(239, 68, 68, 0.5); }
.confirm-btn-save-procurement { background: linear-gradient(135deg, #3b82f6, #2563eb); color: rgb(var(--rgb-text)); box-shadow: 0 6px 15px rgba(37, 99, 235, 0.2); }
.confirm-btn-save-procurement:disabled { opacity: 0.3; cursor: not-allowed; transform: none !important; box-shadow: none !important; }
.confirm-btn-save-procurement:not(:disabled):hover { transform: translateY(-0.2vh); filter: brightness(1.1); box-shadow: 0 8px 20px rgba(37, 99, 235, 0.35); }

.font-bold { font-weight: 700; }
.font-medium { font-weight: 500; }
.font-italic { font-style: italic; }
.empty-table { text-align: center; color: rgba(var(--rgb-muted), 0.5); padding: 3vw; font-style: italic; }
.excel-row--editing { background: rgba(59, 130, 246, 0.08) !important; }
.excel-row-actions { display: flex; gap: 0.4vw; justify-content: center; }
.edit-btn { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); padding: 0.4vw 0.8vw; border-radius: 0.4vw; font-size: 0.75vw; font-weight: 700; cursor: pointer; transition: all 0.2s; }
.edit-btn:hover { background: rgba(16, 185, 129, 0.3); }
.save-btn { background: rgba(52, 211, 153, 0.15); color: #34d399; border: 1px solid rgba(52, 211, 153, 0.3); padding: 0.4vw 0.8vw; border-radius: 0.4vw; font-size: 0.75vw; font-weight: 700; cursor: pointer; }
.save-btn:hover { background: rgba(52, 211, 153, 0.3); }
.cancel-btn { background: #475569; color: rgb(var(--rgb-text)); border: none; padding: 0.4vw 0.6vw; border-radius: 0.4vw; font-size: 0.75vw; font-weight: 700; cursor: pointer; }
.cancel-btn:hover { background: #64748b; }
.delete-btn { background: rgba(239, 68, 68, 0.15); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.3); padding: 0.3vw 0.6vw; border-radius: 0.4vw; font-size: 0.75vw; font-weight: 700; cursor: pointer; transition: all 0.2s; }
.delete-btn:hover { background: rgba(239, 68, 68, 0.3); }

.list-title--closed {
  color: #94a3b8 !important;
  opacity: 0.75;
}
.lock-icon {
  margin-right: 0.5vw;
  font-size: 1.8vw;
}

.closed-list-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.2vw 1.5vw;
  background: rgba(71, 85, 105, 0.15);
  border: 1px solid rgba(148, 163, 184, 0.25);
  border-radius: 0.8vw;
  margin-bottom: 2vh;
  animation: slideIn 0.3s ease;
}
@keyframes slideIn {
  from { transform: translateY(-1vh); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.closed-banner-content {
  display: flex;
  align-items: center;
  gap: 1vw;
  flex: 1;
}

.closed-banner-icon {
  font-size: 1.6vw;
  opacity: 0.8;
}

.closed-banner-text {
  display: flex;
  flex-direction: column;
  gap: 0.2vw;
}

.closed-banner-text strong {
  color: var(--color-subtle);
  font-size: 0.95vw;
}

.closed-banner-details {
  color: #94a3b8;
  font-size: 0.85vw;
  font-weight: 500;
}

.closed-banner-status {
  background: rgba(148, 163, 184, 0.2);
  color: var(--color-subtle);
  padding: 0.5vw 1vw;
  border-radius: 0.5vw;
  font-size: 0.8vw;
  font-weight: 800;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}
</style>
