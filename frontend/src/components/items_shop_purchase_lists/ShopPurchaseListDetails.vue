<template>
  <div class="list-details">
    <button class="back-btn" @click="$emit('back')">← Powrót do moich list</button>

    <div class="list-details__header">
      <div>
        <h2 class="list-details__title">{{ list.name }}</h2>
        <p class="list-details__subtitle">
          Sklep: {{ list.shopName }} | Budżet: {{ currentTotal.toFixed(2) }} / {{ list.maxBudget.toFixed(2) }} PLN
        </p>
      </div>
      <button class="add-item-btn" @click="showModal = true">+ Dodaj pozycję do listy</button>
    </div>

    <div class="items-table-container">
      <table class="items-table">
        <thead>
          <tr>
            <th>Nazwa przedmiotu z katalogu</th>
            <th>Cena jednostkowa</th>
            <th>Ilość sztuk</th>
            <th>Suma</th>
            <th>Akcje</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in listItems" :key="item.id">
            <td class="font-bold">{{ item.name }}</td>
            <td>{{ item.price }} {{ item.currency }}</td>
            <td>{{ item.amount }} szt.</td>
            <td class="font-bold text-blue">{{ item.totalPrice }} {{ item.currency }}</td>
            <td>
              <button class="delete-btn" @click="removeItem(item.id)">Usuń</button>
            </td>
          </tr>
          <tr v-if="listItems.length === 0">
            <td colspan="5" class="empty-table">Koszyk jest pusty. Kliknij "+ Dodaj pozycję do listy".</td>
          </tr>
        </tbody>
      </table>
    </div>

    <AddItemToListModal
      :isOpen="showModal"
      :currentTotal="currentTotal"
      :maxBudget="list.maxBudget"
      @close="showModal = false"
      @add-to-list="addItemToList"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AddItemToListModal from './AddItemToListModal.vue'

const props = defineProps({
  list: {
    type: Object,
    required: true
  }
})

defineEmits(['back'])

const showModal = ref(false)
const listItems = ref([])

const fetchListItems = async () => {
  try {
    const response = await fetch(`http://localhost:8080/api/lists/${props.list.id}/items`)
    if (!response.ok) throw new Error('Błąd sieci')
    const data = await response.json()
    listItems.value = data.map(item => ({
      ...item,
      id: item.line_item_id,
      amount: item.amount,
      totalPrice: item.total_price
    }))
  } catch (error) {
    console.error("Błąd pobierania przedmiotów:", error)
  }
}

const addItemToList = async (newItem) => {
  try {
    const response = await fetch(`http://localhost:8080/api/lists/${props.list.id}/items?item_id=${newItem.id}&ammount=${newItem.amount}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    })

    if (!response.ok) throw new Error('Nie udało się dodać przedmiotu')

    await fetchListItems()
    alert('Przedmiot dodany!')
  } catch (error) {
    console.error("Błąd dodawania:", error)
  }
}

const removeItem = async (id) => {
  if (!confirm('Czy na pewno chcesz usunąć tę pozycję z koszyka?')) {
    return;
  }

  try {
    const response = await fetch(`http://localhost:8080/api/lists/items/${id}`, {
      method: 'DELETE',
    })

    if (!response.ok) throw new Error('Błąd serwera podczas usuwania')

    await fetchListItems()

  } catch (error) {
    console.error("Błąd podczas usuwania przedmiotu:", error)
    alert("Wystąpił błąd. Nie udało się usunąć przedmiotu.")
  }
}

const currentTotal = computed(() => {
  return listItems.value.reduce((sum, item) => sum + item.totalPrice, 0)
})

onMounted(() => {
  fetchListItems()
})
</script>

<style scoped>
.list-details { color: #ffffff; padding: 1vw 0; animation: fadeIn 0.3s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(1vh); } to { opacity: 1; transform: translateY(0); } }

.back-btn { background: none; border: none; color: #93c5fd; cursor: pointer; font-size: 1vw; margin-bottom: 2vh; font-weight: 700; transition: color 0.2s; }
.back-btn:hover { color: #ffffff; }

.list-details__header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4vh; }
.list-details__title { font-size: 2vw; color: #bfdbfe; margin: 0 0 0.5vh 0; }
.list-details__subtitle { color: rgba(226, 232, 240, 0.6); margin: 0; font-size: 1vw; font-weight: 600; }

.add-item-btn { padding: 0.8vw 1.5vw; background: linear-gradient(135deg, #3b82f6, #2563eb); border: none; border-radius: 0.8vw; color: white; font-weight: 700; cursor: pointer; font-size: 0.95vw; box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3); transition: all 0.2s; }
.add-item-btn:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4); }

.items-table-container { background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(148, 163, 184, 0.15); border-radius: 1vw; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }
.items-table { width: 100%; border-collapse: collapse; text-align: left; font-size: 0.95vw; }
.items-table th, .items-table td { padding: 1.2vw; border-bottom: 1px solid rgba(148, 163, 184, 0.1); }
.items-table th { background: rgba(30, 41, 59, 0.8); color: #93c5fd; font-weight: 700; text-transform: uppercase; font-size: 0.75vw; letter-spacing: 0.05em; }
.items-table tr:hover { background: rgba(30, 41, 59, 0.4); }

.font-bold { font-weight: 700; }
.text-blue { color: #60a5fa; }
.empty-table { text-align: center; color: rgba(226, 232, 240, 0.5); padding: 4vw; font-style: italic; }

.delete-btn { background: rgba(239, 68, 68, 0.15); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.3); padding: 0.4vw 0.8vw; border-radius: 0.4vw; font-size: 0.8vw; font-weight: 700; cursor: pointer; transition: all 0.2s; }
.delete-btn:hover { background: rgba(239, 68, 68, 0.3); }
</style>