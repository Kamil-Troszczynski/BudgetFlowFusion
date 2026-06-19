<template>
  <div class="requests-container">
    <template v-if="!activeRequest">
      <div class="requests-section">
        
        <div class="requests-filter-bar">
          <div class="filter-group-item">
            <label class="sort-label">Sekcja Koła:</label>
            <select v-model="selectedSectionFilter" class="excel-sort-select section-filter-dropdown">
              <option value="">Wszystkie sekcje</option>
              <option v-for="section in uniqueSections" :key="section" :value="section">
                {{ section }}
              </option>
            </select>
          </div>

          <div class="filter-group-item">
            <label class="sort-label">Sortuj:</label>
            <select v-model="sortBy" class="excel-sort-select">
              <option value="date-created-desc">Data utworzenia: od najnowszych</option>
              <option value="date-created-asc">Data utworzenia: od najstarszych</option>
              <option value="date-modified-desc">Ostatnia edycja: od najnowszych</option>
              <option value="budget-desc">Budżet wniosku: malejąco</option>
              <option value="budget-asc">Budżet wniosku: rosnąco</option>
              <option value="gross-desc">Suma koszyka brutto: malejąco</option>
              <option value="gross-asc">Suma koszyka brutto: rosnąco</option>
            </select>
          </div>

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

        <div class="requests-header">
          <div class="requests-title-section">
            <h2 class="requests-title">Wnioski o zamówienie</h2>
            <p class="requests-subtitle">Wykaz wszystkich wniosków zakupowych w organizacji</p>
          </div>
          <button class="requests-add-button" @click="openAddRequestModal">+ Nowy wniosek</button>
        </div>

        <div v-for="group in aggregatedRequestGroups" :key="group.key" class="request-status-group">
          <h3 class="status-group-title">{{ group.title }} ({{ group.items.length }})</h3>
          
          <div v-if="group.items.length === 0" class="requests-empty requests-empty--compact">
            <p class="requests-empty-subtext">Brak wniosków w tej sekcji statusu</p>
          </div>

          <template v-else>
            <div v-if="currentLayout === 'grid'" class="requests-grid">
              <div v-for="request in group.items" :key="request.id" class="request-card">
                <div class="request-card__header">
                  <div>
                    <h3 class="request-card__title">{{ request.name }}</h3>
                    <span v-if="request.sectionName" class="request-card__section-badge">{{ request.sectionName }}</span>
                  </div>
                  <span class="request-card__badge" :class="request.status">
                    {{ formatStatus(request.status) }}
                  </span>
                </div>
                <div class="request-card__content">
                  <p class="request-card__detail">
                    <span class="request-card__label">Budżet wniosku:</span>
                    <span class="request-card__value text-blue font-bold">{{ formatMoney(request.budget) }} PLN</span>
                  </p>
                  <p class="request-card__detail">
                    <span class="request-card__label">Suma koszyka Brutto:</span>
                    <span class="request-card__value text-blue font-bold">{{ formatMoney(request.sourceList__totalPrice ?? request.budget) }} PLN</span>
                  </p>
                  <p class="request-card__detail">
                    <span class="request-card__label">Sklepy:</span>
                    <span class="request-card__value text-white">{{ request.sourceList__shopCount ?? 0 }}</span>
                  </p>
                  <p class="request-card__detail">
                    <span class="request-card__label">Utworzył (Skarbnik):</span>
                    <span class="request-card__value text-white font-bold">{{ request.creatorName || 'Nieznany' }}</span>
                  </p>
                  <p class="request-card__detail">
                    <span class="request-card__label">Utworzono:</span>
                    <span class="request-card__value text-white">{{ formatRelativeTime(request.created_at) }}</span>
                  </p>
                  <p class="request-card__detail">
                    <span class="request-card__label">Ostatnia edycja:</span>
                    <span class="request-card__value text-emerald font-bold">{{ formatRelativeTime(request.updated_at || request.created_at) }}</span>
                  </p>
                </div>
                <div class="request-card__actions">
                  <button class="request-card__button view" @click="emit('open-shopping', request)">Otwórz koszyk</button>
                  <button v-if="isOwner(request) && request.status === 'pending'" class="request-card__button view" @click="openEditRequestModal(request)">Edytuj szczegóły</button>
                  <!-- pending → przenieś do dokończenia -->
                  <button
                    v-if="request.status === 'pending' && isOwner(request) && Number(request.sourceList__shopCount || 0) > 0"
                    class="request-card__button finalize"
                    @click="moveToDoDokonczenia(request)"
                  >Przenieś do dokończenia</button>
                  <!-- prepared → zatwierdź (otwiera modal finalizacji) -->
                  <button
                    v-if="request.status === 'prepared' && isOwner(request)"
                    class="request-card__button approve"
                    @click="prepareFinalization(request)"
                  >Zatwierdź</button>
                  <!-- prepared → odrzuć -->
                  <button
                    v-if="request.status === 'prepared' && isOwner(request)"
                    class="request-card__button reject-btn"
                    @click="rejectRequest(request)"
                  >Odrzuć</button>
                  <button v-if="canReturnToOpen(request)" class="request-card__button reopen" @click="returnToOpen(request)">Przywróć do otwartych</button>
                  <button class="request-card__button view" @click="activeRequest = request">Podsumowanie</button>
                  <button v-if="isOwner(request)" class="request-card__button delete" @click="deleteRequest(request.id)">Usuń</button>
                </div>
              </div>
            </div>

            <div v-else class="excel-table-wrapper custom-scrollbar">
              <table class="excel-list-table">
                <thead>
                  <tr>
                    <th>Nazwa wniosku</th>
                    <th>Sekcja koła</th>
                    <th>Status</th>
                    <th>Budżet</th>
                    <th>Suma Brutto</th>
                    <th>Sklepy</th>
                    <th>Utworzył (Skarbnik)</th>
                    <th>Utworzono</th>
                    <th>Ostatnia edycja</th>
                    <th>Akcje</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="request in group.items" :key="request.id">
                    <td class="font-bold text-white">{{ request.name }}</td>
                    <td><span class="table-section-badge">{{ request.sectionName || '-' }}</span></td>
                    <td><span class="request-card__badge text-badge-only" :class="request.status">{{ formatStatus(request.status) }}</span></td>
                    <td class="font-mono text-blue font-bold">{{ formatMoney(request.budget) }} PLN</td>
                    <td class="font-mono text-blue font-bold">{{ formatMoney(request.sourceList__totalPrice ?? request.budget) }} PLN</td>
                    <td>{{ request.sourceList__shopCount ?? 0 }}</td>
                    <td class="font-bold text-white">{{ request.creatorName || 'Nieznany' }}</td>
                    <td>{{ formatDate(request.created_at) }}</td>
                    <td>{{ formatRelativeTime(request.updated_at || request.created_at) }}</td>
                    <td>
                      <div class="table-row-actions">
                        <button class="table-btn view" @click="emit('open-shopping', request)">Lista</button>
                        <button v-if="isOwner(request) && request.status === 'pending'" class="table-btn view" @click="openEditRequestModal(request)">Edytuj</button>
                        <!-- pending → przenieś do dokończenia -->
                        <button
                          v-if="request.status === 'pending' && isOwner(request) && Number(request.sourceList__shopCount || 0) > 0"
                          class="table-btn finalize"
                          @click="moveToDoDokonczenia(request)"
                        >Do dokończenia</button>
                        <!-- prepared → zatwierdź -->
                        <button
                          v-if="request.status === 'prepared' && isOwner(request)"
                          class="table-btn approve"
                          @click="prepareFinalization(request)"
                        >Zatwierdź</button>
                        <!-- prepared → odrzuć -->
                        <button
                          v-if="request.status === 'prepared' && isOwner(request)"
                          class="table-btn reject-btn"
                          @click="rejectRequest(request)"
                        >Odrzuć</button>
                        <button v-if="canReturnToOpen(request)" class="table-btn reopen" @click="returnToOpen(request)">Otwórz</button>
                        <button class="table-btn view" @click="activeRequest = request">Podsumowanie</button>
                        <button v-if="isOwner(request)" class="table-btn delete" @click="deleteRequest(request.id)">Usuń</button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </template>
        </div>
      </div>
    </template>

    <div v-else class="requests-section">
      <button class="request-details__back" @click="activeRequest = null">
        ← Powrót
      </button>

      <div class="request-details__card">
        <div class="request-details__top">
          <div>
            <h2 class="request-details__title">{{ activeRequest.name }}</h2>
            <p class="request-details__subtitle">Wniosek o zamówienie #{{ activeRequest.id }}</p>
          </div>
          <span class="request-card__badge" :class="activeRequest.status">
            {{ formatStatus(activeRequest.status) }}
          </span>
        </div>

        <div class="request-details__grid">
          <div class="request-info">
            <p>Kwota wniosku</p>
            <strong class="text-blue">{{ formatMoney(activeRequest.budget) }} PLN</strong>
          </div>
          <div v-if="activeRequest.sourceList" class="request-info">
            <p>Utworzony z zamówienia</p>
            <strong>{{ activeRequest.sourceList.name }}</strong>
          </div>
          <div class="request-info">
            <p>Dofinansowanie</p>
            <strong>{{ activeRequest.fundingName || 'Brak' }}</strong>
          </div>
          <div class="request-info">
            <p>Sekcja Koła</p>
            <strong class="text-amber">{{ activeRequest.sectionName || 'Brak przypisania' }}</strong>
          </div>
          <div class="request-info">
            <p>Utworzył (Skarbnik)</p>
            <strong>{{ activeRequest.creatorName || 'Nieznany' }}</strong>
          </div>
          <div class="request-info">
            <p>Typ wniosku</p>
            <strong>{{ activeRequest.ifService ? 'Usługa' : 'Produkt' }}</strong>
          </div>
          <div class="request-info">
            <p>Data utworzenia</p>
            <strong>{{ formatDate(activeRequest.created_at) }}</strong>
          </div>
          <div class="request-info">
            <p>Kod CPV</p>
            <strong class="font-mono">
              {{ activeRequest.planPositions?.length ? activeRequest.planPositions.map(requestPlanPositionLabel).join(', ') : (activeRequest.used_cpv_id || 'Brak') }}
            </strong>
          </div>
          <div class="request-info">
            <p>Zgodność z planem ZP</p>
            <strong>{{ formatPlanStatus(activeRequest.planComplianceStatus) }}</strong>
          </div>
          <div v-if="activeRequest.finalizationStatus === 'finalized'" class="request-info">
            <p>Nazwa na dokumencie</p>
            <strong>{{ activeRequest.documentRequestName || activeRequest.name }}</strong>
          </div>
          <div v-if="activeRequest.finalizationStatus === 'finalized'" class="request-info">
            <p>Data ustalenia wartości</p>
            <strong>{{ formatDate(activeRequest.contractValueDate) }}</strong>
          </div>
          <div v-if="activeRequest.finalizationStatus === 'finalized'" class="request-info">
            <p>Kurs euro</p>
            <strong>{{ formatMoney(activeRequest.euroExchangeRate) }}</strong>
          </div>
          <div v-if="activeRequest.finalizationStatus === 'finalized'" class="request-info">
            <p>Główny CPV</p>
            <strong class="font-mono">{{ activeRequest.mainCpvCode || '-' }}</strong>
          </div>
          <div v-if="activeRequest.finalizationStatus === 'finalized'" class="request-info">
            <p>Suma netto CPV</p>
            <strong class="text-emerald">{{ formatMoney(activeRequest.finalNetTotal) }} PLN</strong>
          </div>
          <div v-if="activeRequest.finalizationStatus === 'finalized'" class="request-info">
            <p>Suma brutto finalna</p>
            <strong class="text-blue">{{ formatMoney(activeRequest.finalGrossTotal) }} PLN</strong>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showAddRequestModal" class="modal-overlay" @click="showAddRequestModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2 class="modal-title">{{ editingRequestId ? 'Edycja wniosku o zamówienie' : 'Nowy wniosek o zamówienie' }}</h2>
          <button class="modal-close" @click="showAddRequestModal = false">✕</button>
        </div>
        <form class="modal-form" @submit.prevent="handleNewRequest">
          <div class="modal-form__scroll-container custom-scrollbar">
            <div class="modal-form__group">
              <label class="modal-form__label">Nazwa wniosku</label>
              <input
                v-model="newRequestData.purchase_request_name"
                type="text"
                placeholder="np. Zakup elektroniki"
                class="modal-form__input"
                required
              />
            </div>

            <div v-if="!editingRequestId" class="modal-form__group">
              <label class="modal-form__label">Sekcja koła</label>
              <select
                v-model="newRequestData.section_name"
                class="modal-form__input"
                required
              >
                <option value="" disabled>Wybierz sekcję koła...</option>
                <option v-for="section in uniqueSections" :key="section" :value="section">
                  {{ section }}
                </option>
              </select>
            </div>

            <div v-if="false" class="modal-form__group">
              <label class="modal-form__label">Finansowanie</label>
              <div class="funding-allocation-row">
                <select v-model.number="allocationDraft.funding_id" class="modal-form__input">
                  <option value="" disabled>Wybierz dofinansowanie...</option>
                  <option
                    v-for="funding in fundings"
                    :key="funding.funding_id"
                    :value="funding.funding_id"
                  >
                    {{ funding.funding_name }} (dostepne: {{ formatMoney(funding.available_after_purchase_requests) }} PLN)
                  </option>
                </select>
                <input
                  v-model.number="allocationDraft.allocated_amount"
                  type="number"
                  min="0.01"
                  step="0.01"
                  placeholder="Kwota"
                  class="modal-form__input"
                />
                <button type="button" class="modal-btn modal-btn-save-add" @click="addFundingAllocation">Dodaj</button>
              </div>
              <div v-if="newRequestData.funding_allocations.length > 0" class="funding-allocation-list">
                <div
                  v-for="allocation in newRequestData.funding_allocations"
                  :key="allocation.funding_id"
                  class="funding-allocation-item"
                >
                  <span>{{ fundingName(allocation.funding_id) }}</span>
                  <strong>{{ formatMoney(allocation.allocated_amount) }} PLN</strong>
                  <button type="button" class="delete-inline-btn" @click="removeFundingAllocation(allocation.funding_id)">Usun</button>
                  <div class="plan-position-picker">
                    <select v-model.number="allocation.plan_position_draft_id" class="modal-form__input">
                      <option value="" disabled>Wybierz CPV z planu...</option>
                      <option
                        v-for="position in planOptionsForFunding(allocation.funding_id)"
                        :key="position.public_purchase_plan_id"
                        :value="position.public_purchase_plan_id"
                      >
                        {{ cpvOptionLabel(position) }} - pozostalo {{ formatMoney(position.remaining_amount) }} PLN
                      </option>
                    </select>
                    <input
                      v-model.number="allocation.plan_position_draft_amount"
                      type="number"
                      min="0.01"
                      step="0.01"
                      placeholder="Kwota CPV"
                      class="modal-form__input"
                    />
                    <button type="button" class="modal-btn modal-btn-save-add" @click="addPlanPositionForFunding(allocation)">Dodaj CPV</button>
                  </div>
                  <div v-if="planPositionsForFunding(allocation.funding_id).length" class="plan-position-list">
                    <div
                      v-for="position in planPositionsForFunding(allocation.funding_id)"
                      :key="position.public_purchase_plan_id"
                      class="plan-position-item"
                    >
                      <span>{{ planPositionLabel(position.public_purchase_plan_id) }}</span>
                      <strong>{{ formatMoney(position.allocated_amount) }} PLN</strong>
                      <button type="button" class="delete-inline-btn" @click="removePlanPosition(position.public_purchase_plan_id)">Usun</button>
                    </div>
                  </div>
                </div>
                <div class="funding-allocation-total">
                  <span>Razem</span>
                  <strong>{{ formatMoney(allocationTotal) }} PLN</strong>
                </div>
              </div>
              <p v-else class="modal-form__hint">Dodaj przynajmniej jedno zrodlo finansowania.</p>
            </div>
            <div v-if="editingRequestId" class="modal-form__group">
              <label class="modal-form__label">CPV koszykow</label>
              <button type="button" class="modal-btn modal-btn-save-add cpv-editor-open" @click="openCpvEditorModal">
                Edytuj CPV koszykow
              </button>
              <p class="modal-form__hint">
                {{ basketSummaryRows.length }} pozycji CPV, {{ formatMoney(basketGrossTotal) }} PLN brutto z koszykow.
              </p>
            </div>
            <div v-if="false" class="modal-form__group">
              <label class="modal-form__label">Pozycja planu zamówień publicznych</label>
              <select
                v-model="newRequestData.public_purchase_plan_id"
                class="modal-form__input"
              >
                <option :value="null">Brak pozycji w planie</option>
                <option
                  v-for="position in matchingPlanPositions"
                  :key="position.public_purchase_plan_id"
                  :value="position.public_purchase_plan_id"
                >
                  {{ cpvOptionLabel(position) }} - pozostalo {{ formatMoney(position.remaining_amount) }} PLN
                </option>
              </select>
            </div>
          </div>
          <section v-if="false" class="finalization-section">
            <h3>Podsumowanie sklepów do rozliczeń</h3>
            <div class="excel-table-wrapper custom-scrollbar">
              <table class="excel-list-table finalization-table">
                <thead>
                  <tr>
                    <th>Sklep</th>
                    <th>Opis zakupów</th>
                    <th>Rozeznanie rynku</th>
                    <th>Komentarz</th>
                    <th>Kwota brutto</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="line in settlementLines" :key="line.settlement_line_id || line.shop_purchase_list_id">
                    <td><input v-model="line.shop_name" class="modal-form__input settlement-line-input" type="text" /></td>
                    <td><textarea v-model="line.purchase_description" class="modal-form__input settlement-line-textarea"></textarea></td>
                    <td>
                      <span v-if="line.market_research_required" class="market-research-file">
                        {{ line.market_research_file_name || 'Brak załącznika' }}
                      </span>
                      <span v-else>-</span>
                    </td>
                    <td>
                      <textarea
                        v-if="line.market_research_required"
                        :value="line.market_research_comment || 'Brak komentarza'"
                        class="modal-form__input settlement-line-textarea"
                        readonly
                      ></textarea>
                      <span v-else>-</span>
                    </td>
                    <td><input v-model.number="line.planned_gross_amount" class="modal-form__input settlement-line-input" type="number" min="0" step="0.01" /></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>

          <section v-if="false" class="finalization-section">
            <h3>Końcowe podsumowanie</h3>
            <div class="finalization-totals">
              <div>
                <span>Status po zatwierdzeniu</span>
                <strong>Oczekuje na akceptację księgowości</strong>
              </div>
              <div>
                <span>Dokumenty</span>
                <strong>Eksport PDF/XLSX będzie dostępny później</strong>
              </div>
            </div>
          </section>

          <section v-if="false" class="finalization-section">
            <h3>Podsumowanie sklepow do ksiegowosci</h3>
            <div class="excel-table-wrapper custom-scrollbar">
              <table class="excel-list-table finalization-table">
                <thead>
                  <tr>
                    <th>Sklep</th>
                    <th>Opis zakupow</th>
                    <th>Kwota brutto</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="line in settlementLines" :key="line.settlement_line_id || line.shop_purchase_list_id">
                    <td><input v-model="line.shop_name" class="modal-form__input settlement-line-input" type="text" /></td>
                    <td><textarea v-model="line.purchase_description" class="modal-form__input settlement-line-textarea"></textarea></td>
                    <td><input v-model.number="line.planned_gross_amount" class="modal-form__input settlement-line-input" type="number" min="0" step="0.01" /></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>

          <section v-if="false" class="finalization-section">
            <h3>Koncowe podsumowanie</h3>
            <div class="finalization-totals">
              <div>
                <span>Status po zatwierdzeniu</span>
                <strong>Oczekuje na akceptacje ksiegowosci</strong>
              </div>
              <div>
                <span>Dokumenty</span>
                <strong>Eksport PDF/XLSX bedzie dostepny pozniej</strong>
              </div>
            </div>
          </section>

          <section v-if="showFinalizationModal" class="finalization-section">
            <h3>Podsumowanie sklepow do ksiegowosci</h3>
            <div class="excel-table-wrapper custom-scrollbar">
              <table class="excel-list-table finalization-table">
                <thead>
                  <tr>
                    <th>Sklep</th>
                    <th>Opis zakupow</th>
                    <th>Kwota brutto</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="line in settlementLines" :key="line.settlement_line_id || line.shop_purchase_list_id">
                    <td><input v-model="line.shop_name" class="modal-form__input settlement-line-input" type="text" /></td>
                    <td><textarea v-model="line.purchase_description" class="modal-form__input settlement-line-textarea"></textarea></td>
                    <td><input v-model.number="line.planned_gross_amount" class="modal-form__input settlement-line-input" type="number" min="0" step="0.01" /></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>

          <section v-if="showFinalizationModal" class="finalization-section">
            <h3>Koncowe podsumowanie</h3>
            <div class="finalization-totals">
              <div>
                <span>Status po zatwierdzeniu</span>
                <strong>Oczekuje na akceptacje ksiegowosci</strong>
              </div>
              <div>
                <span>Dokumenty</span>
                <strong>Eksport PDF/XLSX bedzie dostepny pozniej</strong>
              </div>
            </div>
          </section>

          <div class="modal-actions">
            <button type="button" class="modal-btn modal-btn-cancel" @click="showAddRequestModal = false">Anuluj</button>
            <button type="submit" :class="editingRequestId ? 'modal-btn modal-btn-finish' : 'modal-btn modal-btn-save'" :disabled="editingRequestId && allocationTotal <= 0">
              {{ editingRequestId ? 'Zakończ edycję' : 'Złóż wniosek' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="showCpvEditorModal" class="modal-overlay" @click="showCpvEditorModal = false">
      <div class="modal-content cpv-modal-content" @click.stop>
        <div class="modal-header">
          <h2 class="modal-title">CPV koszykow</h2>
          <button class="modal-close" @click="showCpvEditorModal = false">x</button>
        </div>
        <div class="cpv-editor custom-scrollbar">
          <div class="cpv-main-funding">
            <label class="modal-form__label">Finansowanie glówne</label>
            <select v-model.number="newRequestData.funding_id" class="modal-form__input">
              <option value="" disabled>Wybierz finansowanie glówne...</option>
              <option v-for="funding in projectFundings" :key="funding.funding_id" :value="funding.funding_id">
                {{ funding.funding_name }} ({{ formatMoney(funding.available_after_purchase_requests) }} PLN)
              </option>
            </select>
          </div>
          <div v-if="requestBaskets.length === 0" class="requests-empty requests-empty--compact">
            <p class="requests-empty-subtext">Brak koszykow przypisanych do tego wniosku</p>
          </div>
          <div v-for="basket in requestBaskets" :key="basket.shop_purchase_list_id" class="cpv-basket">
            <div class="cpv-basket__top">
              <div>
                <h3>{{ basket.shop_name || basket.name || `Koszyk #${basket.shop_purchase_list_id}` }}</h3>
                <p>{{ fundingName(effectiveBasketFundingId(basket)) }} - brutto {{ formatMoney(basket.total_price) }} PLN - netto {{ formatMoney(basket.total_net) }} PLN</p>
              </div>
              <div class="cpv-mode-toggle">
                <button type="button" :class="{ active: basket.cpv_mode === 'single' }" @click="basket.cpv_mode = 'single'">Jedno</button>
                <button type="button" :class="{ active: basket.cpv_mode === 'split' }" @click="basket.cpv_mode = 'split'">Dzielone</button>
              </div>
            </div>

            <div v-if="basket.cpv_mode === 'single'" class="cpv-single-row">
                <select v-model.number="basket.single_plan_id" class="modal-form__input">
                  <option value="" disabled>Wybierz CPV z planu finansowania...</option>
                  <option
                    v-for="position in planOptionsForFunding(newRequestData.funding_id)"
                    :key="position.public_purchase_plan_id"
                    :value="position.public_purchase_plan_id"
                  >
                  {{ cpvOptionLabel(position) }} - pozostalo netto {{ formatMoney(position.remaining_amount) }} PLN
                </option>
              </select>
            </div>

            <div v-else class="cpv-split">
              <div
                v-for="(row, index) in basket.split_rows"
                :key="index"
                class="cpv-split-row"
              >
                <select v-model.number="row.funding_id" class="modal-form__input">
                  <option value="" disabled>Finansowanie...</option>
                  <option v-for="funding in projectFundings" :key="funding.funding_id" :value="funding.funding_id">
                    {{ funding.funding_name }}
                  </option>
                </select>
                <select v-model.number="row.public_purchase_plan_id" class="modal-form__input">
                  <option value="" disabled>CPV...</option>
                  <option
                    v-for="position in planOptionsForFunding(row.funding_id)"
                    :key="position.public_purchase_plan_id"
                    :value="position.public_purchase_plan_id"
                  >
                    {{ cpvOptionLabel(position) }} - pozostalo netto {{ formatMoney(position.remaining_amount) }} PLN
                  </option>
                </select>
                <input
                  v-model.number="row.allocated_amount"
                  type="number"
                  min="0.01"
                  step="0.01"
                  placeholder="Kwota netto"
                  class="modal-form__input"
                />
                <button type="button" class="delete-inline-btn" @click="removeBasketSplitRow(basket, index)">Usun</button>
              </div>
              <button type="button" class="modal-btn modal-btn-save-add" @click="addBasketSplitRow(basket)">Dodaj zrodlo</button>
            </div>
          </div>

          <div class="cpv-summary">
            <h3>Podsumowanie</h3>
            <div class="excel-table-wrapper custom-scrollbar">
              <table class="excel-list-table cpv-summary-table">
                <thead>
                  <tr>
                    <th>Sklep</th>
                    <th>Zrodlo finansowania</th>
                    <th>CPV</th>
                    <th>Kwota koszyka brutto</th>
                    <th>Kwota CPV netto</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="row in basketSummaryRows" :key="row.key">
                    <td>{{ row.shopName }}</td>
                    <td>{{ row.fundingName }}</td>
                    <td>
                      <div class="font-mono">{{ row.cpvCode || '-' }}</div>
                      <small v-if="row.cpvDetails">{{ row.cpvDetails }}</small>
                    </td>
                    <td class="font-mono text-blue">{{ formatMoney(row.grossAmount) }} PLN</td>
                    <td class="font-mono text-emerald">{{ formatMoney(row.netAmount) }} PLN</td>
                  </tr>
                </tbody>
                <tfoot>
                  <tr>
                    <td colspan="3">Razem</td>
                    <td class="font-mono text-blue">{{ formatMoney(basketGrossTotal) }} PLN</td>
                    <td class="font-mono text-emerald">{{ formatMoney(basketNetAssignedTotal) }} PLN</td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </div>
        </div>
        <div class="modal-actions">
          <button type="button" class="modal-btn modal-btn-cancel" @click="showCpvEditorModal = false">Zamknij</button>
          <button type="button" class="modal-btn modal-btn-save" :disabled="finalizationSaving" @click="saveCpvEditorChanges">Zapisz CPV</button>
        </div>
      </div>
    </div>

    <div v-if="showFinalizationModal" class="modal-overlay">
      <div class="modal-content finalization-modal-content" @click.stop>
        <div class="modal-header">
          <h2 class="modal-title">Finalizacja wniosku</h2>
          <button class="modal-close" @click="showFinalizationModal = false">x</button>
        </div>
        <div v-if="finalizationLoading" class="requests-empty requests-empty--compact">
          <p class="requests-empty-subtext">Przygotowywanie podsumowania...</p>
        </div>
        <form v-else class="finalization-editor custom-scrollbar" @submit.prevent="saveFinalization">
          <div class="finalization-grid">
            <label class="modal-form__group">
              <span class="modal-form__label">Nazwa wniosku na dokumencie</span>
              <input v-model="finalizationForm.document_request_name" class="modal-form__input" type="text" required />
            </label>
            <label class="modal-form__group">
              <span class="modal-form__label">Kurs euro dla ZP</span>
              <input v-model.number="finalizationForm.euro_exchange_rate" class="modal-form__input" type="number" min="0.0001" step="0.0001" required />
            </label>
            <label class="modal-form__group">
              <span class="modal-form__label">Data ustalenia wartości</span>
              <input v-model="finalizationForm.contract_value_date" class="modal-form__input" type="date" required />
            </label>
            <div class="modal-form__group finalization-cpv-shortcut">
              <span class="modal-form__label">CPV koszyków</span>
              <button type="button" class="modal-btn modal-btn-save-add" @click="openCpvEditorModal">
                Edytuj CPV koszyków
              </button>
            
            </div>
          </div>
<section class="finalization-section">
            <h3>Podsumowanie sklepów na wniosku</h3>
            <div class="excel-table-wrapper custom-scrollbar">
              <table class="excel-list-table finalization-table">
                <thead>
                  <tr>
                    <th>Sklep</th>
                    <th>Opis zakupów</th>
                    <th>Badanie rynku</th>
                    <th>Komentarz</th>
                    <th>Ostateczna kwota brutto</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="line in settlementLines" :key="line.settlement_line_id || line.shop_purchase_list_id">
                    <td><input v-model="line.shop_name" class="modal-form__input settlement-line-input" type="text" /></td>
                    <td><textarea v-model="line.purchase_description" class="modal-form__input settlement-line-textarea"></textarea></td>
                    <td>
                      <span v-if="line.market_research_required" class="market-research-file">
                        {{ line.market_research_file_name || 'Brak załącznika' }}
                      </span>
                      <span v-else>-</span>
                    </td>
                    <td>
                      <textarea
                        v-if="line.market_research_required"
                        :value="line.market_research_comment || 'Brak komentarza'"
                        class="modal-form__input settlement-line-textarea"
                        readonly
                      ></textarea>
                      <span v-else>-</span>
                    </td>
                    <td><input v-model.number="line.planned_gross_amount" class="modal-form__input settlement-line-input" type="number" min="0" step="0.01" /></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>


<section class="finalization-section finalization-plan-summary">
            <div class="finalization-section__header">
              <div>
                <h3>Podsumowanie planu</h3>
                <p>Koszyki, CPV, finansowanie i ręcznie poprawione kwoty w jednym miejscu.</p>
              </div>
              <div class="plan-summary-toggle">
                <button
                  type="button"
                  :class="{ active: finalizationPlanSummaryLayout === 'cards' }"
                  @click="finalizationPlanSummaryLayout = 'cards'"
                >
                  Kafelki
                </button>
                <button
                  type="button"
                  :class="{ active: finalizationPlanSummaryLayout === 'list' }"
                  @click="finalizationPlanSummaryLayout = 'list'"
                >
                  Lista
                </button>
              </div>
            </div>
            <div class="plan-summary-metrics">
              <div>
                <span>Brutto z planu</span>
                <strong>{{ formatMoney(finalizationSummary?.gross_total) }} PLN</strong>
              </div>
              <div>
                <span>Brutto po korektach</span>
                <strong>{{ formatMoney(finalizationCorrectedGrossTotal) }} PLN</strong>
              </div>
              <div>
                <span>Netto CPV</span>
                <strong>{{ formatMoney(finalizationCorrectedNetTotal) }} PLN</strong>
              </div>
              <div>
                <span>Główny CPV</span>
                <strong class="font-mono">{{ finalizationSummary?.main_cpv_code || '-' }}</strong>
              </div>
            </div>
            <div v-if="finalizationPlanSummaryLayout === 'cards'" class="plan-summary-list">
              <article
                v-for="basket in finalizationPlanSummaryRows"
                :key="basket.key"
                class="plan-summary-card"
              >
                <div class="plan-summary-card__top">
                  <div>
                    <h4>{{ basket.shopName }}</h4>
                    <p>{{ basket.purchaseDescription || 'Brak opisu zakupów' }}</p>
                  </div>
                  <span
                    class="plan-summary-card__badge"
                    :class="{ 'plan-summary-card__badge--changed': basket.hasManualCorrection }"
                  >
                    {{ basket.hasManualCorrection ? 'Kwota poprawiona' : 'Kwota z koszyka' }}
                  </span>
                </div>

                <div class="plan-summary-card__amounts">
                  <div>
                    <span>Z koszyka</span>
                    <strong>{{ formatMoney(basket.calculatedGrossAmount) }} PLN</strong>
                  </div>
                  <div>
                    <span>W finalizacji</span>
                    <strong>{{ formatMoney(basket.plannedGrossAmount) }} PLN</strong>
                  </div>
                  <div>
                    <span>Różnica</span>
                    <strong :class="basket.correctionAmount === 0 ? 'text-muted' : (basket.correctionAmount > 0 ? 'text-blue' : 'text-amber')">
                      {{ formatMoney(basket.correctionAmount) }} PLN
                    </strong>
                  </div>
                </div>

                <div class="plan-summary-cpv-list">
                  <div v-for="row in basket.cpvRows" :key="row.key" class="plan-summary-cpv">
                    <span class="font-mono">{{ row.cpvCode || '-' }}</span>
                    <span>{{ row.planNumber || 'Brak nr planu' }}</span>
                    <span>{{ row.fundingName || 'Brak finansowania' }}</span>
                    <strong>{{ formatMoney(row.netAmount) }} PLN netto</strong>
                  </div>
                  <div v-if="basket.cpvRows.length === 0" class="plan-summary-empty">
                    Brak przypisanych pozycji CPV.
                  </div>
                </div>

                <div v-if="basket.marketResearchRequired" class="plan-summary-research">
                  <span>Rozeznanie: {{ basket.marketResearchFileName || 'brak załącznika' }}</span>
                  <p>{{ basket.marketResearchComment || 'Brak komentarza rozeznania.' }}</p>
                </div>
              </article>
            </div>
            <div v-else class="excel-table-wrapper custom-scrollbar">
              <table class="excel-list-table finalization-table plan-summary-table">
                <thead>
                  <tr>
                    <th>Koszyk</th>
                    <th>CPV / plan / finansowanie</th>
                    <th>Kwota brutto z koszyka</th>
                    <th>Kwota brutto finalna</th>
                    <th>Różnica brutto</th>
                    <th>Rozeznanie</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="basket in finalizationPlanSummaryRows" :key="basket.key">
                    <td>
                      <strong>{{ basket.shopName }}</strong>
                      <small>{{ basket.purchaseDescription || 'Brak opisu zakupów' }}</small>
                    </td>
                    <td>
                      <div v-if="basket.cpvRows.length" class="plan-summary-table-cpv">
                        <span v-for="row in basket.cpvRows" :key="row.key">
                          <strong class="font-mono">{{ row.cpvCode || '-' }}</strong>
                          {{ row.planNumber || 'Brak nr planu' }} · {{ row.fundingName || 'Brak finansowania' }} · {{ formatMoney(row.netAmount) }} PLN netto
                        </span>
                      </div>
                      <span v-else class="text-muted">Brak przypisanych pozycji CPV</span>
                    </td>
                    <td class="font-mono text-blue">{{ formatMoney(basket.calculatedGrossAmount) }} PLN</td>
                    <td class="font-mono text-emerald">{{ formatMoney(basket.plannedGrossAmount) }} PLN</td>
                    <td>
                      <span
                        class="plan-summary-diff"
                        :class="{ changed: basket.hasManualCorrection }"
                      >
                        {{ formatMoney(basket.correctionAmount) }} PLN
                      </span>
                    </td>
                    <td>
                      <span v-if="basket.marketResearchRequired">
                        {{ basket.marketResearchFileName || 'Brak załącznika' }}
                      </span>
                      <span v-else>-</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>

          <section class="finalization-section">
            <h3>CPV i pozycje planu</h3>
            <div class="excel-table-wrapper custom-scrollbar">
              <table class="excel-list-table finalization-table">
                <thead>
                  <tr>
                    <th>Plan</th>
                    <th>Numer planu</th>
                    <th>Odpowiedzialny</th>
                    <th>Organizator</th>
                    <th>Pozycja</th>
                    <th>CPV</th>
                    <th>Plan netto</th>
                    <th>Finalnie netto</th>
                    <th>Finalnie EUR</th>
                    <th>Główny</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="row in finalizationPlanPositionRows" :key="row.public_purchase_plan_id">
                    <td>{{ row.public_plan_list_name || row.plan_name || '-' }}</td>
                    <td>{{ row.plan_number || '-' }}</td>
                    <td>{{ row.fund_responsible_person || row.funding_signing_person || '-' }}</td>
                    <td>{{ row.funding_organizer || '-' }}</td>
                    <td>{{ row.plan_position_number || '-' }}</td>
                    <td class="font-mono">{{ row.cpv_code || '-' }}</td>
                    <td class="font-mono text-blue">{{ formatMoney(row.planned_net_amount) }} PLN</td>
                    <td class="font-mono text-emerald">{{ formatMoney(row.allocated_net_amount) }} PLN</td>
                    <td class="font-mono text-blue">{{ formatMoney(row.allocated_eur_amount) }} EUR</td>
                    <td>{{ row.is_main_cpv ? 'Tak' : '-' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>

          <section class="finalization-section">
            <h3>Kwoty brutto według finansowania</h3>
            <div class="finalization-totals">
              <div>
                <span>Kwota brutto razem</span>
                <strong>{{ formatMoney(finalizationCorrectedGrossTotal) }} PLN</strong>
              </div>
              <div v-for="row in finalizationFundingGrossRows" :key="row.funding_id || row.funding_name">
                <span>{{ row.funding_name ? `Pobrane z: ${row.funding_name}` : 'Brak wybranego finansowania' }}</span>
                <strong>{{ formatMoney(row.gross_amount) }} PLN</strong>
              </div>
            </div>
          </section>

          <section class="finalization-section finalization-remaining-tab">
            <div class="finalization-section__header">
              <div>
                <h3>Pozostanie po wniosku</h3>
                <p>Mały podgląd tego, ile pieniędzy zostanie w każdym finansowaniu po zapisie tego wniosku.</p>
              </div>
            </div>
            <div class="remaining-funding-list">
              <article v-for="row in finalizationFundingRemainingRows" :key="row.funding_id || row.funding_name" class="remaining-funding-card">
                <div>
                  <h4>{{ row.funding_name || 'Brak finansowania' }}</h4>
                  <p>Obecnie dostępne: {{ formatMoney(row.current_available) }} PLN</p>
                </div>
                <strong :class="row.remaining_after < 0 ? 'text-amber' : 'text-emerald'">
                  {{ formatMoney(row.remaining_after) }} PLN
                </strong>
              </article>
              <div v-if="finalizationFundingRemainingRows.length === 0" class="plan-summary-empty">
                Brak danych finansowania do wyświetlenia.
              </div>
            </div>
          </section>

          <section class="finalization-section">
            <h3>Koncowe podsumowanie</h3>
            <div class="finalization-totals">
              <div>
                <span>Status po zatwierdzeniu</span>
                <strong>Oczekuje na akceptacje ksiegowosci</strong>
              </div>
              <div>
                <span>Dokumenty</span>
                <strong>Eksport PDF/XLSX bedzie dostepny pozniej</strong>
              </div>
            </div>
          </section>

          <div class="modal-actions">
            <button type="button" class="modal-btn modal-btn-cancel" :disabled="finalizationSaving" @click="saveFinalizationDraft">Przerwij i dokończ później</button>
            <button type="button" class="modal-btn modal-btn-finish" :disabled="finalizationSaving || finalizationRequest?.finalizationStatus !== 'accounting_pending'" @click="sendToSettlement">Przekaz do rozliczen</button>
            <button type="submit" class="modal-btn modal-btn-save" :disabled="finalizationSaving">
              {{ finalizationSaving ? 'Zapisywanie...' : 'Potwierdź i zakończ' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, watch } from 'vue'
import { useAuth } from '@/composables/useAuth'

const API_URL = 'http://localhost:8080/api'
const { user } = useAuth()
const emit = defineEmits(['budget-changed', 'open-shopping'])
const activeRequest = ref(null)
const showAddRequestModal = ref(false)
const showCpvEditorModal = ref(false)
const showFinalizationModal = ref(false)
const finalizationLoading = ref(false)
const finalizationSaving = ref(false)
const finalizationRequest = ref(null)
const finalizationSummary = ref(null)
const finalizationPlanSummaryLayout = ref('cards')
const settlementLines = ref([])
const finalizationForm = ref({
  document_request_name: '',
  euro_exchange_rate: null,
  contract_value_date: new Date().toISOString().slice(0, 10)
})
const editingRequestId = ref(null)
const sortBy = ref('date-created-desc')
const currentLayout = ref('grid')
const selectedSectionFilter = ref('')

const allRequests = ref([])
const closedOrders = ref([])
const fundings = ref([])
const fundingPlans = ref([])
const allocationDraft = ref({ funding_id: '', allocated_amount: null })
const requestBaskets = ref([])
const studentsMap = ref({})
const VAT_RATE = 1.23

const currentFinanceManagerId = computed(() => {
  return user.value?.projectFinanceManagerId || user.value?.id
})

const newRequestData = ref({
  purchase_request_name: '',
  section_name: '',
  budget_allocated_for_the_order: null,
  if_service: false,
  used_cpv_id: null,
  can_add: true,
  shop_purchase_list_id: '',
  funding_id: '',
  project_budget_id: null,
  funding_allocations: [],
  public_purchase_plan_id: null,
  plan_positions: []
})

const uniqueSections = computed(() => {
  const sectionsSet = new Set()
  fundings.value.forEach(f => {
    if (f.project_budget_name) sectionsSet.add(f.project_budget_name)
  })
  if (sectionsSet.size === 0) {
    return ['Elektronika', 'Konstrukcja', 'Software', 'Aero', 'Marketing']
  }
  return Array.from(sectionsSet)
})

const selectedFunding = computed(() =>
  fundings.value.find(funding => Number(funding.funding_id) === Number(newRequestData.value.funding_id)) || null
)

const projectFundings = computed(() => {
  const projectBudgetId = Number(newRequestData.value.project_budget_id || 0)
  if (!projectBudgetId) return fundings.value
  return fundings.value.filter(
    funding => Number(funding.project_budget_id) === projectBudgetId
  )
})

const allocationTotal = computed(() =>
  newRequestData.value.funding_allocations.reduce(
    (sum, allocation) => sum + Number(allocation.allocated_amount || 0),
    0
  )
)

const basketGrossTotal = computed(() =>
  requestBaskets.value.reduce((sum, basket) => sum + Number(basket.total_price || 0), 0)
)

const basketPlanRows = computed(() =>
  requestBaskets.value.flatMap(basket => {
    if (basket.cpv_mode === 'single') {
      const plan = allPlanPositions.value.find(
        position => Number(position.public_purchase_plan_id) === Number(basket.single_plan_id)
      )
      return plan ? [{
        shop_purchase_list_id: basket.shop_purchase_list_id,
        public_purchase_plan_id: plan.public_purchase_plan_id,
        funding_id: plan.funding_id,
        cpv_code: plan.cpv_code,
        description: plan.description,
        product_category_name: plan.product_category_name,
        allocated_amount: Number(basket.total_net || 0),
        basket
      }] : []
    }
    return (basket.split_rows || []).map(row => {
      const plan = allPlanPositions.value.find(
        position => Number(position.public_purchase_plan_id) === Number(row.public_purchase_plan_id)
      )
      return plan ? {
        shop_purchase_list_id: basket.shop_purchase_list_id,
        public_purchase_plan_id: plan.public_purchase_plan_id,
        funding_id: plan.funding_id,
        cpv_code: plan.cpv_code,
        description: plan.description,
        product_category_name: plan.product_category_name,
        allocated_amount: Number(row.allocated_amount || 0),
        basket
      } : null
    }).filter(Boolean)
  }).filter(row => row.allocated_amount > 0)
)

const basketFundingAllocations = computed(() => {
  const grouped = new Map()
  basketPlanRows.value.forEach(row => {
    const grossAmount = Number(row.allocated_amount || 0) * VAT_RATE
    grouped.set(row.funding_id, (grouped.get(row.funding_id) || 0) + grossAmount)
  })
  return Array.from(grouped.entries()).map(([funding_id, allocated_amount]) => ({
    funding_id,
    allocated_amount
  }))
})

const basketNetAssignedTotal = computed(() =>
  basketPlanRows.value.reduce((sum, row) => sum + Number(row.allocated_amount || 0), 0)
)

const basketSummaryRows = computed(() => {
  const rows = []
  requestBaskets.value.forEach(basket => {
    const assignedRows = basketPlanRows.value.filter(
      row => Number(row.shop_purchase_list_id) === Number(basket.shop_purchase_list_id)
    )
    if (assignedRows.length === 0) {
      rows.push({
        key: `${basket.shop_purchase_list_id}-empty`,
        shopName: basket.shop_name || basket.name || `Koszyk #${basket.shop_purchase_list_id}`,
        fundingName: 'Nieprzypisane',
        cpvCode: '',
        cpvDetails: '',
        grossAmount: basket.total_price || 0,
        netAmount: 0
      })
      return
    }
    assignedRows.forEach(row => {
      rows.push({
        key: `${basket.shop_purchase_list_id}-${row.public_purchase_plan_id}`,
        shopName: basket.shop_name || basket.name || `Koszyk #${basket.shop_purchase_list_id}`,
        fundingName: fundingName(row.funding_id),
        cpvCode: row.cpv_code,
        cpvDetails: [row.description, row.product_category_name].filter(Boolean).join(' - '),
        grossAmount: basket.total_price || 0,
        netAmount: row.allocated_amount || 0
      })
    })
  })
  return rows
})

const finalizationAdjustedSnapshotRows = computed(() => {
  const snapshotRows = finalizationSummary.value?.snapshot_rows || []
  const listNetTotals = snapshotRows.reduce((totals, row) => {
    const listId = row.shop_purchase_list_id || 'none'
    totals[listId] = (totals[listId] || 0) + Number(row.allocated_net_amount || 0)
    return totals
  }, {})
  const finalGrossByList = settlementLines.value.reduce((totals, line) => {
    if (line.shop_purchase_list_id) {
      totals[line.shop_purchase_list_id] = Number(line.planned_gross_amount || 0)
    }
    return totals
  }, {})

  return snapshotRows.map(row => {
    const listId = row.shop_purchase_list_id || 'none'
    const originalListNet = Number(listNetTotals[listId] || 0)
    const originalNet = Number(row.allocated_net_amount || 0)
    const finalGross = finalGrossByList[row.shop_purchase_list_id]
    const adjustedNet = finalGross !== undefined && originalListNet > 0
      ? (finalGross / 1.23) * (originalNet / originalListNet)
      : originalNet
    return {
      ...row,
      allocated_net_amount: adjustedNet,
      allocated_gross_amount: adjustedNet * 1.23
    }
  })
})

const finalizationCpvRows = computed(() => {
  const rate = Number(finalizationForm.value.euro_exchange_rate || 0)
  const totals = finalizationAdjustedSnapshotRows.value.reduce((grouped, row) => {
    const cpv = row.cpv_code || ''
    if (!grouped[cpv]) {
      grouped[cpv] = {
        cpv_code: cpv,
        plan_number: row.plan_number || null,
        allocated_net_amount: 0
      }
    } else if (row.plan_number && !String(grouped[cpv].plan_number || '').includes(row.plan_number)) {
      grouped[cpv].plan_number = [grouped[cpv].plan_number, row.plan_number].filter(Boolean).join(', ')
    }
    grouped[cpv].allocated_net_amount += Number(row.allocated_net_amount || 0)
    return grouped
  }, {})
  const rows = Object.values(totals)
  const mainCpv = rows.length
    ? rows.reduce((max, row) => Number(row.allocated_net_amount || 0) > Number(max.allocated_net_amount || 0) ? row : max, rows[0]).cpv_code
    : null
  return rows.map(row => ({
    ...row,
    allocated_eur_amount: rate > 0 ? Number(row.allocated_net_amount || 0) / rate : 0,
    is_main_cpv: Boolean(mainCpv && row.cpv_code === mainCpv)
  }))
})

const finalizationPlanPositionRows = computed(() => {
  const rate = Number(finalizationForm.value.euro_exchange_rate || 0)
  const cpvRows = finalizationCpvRows.value
  const mainCpv = cpvRows.find(row => row.is_main_cpv)?.cpv_code
  const grouped = finalizationAdjustedSnapshotRows.value.reduce((plans, row) => {
    const planId = row.public_purchase_plan_id
    if (!plans[planId]) {
      plans[planId] = {
        ...row,
        allocated_net_amount: 0
      }
    }
    plans[planId].allocated_net_amount += Number(row.allocated_net_amount || 0)
    return plans
  }, {})
  return Object.values(grouped).map(row => ({
    public_purchase_plan_id: row.public_purchase_plan_id,
    plan_name: row.plan_name,
    public_plan_list_name: row.public_plan_list_name,
    plan_number: row.plan_number,
    fund_responsible_person: row.fund_responsible_person,
    funding_organizer: row.funding_organizer,
    funding_signing_person: row.funding_signing_person,
    plan_position_number: row.plan_position_number,
    cpv_code: row.cpv_code,
    planned_net_amount: row.planned_net_amount,
    allocated_net_amount: row.allocated_net_amount,
    allocated_eur_amount: rate > 0 ? Number(row.allocated_net_amount || 0) / rate : 0,
    is_main_cpv: Boolean(mainCpv && row.cpv_code === mainCpv)
  }))
})

const finalizationCorrectedNetTotal = computed(() =>
  finalizationAdjustedSnapshotRows.value.reduce(
    (sum, row) => sum + Number(row.allocated_net_amount || 0),
    0
  )
)

const finalizationCorrectedGrossTotal = computed(() =>
  settlementLines.value.reduce(
    (sum, line) => sum + Number(line.planned_gross_amount || 0),
    0
  )
)

const finalizationFundingGrossRows = computed(() => {
  const grouped = finalizationAdjustedSnapshotRows.value.reduce((rows, row) => {
    const key = row.funding_id || 'none'
    if (!rows[key]) {
      rows[key] = {
        funding_id: row.funding_id,
        funding_name: row.funding_name,
        gross_amount: 0
      }
    }
    rows[key].gross_amount += Number(row.allocated_gross_amount || 0)
    return rows
  }, {})
  return Object.values(grouped)
})

const finalizationFundingRemainingRows = computed(() => {
  const fundingMap = new Map(
    fundings.value.map(funding => [Number(funding.funding_id), funding])
  )
  return finalizationFundingGrossRows.value.map(row => {
    const funding = fundingMap.get(Number(row.funding_id))
    const currentAvailable = Number(funding?.available_after_purchase_requests ?? 0)
    return {
      funding_id: row.funding_id,
      funding_name: row.funding_name,
      current_available: currentAvailable,
      request_gross: Number(row.gross_amount || 0),
      remaining_after: currentAvailable - Number(row.gross_amount || 0)
    }
  })
})

const finalizationPlanSummaryRows = computed(() => {
  const snapshotRows = finalizationAdjustedSnapshotRows.value
  return settlementLines.value.map(line => {
    const cpvRows = snapshotRows
      .filter(row => Number(row.shop_purchase_list_id) === Number(line.shop_purchase_list_id))
      .map((row, index) => ({
        key: `${line.shop_purchase_list_id || 'extra'}-${row.public_purchase_plan_id || index}-${row.cpv_code || index}`,
        cpvCode: row.cpv_code,
        planNumber: row.plan_number,
        fundingName: row.funding_name,
        netAmount: Number(row.allocated_net_amount || 0)
      }))
    const calculatedGrossAmount = Number(line.calculated_gross_amount ?? line.planned_gross_amount ?? 0)
    const plannedGrossAmount = Number(line.planned_gross_amount || 0)
    return {
      key: line.settlement_line_id || line.shop_purchase_list_id || line.shop_name,
      shopName: line.shop_name || 'Koszyk',
      purchaseDescription: line.purchase_description,
      calculatedGrossAmount,
      plannedGrossAmount,
      correctionAmount: plannedGrossAmount - calculatedGrossAmount,
      hasManualCorrection: Math.abs(plannedGrossAmount - calculatedGrossAmount) >= 0.01,
      marketResearchRequired: line.market_research_required,
      marketResearchComment: line.market_research_comment,
      marketResearchFileName: line.market_research_file_name,
      cpvRows
    }
  })
})

const allPlanPositions = computed(() =>
  fundingPlans.value.flatMap(plan =>
    (plan.public_purchase_plans || []).map(position => ({
      ...position,
      funding_id: plan.funding_id,
      funding_name: plan.funding_name || fundingName(plan.funding_id)
    }))
  )
)

const matchingPlanPositions = computed(() => {
  const cpv = String(newRequestData.value.used_cpv_id || '')
  return allPlanPositions.value.filter(position => String(position.cpv_code || '') === cpv)
})

const selectedPlanPosition = computed(() =>
  matchingPlanPositions.value.find(
    position => Number(position.public_purchase_plan_id) === Number(newRequestData.value.public_purchase_plan_id)
  ) || null
)

const isOwner = (request) => {
  return Number(request.project_finance_manager_id) === Number(currentFinanceManagerId.value)
}

const canFinalizeRequest = request =>
  isOwner(request)
  && ['pending', 'prepared', 'approved', 'accounting'].includes(request.status)
  && !['settlement', 'settled'].includes(request.finalizationStatus)
  && Number(request.sourceList__shopCount || 0) > 0

const canReturnToOpen = request =>
  isOwner(request) && request.finalizationStatus === 'prepared'

const finalizationActionLabel = (request, short = false) =>
  request.finalizationStatus === 'prepared'
    ? (short ? 'Dokończ' : 'Dokończ wniosek')
    : (short ? 'Stwórz' : 'Stwórz wniosek')

const workflowActionLabel = (request, short = false) => {
  if (['settlement', 'settled'].includes(request.finalizationStatus)) return short ? 'Historia' : 'Podglad historii'
  if (request.finalizationStatus === 'finalized') return short ? 'Rozlicz' : 'Przekaz do rozliczen'
  if (request.finalizationStatus === 'prepared') return short ? 'Dokoncz' : 'Dokoncz wniosek'
  return short ? 'Edytuj' : 'Edytuj / finalizuj'
}

const filterAndSortList = (itemsList) => {
  let filtered = [...itemsList]
  if (selectedSectionFilter.value) {
    filtered = filtered.filter(item => item.sectionName === selectedSectionFilter.value)
  }
  
  if (sortBy.value === 'date-created-desc') return filtered.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
  if (sortBy.value === 'date-created-asc') return filtered.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
  if (sortBy.value === 'date-modified-desc') return filtered.sort((a, b) => new Date(b.updated_at || b.created_at).getTime() - new Date(a.updated_at || a.created_at).getTime())
  if (sortBy.value === 'budget-desc') return filtered.sort((a, b) => Number(b.budget || 0) - Number(a.budget || 0))
  if (sortBy.value === 'budget-asc') return filtered.sort((a, b) => Number(a.budget || 0) - Number(b.budget || 0))
  if (sortBy.value === 'gross-desc') return filtered.sort((a, b) => Number(b.sourceList__totalPrice ?? b.budget ?? 0) - Number(a.sourceList__totalPrice ?? a.budget ?? 0))
  if (sortBy.value === 'gross-asc') return filtered.sort((a, b) => Number(a.sourceList__totalPrice ?? a.budget ?? 0) - Number(b.sourceList__totalPrice ?? b.budget ?? 0))
  return filtered
}

const aggregatedRequestGroups = computed(() => {
  const processed = filterAndSortList(allRequests.value)
  return [
    { key: 'open',     title: 'Otwarte wnioski',       items: processed.filter(r => r.status === 'pending') },
    { key: 'prepared', title: 'Wnioski do dokończenia', items: processed.filter(r => r.status === 'prepared') },
    { key: 'rejected', title: 'Odrzucone wnioski',      items: processed.filter(r => r.status === 'rejected') },
    { key: 'closed',   title: 'Zamknięte wnioski',      items: processed.filter(r => !['pending', 'prepared', 'rejected'].includes(r.status)) }
  ]
})

const formatRelativeTime = (dateInput) => {
  if (!dateInput) return '—'
  const dateStr = String(dateInput).endsWith('Z') || String(dateInput).includes('+') ? dateInput : `${dateInput}Z`
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  if (diffMs < 0 && diffMs > -60000) return 'przed chwilą'
  const diffSec = Math.floor(diffMs / 1000)
  const diffMin = Math.floor(diffSec / 60)
  const diffHour = Math.floor(diffMin / 60)
  if (diffSec < 60) return 'przed chwilą'
  if (diffMin < 60) return `${diffMin} min temu`
  if (diffHour < 24) return `${diffHour} godz. temu`
  return new Intl.DateTimeFormat('pl-PL').format(date)
}

const mapRequest = (req) => {
  const pfmId = req.project_finance_manager_id
  return {
    id: req.purchase_request_id,
    name: req.purchase_request_name,
    sectionName: req.section_name || req.project_budget_name,
    budget: req.budget_allocated_for_the_order,
    ifService: req.if_service,
    status: req.finalization_status === 'rejected'
      ? 'rejected'
      : (req.finalization_status === 'prepared'
        ? 'prepared'
        : (req.finalization_status === 'accounting_pending'
          ? 'accounting'
          : (req.can_add ? 'pending' : 'approved'))),
    created_at: req.created_at,
    updated_at: req.updated_at,
    used_cpv_id: req.used_cpv_id,
    projectBudgetId: req.project_budget_id,
    projectBudgetName: req.project_budget_name,
    fundingId: req.funding_id,
    fundingName: req.funding_name,
    fundingAllocations: req.funding_allocations || [],
    project_finance_manager_id: pfmId,
    creatorName: pfmId ? (studentsMap.value[pfmId] || `Skarbnik #${pfmId}`) : 'Nieznany',
    sourceList: req.source_shop_purchase_list,
    sourceList__shopCount: req.source_shop_purchase_list?.shop_count,
    sourceList__totalNet: req.source_shop_purchase_list?.total_net,
    sourceList__totalPrice: req.source_shop_purchase_list?.total_price,
    planPosition: req.plan_position,
    planPositions: req.plan_positions || [],
    planComplianceStatus: req.plan_compliance_status,
    documentRequestName: req.document_request_name,
    contractValueDate: req.contract_value_date,
    euroExchangeRate: req.euro_exchange_rate,
    mainCpvCode: req.main_cpv_code,
    finalNetTotal: req.final_net_total,
    finalGrossTotal: req.final_gross_total,
    finalizationStatus: req.finalization_status
  }
}

const fetchStudentsMap = async () => {
  try {
    const response = await fetch(`${API_URL}/students`, { cache: 'no-store' })
    if (!response.ok) return
    const data = await response.json()
    const map = {}
    ;(data || []).forEach(s => {
      const id = s.student_id ?? s.id
      const fullName = [s.name, s.surname].filter(Boolean).join(' ')
      if (id) map[id] = fullName || `Student #${id}`
    })
    studentsMap.value = map
  } catch (e) {
    console.error(e)
  }
}

const fetchRequests = async () => {
  try {
    const response = await fetch(`${API_URL}/purchase_requests`)
    if (!response.ok) throw new Error('Błąd pobierania danych')
    const data = await response.json()
    allRequests.value = data.map(mapRequest)
  } catch (error) {
    console.error(error)
  }
}

const fetchClosedOrdersForRequests = async () => {
  if (!currentFinanceManagerId.value) return
  try {
    const response = await fetch(`${API_URL}/lists/closed_for_purchase_requests?project_finance_manager_id=${currentFinanceManagerId.value}`)
    closedOrders.value = await response.json()
  } catch (error) {
    console.error(error)
  }
}

const fetchFundings = async () => {
  if (!user.value?.association_id) return
  try {
    const response = await fetch(`${API_URL}/fundings?association_id=${user.value.association_id}`)
    fundings.value = await response.json()
  } catch (error) {
    console.error(error)
  }
}

const fetchFundingPlan = async fundingId => {
  fundingPlans.value = []
  if (!fundingId) return
  const response = await fetch(`${API_URL}/public_purchase_plan_lists?funding_id=${fundingId}`)
  if (!response.ok) return
  const plans = await response.json()
  const plan = plans[0] || null
  fundingPlans.value = plan ? [plan] : []
}

const fetchFundingPlansForAllocations = async () => {
  const fundingIds = [...new Set(newRequestData.value.funding_allocations.map(a => Number(a.funding_id)).filter(Boolean))]
  if (fundingIds.length === 0) { fundingPlans.value = []; return; }
  const plans = await Promise.all(fundingIds.map(async fundingId => {
    const response = await fetch(`${API_URL}/public_purchase_plan_lists?funding_id=${fundingId}`)
    if (!response.ok) return null
    const data = await response.json()
    return data[0] || null
  }))
  fundingPlans.value = plans.filter(Boolean)
}

const fetchFundingPlansForIds = async fundingIds => {
  const uniqueFundingIds = [...new Set((fundingIds || []).map(Number).filter(Boolean))]
  if (uniqueFundingIds.length === 0) { fundingPlans.value = []; return }
  const plans = await Promise.all(uniqueFundingIds.map(async fundingId => {
    const response = await fetch(`${API_URL}/public_purchase_plan_lists?funding_id=${fundingId}`)
    if (!response.ok) return null
    const data = await response.json()
    return data[0] || null
  }))
  fundingPlans.value = plans.filter(Boolean)
}

const buildBasketEditorState = basket => {
  const netTotal = Number(basket.total_net ?? ((basket.total_price || basket.cost || 0) / VAT_RATE))
  const fallbackFundingId = Number(newRequestData.value.funding_id || basket.funding_id || '')
  const savedRows = newRequestData.value.plan_positions.filter(
    position => Number(position.shop_purchase_list_id) === Number(basket.shop_purchase_list_id)
  )
  if (savedRows.length === 1 && Math.abs(Number(savedRows[0].allocated_amount || 0) - netTotal) < 0.01) {
    return {
      ...basket,
      total_price: Number(basket.total_price || basket.cost || 0),
      total_net: netTotal,
      cpv_mode: 'single',
      funding_id: fallbackFundingId || basket.funding_id || '',
      single_plan_id: savedRows[0].public_purchase_plan_id,
      split_rows: []
    }
  }
  return {
    ...basket,
    total_price: Number(basket.total_price || basket.cost || 0),
    total_net: netTotal,
    cpv_mode: savedRows.length > 0 ? 'split' : 'single',
    funding_id: fallbackFundingId || basket.funding_id || '',
    single_plan_id: '',
    split_rows: savedRows.map(row => {
      const plan = allPlanPositions.value.find(
        position => Number(position.public_purchase_plan_id) === Number(row.public_purchase_plan_id)
      )
      return {
        funding_id: plan?.funding_id || fallbackFundingId || '',
        public_purchase_plan_id: row.public_purchase_plan_id,
        allocated_amount: row.allocated_amount
      }
    })
  }
}

const fetchRequestBaskets = async requestId => {
  if (!requestId) { requestBaskets.value = []; return }
  const response = await fetch(`${API_URL}/lists?purchase_request_id=${requestId}`)
  if (!response.ok) { requestBaskets.value = []; return }
  const data = await response.json()
  requestBaskets.value = (data || []).map(buildBasketEditorState)
}

const fundingName = fundingId => {
  const funding = fundings.value.find(item => Number(item.funding_id) === Number(fundingId))
  return funding?.funding_name || `Dofinansowanie #${fundingId}`
}

const planOptionsForFunding = fundingId =>
  allPlanPositions.value.filter(position => Number(position.funding_id) === Number(fundingId))

const cpvOptionLabel = position => {
  if (!position) return ''
  const prefix = [
    position.plan_position_number ? `poz. ${position.plan_position_number}` : '',
    position.plan_number ? `plan ${position.plan_number}` : ''
  ].filter(Boolean).join(', ')
  const details = [prefix, position.description, position.product_category_name].filter(Boolean).join(' - ')
  return details
    ? `CPV ${position.cpv_code} - ${details}`
    : `CPV ${position.cpv_code} - ${position.funding_name}`
}

const requestPlanPositionLabel = position => {
  const details = [
    position.plan_position_number ? `poz. ${position.plan_position_number}` : '',
    position.description,
    position.product_category_name
  ].filter(Boolean).join(' - ')
  return details ? `${position.cpv_code} (${details})` : position.cpv_code
}

const effectiveBasketFundingId = basket =>
  Number(
    basket?.cpv_mode === 'single'
      ? (newRequestData.value.funding_id || basket?.funding_id || '')
      : (basket?.funding_id || newRequestData.value.funding_id || '')
  )

const planPositionsForFunding = fundingId =>
  newRequestData.value.plan_positions.filter(position => {
    const planPosition = allPlanPositions.value.find(
      item => Number(item.public_purchase_plan_id) === Number(position.public_purchase_plan_id)
    )
    return Number(planPosition?.funding_id) === Number(fundingId)
  })

const planPositionLabel = publicPurchasePlanId => {
  const planPosition = allPlanPositions.value.find(
    item => Number(item.public_purchase_plan_id) === Number(publicPurchasePlanId)
  )
  return planPosition
    ? `${planPosition.funding_name} - ${cpvOptionLabel(planPosition)}`
    : `Pozycja planu #${publicPurchasePlanId}`
}

const openCpvEditorModal = () => {
  showCpvEditorModal.value = true
}

const addBasketSplitRow = basket => {
  if (!basket.split_rows) basket.split_rows = []
  basket.split_rows.push({
    funding_id: '',
    public_purchase_plan_id: '',
    allocated_amount: null
  })
}

const removeBasketSplitRow = (basket, index) => {
  basket.split_rows = (basket.split_rows || []).filter((_, rowIndex) => rowIndex !== index)
}

const applyBasketCpvAssignments = () => {
  newRequestData.value.plan_positions = basketPlanRows.value.map(row => ({
    shop_purchase_list_id: row.shop_purchase_list_id,
    public_purchase_plan_id: row.public_purchase_plan_id,
    allocated_amount: row.allocated_amount
  }))
  newRequestData.value.funding_allocations = basketFundingAllocations.value
  newRequestData.value.budget_allocated_for_the_order = basketGrossTotal.value
  const firstRow = basketPlanRows.value[0]
  newRequestData.value.used_cpv_id = firstRow?.cpv_code || null
  newRequestData.value.public_purchase_plan_id = firstRow?.public_purchase_plan_id || null
  showCpvEditorModal.value = false
}

const requestEditPayload = () => ({
  purchase_request_name: newRequestData.value.purchase_request_name,
  section_name: newRequestData.value.section_name,
  budget_allocated_for_the_order: basketGrossTotal.value || allocationTotal.value || newRequestData.value.budget_allocated_for_the_order || 0,
  if_service: newRequestData.value.if_service,
  used_cpv_id: newRequestData.value.used_cpv_id,
  created_at: new Date().toISOString(),
  can_add: newRequestData.value.can_add,
  project_finance_manager_id: currentFinanceManagerId.value,
  funding_allocations: newRequestData.value.funding_allocations.map(allocation => ({
    funding_id: allocation.funding_id,
    allocated_amount: allocation.allocated_amount
  })),
  public_purchase_plan_id: newRequestData.value.plan_positions[0]?.public_purchase_plan_id || null,
  plan_positions: newRequestData.value.plan_positions
})

const saveCpvEditorChanges = async () => {
  applyBasketCpvAssignments()
  if (!showFinalizationModal.value || !editingRequestId.value) return
  finalizationSaving.value = true
  try {
    const response = await fetch(`${API_URL}/purchase_requests/${editingRequestId.value}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestEditPayload())
    })
    const savedRequest = await response.json().catch(() => ({}))
    if (!response.ok) throw new Error(savedRequest.detail || 'Nie udało się zapisać CPV.')

    const summaryResponse = await fetch(`${API_URL}/purchase_requests/${editingRequestId.value}/prepare_finalization`, {
      method: 'POST'
    })
    const summary = await summaryResponse.json()
    if (!summaryResponse.ok) throw new Error(summary.detail || 'Nie udało się odświeżyć finalizacji.')
    finalizationSummary.value = summary
    finalizationForm.value = {
      ...finalizationForm.value,
      euro_exchange_rate: summary.euro_exchange_rate || finalizationForm.value.euro_exchange_rate,
      contract_value_date: summary.contract_value_date || finalizationForm.value.contract_value_date
    }
    await fetchSettlementLines(editingRequestId.value)
    await Promise.all([fetchRequests(), fetchClosedOrdersForRequests()])
    emit('budget-changed')
  } catch (error) {
    console.error(error)
    alert(error.message || 'Nie udało się zapisać zmian CPV.')
  } finally {
    finalizationSaving.value = false
  }
}

const addPlanPositionForFunding = allocation => {
  const planPositionId = Number(allocation.plan_position_draft_id)
  const amount = Number(allocation.plan_position_draft_amount || 0)
  if (!planPositionId || amount <= 0) return
  const planPosition = allPlanPositions.value.find(
    item => Number(item.public_purchase_plan_id) === planPositionId
  )
  if (!planPosition || Number(planPosition.funding_id) !== Number(allocation.funding_id)) return
  const existing = newRequestData.value.plan_positions.find(
    item => Number(item.public_purchase_plan_id) === planPositionId
  )
  if (existing) existing.allocated_amount = Number(existing.allocated_amount || 0) + amount
  else newRequestData.value.plan_positions.push({
    public_purchase_plan_id: planPositionId,
    allocated_amount: amount
  })
  newRequestData.value.used_cpv_id = planPosition.cpv_code
  newRequestData.value.public_purchase_plan_id = newRequestData.value.plan_positions[0]?.public_purchase_plan_id || null
  allocation.plan_position_draft_id = ''
  allocation.plan_position_draft_amount = null
}

const removePlanPosition = publicPurchasePlanId => {
  newRequestData.value.plan_positions = newRequestData.value.plan_positions.filter(
    item => Number(item.public_purchase_plan_id) !== Number(publicPurchasePlanId)
  )
  const firstPlanId = newRequestData.value.plan_positions[0]?.public_purchase_plan_id || null
  const firstPlan = allPlanPositions.value.find(
    item => Number(item.public_purchase_plan_id) === Number(firstPlanId)
  )
  newRequestData.value.public_purchase_plan_id = firstPlanId
  newRequestData.value.used_cpv_id = firstPlan?.cpv_code || null
}

const addFundingAllocation = () => {
  const fundingId = Number(allocationDraft.value.funding_id)
  const amount = Number(allocationDraft.value.allocated_amount || 0)
  if (!fundingId || amount <= 0) return
  const existing = newRequestData.value.funding_allocations.find(a => Number(a.funding_id) === fundingId)
  if (existing) { existing.allocated_amount = Number(existing.allocated_amount) + amount } 
  else { newRequestData.value.funding_allocations.push({ funding_id: fundingId, allocated_amount: amount, plan_position_draft_id: '', plan_position_draft_amount: null }) }
  if (!newRequestData.value.funding_id) {
    newRequestData.value.funding_id = fundingId
    const funding = fundings.value.find(item => Number(item.funding_id) === fundingId)
    newRequestData.value.project_budget_id = funding?.project_budget_id || null
  }
  fetchFundingPlansForAllocations()
  allocationDraft.value = { funding_id: '', allocated_amount: null }
}

const removeFundingAllocation = fundingId => {
  newRequestData.value.funding_allocations = newRequestData.value.funding_allocations.filter(a => Number(a.funding_id) !== Number(fundingId))
  const removedPlanIds = planOptionsForFunding(fundingId).map(position => Number(position.public_purchase_plan_id))
  newRequestData.value.plan_positions = newRequestData.value.plan_positions.filter(
    position => !removedPlanIds.includes(Number(position.public_purchase_plan_id))
  )
  if (Number(newRequestData.value.funding_id) === Number(fundingId)) {
    const first = newRequestData.value.funding_allocations[0]
    newRequestData.value.funding_id = first?.funding_id || ''
    const funding = fundings.value.find(item => Number(item.funding_id) === Number(newRequestData.value.funding_id))
    newRequestData.value.project_budget_id = funding?.project_budget_id || null
  }
  fetchFundingPlansForAllocations()
}

const resetRequestForm = () => {
  newRequestData.value.purchase_request_name = ''
  newRequestData.value.section_name = ''
  newRequestData.value.budget_allocated_for_the_order = null
  newRequestData.value.if_service = false
  newRequestData.value.used_cpv_id = null
  newRequestData.value.can_add = true
  newRequestData.value.shop_purchase_list_id = ''
  newRequestData.value.funding_id = ''
  newRequestData.value.project_budget_id = null
  newRequestData.value.funding_allocations = []
  newRequestData.value.public_purchase_plan_id = null
  newRequestData.value.plan_positions = []
  allocationDraft.value = { funding_id: '', allocated_amount: null }
  fundingPlans.value = []
  requestBaskets.value = []
}

const prepareFinalization = async request => {
  finalizationRequest.value = request
  finalizationLoading.value = true
  showFinalizationModal.value = true
  try {
    await hydrateRequestEditorState(request)
    const response = await fetch(`${API_URL}/purchase_requests/${request.id}/prepare_finalization`, {
      method: 'POST'
    })
    const data = await response.json()
    if (!response.ok) throw new Error(data.detail || 'Nie udalo sie przygotowac wniosku')
    finalizationSummary.value = data
    finalizationForm.value = {
      document_request_name: data.document_request_name || request.name,
      euro_exchange_rate: data.euro_exchange_rate || null,
      contract_value_date: data.contract_value_date || new Date().toISOString().slice(0, 10)
    }
    await fetchSettlementLines(request.id)
    await Promise.all([fetchRequests(), fetchClosedOrdersForRequests()])
  } catch (error) {
    console.error(error)
    alert(error.message || 'Nie udalo sie przygotowac finalizacji.')
    showFinalizationModal.value = false
  } finally {
    finalizationLoading.value = false
  }
}

const fetchSettlementLines = async requestId => {
  if (!requestId) {
    settlementLines.value = []
    return
  }
  const response = await fetch(`${API_URL}/purchase_requests/${requestId}/settlement_lines`)
  if (!response.ok) {
    settlementLines.value = []
    return
  }
  settlementLines.value = await response.json()
}

const saveSettlementLines = async () => {
  if (!finalizationRequest.value) return
  const response = await fetch(`${API_URL}/purchase_requests/${finalizationRequest.value.id}/settlement_lines`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      lines: settlementLines.value.map(line => ({
        settlement_line_id: line.settlement_line_id,
        shop_purchase_list_id: line.shop_purchase_list_id,
        invoice_id: line.invoice_id,
        shop_name: line.shop_name,
        purchase_description: line.purchase_description,
        planned_gross_amount: Number(line.planned_gross_amount || 0),
        actual_gross_amount: line.actual_gross_amount,
        is_extra: Boolean(line.is_extra)
      }))
    })
  })
  const data = await response.json().catch(() => [])
  if (!response.ok) throw new Error(data.detail || 'Nie udalo sie zapisac podsumowania rozliczen')
  settlementLines.value = data
}

const saveFinalization = async () => {
  if (!finalizationRequest.value) return
  finalizationSaving.value = true
  try {
    await saveSettlementLines()
    const response = await fetch(`${API_URL}/purchase_requests/${finalizationRequest.value.id}/finalize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        document_request_name: finalizationForm.value.document_request_name,
        euro_exchange_rate: Number(finalizationForm.value.euro_exchange_rate || 0),
        contract_value_date: finalizationForm.value.contract_value_date
      })
    })
    const data = await response.json()
    if (!response.ok) throw new Error(data.detail || 'Nie udalo sie zapisac finalizacji')
    finalizationSummary.value = data
    finalizationRequest.value = { ...finalizationRequest.value, finalizationStatus: 'accounting_pending' }
    await fetchSettlementLines(finalizationRequest.value.id)
    await Promise.all([fetchRequests(), fetchClosedOrdersForRequests()])
    emit('budget-changed')
  } catch (error) {
    console.error(error)
    alert(error.message || 'Nie udalo sie zapisac finalizacji.')
  } finally {
    finalizationSaving.value = false
  }
}

const sendToSettlement = async () => {
  if (!finalizationRequest.value) return
  finalizationSaving.value = true
  try {
    await saveSettlementLines()
    const response = await fetch(`${API_URL}/purchase_requests/${finalizationRequest.value.id}/send_to_settlement`, {
      method: 'POST'
    })
    const data = await response.json().catch(() => ({}))
    if (!response.ok) throw new Error(data.detail || 'Nie udalo sie przekazac wniosku do rozliczen')
    showFinalizationModal.value = false
    await Promise.all([fetchRequests(), fetchClosedOrdersForRequests()])
    emit('budget-changed')
  } catch (error) {
    console.error(error)
    alert(error.message || 'Nie udalo sie przekazac wniosku do rozliczen.')
  } finally {
    finalizationSaving.value = false
  }
}

const saveFinalizationDraft = async () => {
  if (!finalizationRequest.value) {
    showFinalizationModal.value = false
    return
  }
  finalizationSaving.value = true
  try {
    const payload = {
      document_request_name: finalizationForm.value.document_request_name,
      contract_value_date: finalizationForm.value.contract_value_date
    }
    if (Number(finalizationForm.value.euro_exchange_rate || 0) > 0) {
      payload.euro_exchange_rate = Number(finalizationForm.value.euro_exchange_rate)
    }
    const response = await fetch(`${API_URL}/purchase_requests/${finalizationRequest.value.id}/finalization_draft`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    const data = await response.json()
    if (!response.ok) throw new Error(data.detail || 'Nie udalo sie zapisac szkicu finalizacji')
    finalizationSummary.value = data
    showFinalizationModal.value = false
    await fetchRequests()
  } catch (error) {
    console.error(error)
    alert(error.message || 'Nie udalo sie zapisac szkicu finalizacji.')
  } finally {
    finalizationSaving.value = false
  }
}

const moveToDoDokonczenia = async (request) => {
  if (!confirm(`Przenieść wniosek "${request.name}" do dokończenia?\nKoszyki zostaną zablokowane do edycji.`)) return
  try {
    const response = await fetch(`${API_URL}/purchase_requests/${request.id}/prepare_finalization`, {
      method: 'POST'
    })
    const data = await response.json().catch(() => ({}))
    if (!response.ok) throw new Error(data.detail || 'Nie udało się przenieść wniosku')
    await Promise.all([fetchRequests(), fetchClosedOrdersForRequests()])
  } catch (error) {
    console.error(error)
    alert(error.message || 'Nie udało się przenieść wniosku do dokończenia.')
  }
}

const rejectRequest = async (request) => {
  if (!confirm(`Odrzucić wniosek "${request.name}"?\nTej operacji nie można cofnąć.`)) return
  try {
    const response = await fetch(`${API_URL}/purchase_requests/${request.id}/reject`, {
      method: 'POST'
    })
    const data = await response.json().catch(() => ({}))
    if (!response.ok) throw new Error(data.detail || 'Nie udało się odrzucić wniosku')
    await Promise.all([fetchRequests(), fetchClosedOrdersForRequests()])
    emit('budget-changed')
  } catch (error) {
    console.error(error)
    alert(error.message || 'Nie udało się odrzucić wniosku.')
  }
}

const returnToOpen = async request => {
  if (!confirm('Przywrócić wniosek do otwartych i odblokować edycję koszyków?')) return
  try {
    const response = await fetch(`${API_URL}/purchase_requests/${request.id}/return_to_open`, {
      method: 'POST'
    })
    const data = await response.json().catch(() => ({}))
    if (!response.ok) throw new Error(data.detail || 'Nie udalo sie przywrocic wniosku')
    await Promise.all([fetchRequests(), fetchClosedOrdersForRequests()])
    emit('budget-changed')
  } catch (error) {
    console.error(error)
    alert(error.message || 'Nie udalo sie przywrocic wniosku do otwartych.')
  }
}

const handleNewRequest = async () => {
  if (!currentFinanceManagerId.value) {
    alert('Brak ID skarbnika. Nie mozna zapisac wniosku.')
    return
  }
  if (editingRequestId.value && requestBaskets.value.length > 0) {
    applyBasketCpvAssignments()
  }
  try {
    const payload = editingRequestId.value ? requestEditPayload() : {
      purchase_request_name: newRequestData.value.purchase_request_name,
      section_name: newRequestData.value.section_name,
      budget_allocated_for_the_order: 0,
      if_service: false,
      used_cpv_id: null,
      created_at: new Date().toISOString(),
      can_add: true,
      project_finance_manager_id: currentFinanceManagerId.value
    }
    const requestUrl = editingRequestId.value ? `${API_URL}/purchase_requests/${editingRequestId.value}` : `${API_URL}/create_purchase_requests`
    const response = await fetch(requestUrl, { method: editingRequestId.value ? 'PATCH' : 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
    if (!response.ok) {
      const error = await response.json().catch(() => ({}))
      throw new Error(error.detail || 'Nie udalo sie zapisac wniosku')
    }
    resetRequestForm()
    showAddRequestModal.value = false
    editingRequestId.value = null
    await Promise.all([fetchRequests(), fetchClosedOrdersForRequests()])
    emit('budget-changed')
  } catch (error) {
    console.error(error)
    alert(error.message || 'Nie udalo sie zapisac wniosku.')
  }
}

const deleteRequest = async (id) => {
  if (!confirm('Czy na pewno chcesz usunąć ten wniosek?')) return
  try {
    const response = await fetch(`${API_URL}/purchase_requests/${id}`, { method: 'DELETE' })
    if (response.ok) {
      allRequests.value = allRequests.value.filter(r => r.id !== id)
      if (activeRequest.value?.id === id) activeRequest.value = null
    }
  } catch (error) { console.error(error) }
}

const formatStatus = (status) => {
  const map = { pending: 'Oczekujący', prepared: 'Do dokończenia', approved: 'Zatwierdzony', rejected: 'Odrzucony' }
  return map[status] || status
}
const formatPlanStatus = status => status === 'compliant' ? 'Zgodny z planem' : (status === 'requires_approval' ? 'Wymaga zgody' : status || 'Brak danych')
const formatDate = (dateStr) => dateStr ? new Intl.DateTimeFormat('pl-PL').format(new Date(dateStr)) : '—'
const formatMoney = (value) => Number(value || 0).toLocaleString('pl-PL', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

const openAddRequestModal = async () => {
  resetRequestForm()
  editingRequestId.value = null
  showAddRequestModal.value = true
  fetchFundings()
}

const hydrateRequestEditorState = async (request) => {
  await fetchFundings()
  editingRequestId.value = request.id
  newRequestData.value.purchase_request_name = request.name
  newRequestData.value.section_name = request.sectionName || ''
  newRequestData.value.budget_allocated_for_the_order = request.budget
  newRequestData.value.if_service = request.ifService
  newRequestData.value.used_cpv_id = request.used_cpv_id || null
  newRequestData.value.can_add = request.status === 'pending'
  newRequestData.value.shop_purchase_list_id = ''
  newRequestData.value.funding_id = request.fundingId
  newRequestData.value.project_budget_id = request.projectBudgetId
  newRequestData.value.funding_allocations = request.fundingAllocations?.length
    ? request.fundingAllocations.map(allocation => ({
        funding_id: allocation.funding_id,
        allocated_amount: allocation.allocated_amount,
        plan_position_draft_id: '',
        plan_position_draft_amount: null
      }))
    : [{
        funding_id: request.fundingId,
        allocated_amount: request.budget,
        plan_position_draft_id: '',
        plan_position_draft_amount: null
      }]
  newRequestData.value.public_purchase_plan_id = request.planPosition?.public_purchase_plan_id || null
  newRequestData.value.plan_positions = request.planPositions?.length
    ? request.planPositions.map(position => ({
        shop_purchase_list_id: position.shop_purchase_list_id || null,
        public_purchase_plan_id: position.public_purchase_plan_id,
        allocated_amount: position.allocated_amount || request.budget
      }))
    : (request.planPosition ? [{
        public_purchase_plan_id: request.planPosition.public_purchase_plan_id,
        allocated_amount: request.planPosition.allocated_amount || request.budget
      }] : [])
  await fetchFundingPlansForIds(fundings.value.map(funding => funding.funding_id))
  await fetchRequestBaskets(request.id)
}

const openEditRequestModal = async (request) => {
  await hydrateRequestEditorState(request)
  showAddRequestModal.value = true
}

watch(
  () => newRequestData.value.funding_id,
  newFundingId => {
    const normalizedFundingId = Number(newFundingId || 0)
    if (!normalizedFundingId) return

    requestBaskets.value = requestBaskets.value.map(basket => {
      if (basket.cpv_mode !== 'single') return basket
      const currentPlan = allPlanPositions.value.find(
        position => Number(position.public_purchase_plan_id) === Number(basket.single_plan_id)
      )
      const shouldResetPlan =
        currentPlan && Number(currentPlan.funding_id) !== normalizedFundingId
      return {
        ...basket,
        funding_id: normalizedFundingId,
        single_plan_id: shouldResetPlan ? '' : basket.single_plan_id
      }
    })
  }
)

onMounted(async () => {
  await fetchStudentsMap()
  await fetchRequests()
  await fetchClosedOrdersForRequests()
  await fetchFundings()
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;500;600;700;800&display=swap');

.requests-container { display: flex; flex-direction: column; gap: 2vh; }
.requests-section { width: 100%; padding: 2vh 0; font-family: 'Nunito', system-ui, sans-serif; }

.requests-filter-bar { display: flex; justify-content: space-between; align-items: center; gap: 1.5vw; margin-bottom: 3vh; padding: 1vw; background: rgba(var(--rgb-surface), 0.5); border: 0.08vw solid rgba(148, 163, 184, 0.15); border-radius: 0.8vw; flex-wrap: wrap; }
.filter-group-item { display: flex; align-items: center; gap: 0.5vw; }
.section-filter-dropdown { min-width: 14vw; }

.view-toggle-container { display: flex; background: rgba(var(--rgb-raised), 0.8); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 0.6vw; padding: 0.2vw; margin-left: auto; }
.toggle-view-btn { background: transparent; border: none; color: #94a3b8; padding: 0.5vw 1.2vw; font-size: 0.85vw; font-weight: 700; border-radius: 0.4vw; cursor: pointer; transition: all 0.2s ease; font-family: inherit; }
.toggle-view-btn--active { background: rgba(59, 130, 246, 0.2); color: #60a5fa; }

.requests-header { margin-bottom: 3vh; display: flex; justify-content: space-between; align-items: center; gap: 2vw; }
.requests-title-section { display: flex; flex-direction: column; gap: 0.5vw; }
.requests-title { font-size: 1.8vw; font-weight: 800; color: var(--color-heading); margin: 0; }
.requests-subtitle { font-size: 0.95vw; color: rgba(var(--rgb-muted), 0.6); margin: 0; }

.requests-add-button { padding: 0.8vw 1.5vw; background: linear-gradient(135deg, #3b82f6, #2563eb); color: rgb(var(--rgb-text)); border: none; border-radius: 0.8vw; font-size: 1vw; font-weight: 700; cursor: pointer; transition: all 0.2s ease; box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3); }
.requests-add-button:hover { transform: translateY(-0.2vh); box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4); }

.request-status-group { margin-bottom: 4vh; }
.status-group-title { font-size: 1.2vw; color: #94a3b8; font-weight: 800; text-transform: uppercase; letter-spacing: 0.04em; margin: 0 0 1.5vw 0; border-left: 3px solid #3b82f6; padding-left: 0.6vw; }

.requests-empty { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 5vh; background: rgba(var(--rgb-surface), 0.4); border: 0.08vw dashed rgba(148, 163, 184, 0.25); border-radius: 1vw; text-align: center; }
.requests-empty--compact { padding: 2.5vh; border-style: solid; background: rgba(var(--rgb-surface), 0.2); }
.requests-empty-subtext { font-size: 0.9vw; color: rgba(var(--rgb-muted), 0.4); margin: 0; font-style: italic; }

.requests-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(26vw, 1fr)); gap: 2vw; }
.request-card { display: flex; flex-direction: column; padding: 1.8vw; background: rgba(var(--rgb-surface), 0.6); border: 0.08vw solid rgba(148, 163, 184, 0.15); border-radius: 1vw; transition: all 0.3s ease; }
.request-card:hover { background: rgba(var(--rgb-surface), 0.8); border-color: rgba(59, 130, 246, 0.3); transform: translateY(-0.4vh); }
.request-card__header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.5vw; gap: 1vw; }
.request-card__title { font-size: 1.15vw; font-weight: 700; color: rgb(var(--rgb-text)); margin: 0; flex: 1; }
.request-card__section-badge { display: inline-block; padding: 0.15vw 0.5vw; background: rgba(59, 130, 246, 0.12); color: #60a5fa; border-radius: 0.3vw; font-size: 0.7vw; font-weight: 700; border: 1px solid rgba(59, 130, 246, 0.2); margin-top: 0.4vw; text-transform: uppercase; }

.request-card__badge { padding: 0.4vw 0.8vw; border-radius: 0.4vw; font-size: 0.8vw; font-weight: 700; white-space: nowrap; text-transform: uppercase; text-align: center; }
.request-card__badge.pending { background: rgba(251, 191, 36, 0.15); color: #fcd34d; border: 1px solid rgba(251, 191, 36, 0.25); }
.request-card__badge.prepared { background: rgba(16, 185, 129, 0.15); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.28); }
.request-card__badge.accounting { background: rgba(245, 158, 11, 0.14); color: #fcd34d; border: 1px solid rgba(245, 158, 11, 0.28); }
.request-card__badge.approved { background: rgba(34, 197, 94, 0.15); color: #86efac; border: 1px solid rgba(34, 197, 94, 0.25); }
.request-card__badge.rejected { background: rgba(239, 68, 68, 0.15); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.25); }

.request-card__content { flex: 1; display: flex; flex-direction: column; gap: 0.6vw; margin-bottom: 1.5vw; }
.request-card__detail { display: flex; align-items: center; justify-content: space-between; font-size: 0.9vw; margin: 0; }
.request-card__label { color: rgba(var(--rgb-muted), 0.55); font-weight: 600; }
.request-card__value { color: rgb(var(--rgb-text)); font-weight: 500; }

.request-card__actions { display: flex; gap: 0.5vw; flex-wrap: wrap; }
.request-card__button { flex: 1; min-width: 5.5vw; padding: 0.6vw; border: none; border-radius: 0.5vw; font-size: 0.85vw; font-weight: 700; cursor: pointer; transition: all 0.2s ease; font-family: inherit; }
.request-card__button.view { background: rgba(59, 130, 246, 0.15); color: var(--color-link); border: 1px solid rgba(59, 130, 246, 0.2); }
.request-card__button.view:hover { background: #2563eb; color: rgb(var(--rgb-text)); border-color: #2563eb; }
.request-card__button.finalize { background: rgba(16, 185, 129, 0.14); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.28); }
.request-card__button.finalize:hover { background: #059669; color: rgb(var(--rgb-text)); border-color: #059669; }
.request-card__button.reopen { background: rgba(245, 158, 11, 0.14); color: #fcd34d; border: 1px solid rgba(245, 158, 11, 0.28); }
.request-card__button.reopen:hover { background: #d97706; color: rgb(var(--rgb-text)); border-color: #d97706; }
.request-card__button.delete { background: rgba(239, 68, 68, 0.12); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.2); }
.request-card__button.delete:hover { background: #dc2626; color: rgb(var(--rgb-text)); border-color: #dc2626; }
.request-card__button.approve { background: rgba(16, 185, 129, 0.14); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.28); }
.request-card__button.approve:hover { background: #059669; color: rgb(var(--rgb-text)); border-color: #059669; }
.request-card__button.reject-btn { background: rgba(239, 68, 68, 0.12); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.2); }
.request-card__button.reject-btn:hover { background: #dc2626; color: rgb(var(--rgb-text)); border-color: #dc2626; }

.excel-table-wrapper { background: rgba(var(--rgb-surface), 0.4); border: 1px solid rgba(148, 163, 184, 0.15); border-radius: 0.8vw; overflow-x: auto; width: 100%; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2); margin-bottom: 1vw; }
.excel-list-table { width: 100%; border-collapse: collapse; text-align: left; font-size: 0.85vw; min-width: 1050px; }
.excel-list-table th, .excel-list-table td { padding: 0.9vw 1.2vw; border-bottom: 1px solid rgba(148, 163, 184, 0.1); vertical-align: middle; }
.excel-list-table th { background: rgba(var(--rgb-raised), 0.8); color: #94a3b8; font-weight: 700; text-transform: uppercase; font-size: 0.75vw; letter-spacing: 0.05em; border-bottom: 2px solid rgba(148, 163, 184, 0.2); }
.excel-list-table tr:hover { background: rgba(59, 130, 246, 0.02); }

.table-section-badge { padding: 0.2vw 0.5vw; background: rgba(245, 158, 11, 0.12); color: #fcd34d; border-radius: 0.4vw; font-weight: 700; font-size: 0.75vw; text-transform: uppercase; }
.text-badge-only { padding: 0.2vw 0.5vw; font-size: 0.75vw; display: inline-block; border-radius: 0.3vw; }
.table-row-actions { display: flex; gap: 0.4vw; }
.table-btn { padding: 0.4vw 0.8vw; border: none; border-radius: 0.4vw; font-size: 0.78vw; font-weight: 700; cursor: pointer; transition: all 0.2s ease; font-family: inherit; }
.table-btn.view { background: rgba(59, 130, 246, 0.15); color: var(--color-link); border: 1px solid rgba(59, 130, 246, 0.2); }
.table-btn.view:hover { background: #2563eb; color: rgb(var(--rgb-text)); }
.table-btn.finalize { background: rgba(16, 185, 129, 0.14); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.28); }
.table-btn.finalize:hover { background: #059669; color: rgb(var(--rgb-text)); }
.table-btn.reopen { background: rgba(245, 158, 11, 0.14); color: #fcd34d; border: 1px solid rgba(245, 158, 11, 0.28); }
.table-btn.reopen:hover { background: #d97706; color: rgb(var(--rgb-text)); }
.table-btn.delete { background: rgba(239, 68, 68, 0.12); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.2); }
.table-btn.delete:hover { background: #dc2626; color: rgb(var(--rgb-text)); }
.table-btn.approve { background: rgba(16, 185, 129, 0.14); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.28); }
.table-btn.approve:hover { background: #059669; color: rgb(var(--rgb-text)); }
.table-btn.reject-btn { background: rgba(239, 68, 68, 0.12); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.2); }
.table-btn.reject-btn:hover { background: #dc2626; color: rgb(var(--rgb-text)); }

.sort-label { font-size: 0.8vw; color: #94a3b8; font-weight: 700; text-transform: uppercase; }
.excel-sort-select { background: transparent; border: none; color: #60a5fa; font-size: 0.85vw; font-weight: 700; cursor: pointer; outline: none; font-family: inherit; }
.excel-sort-select option { background: #0f172a; color: rgb(var(--rgb-text)); }

.request-details__back { margin-bottom: 2vh; background: none; border: none; color: var(--color-link); cursor: pointer; font-size: 1vw; font-family: inherit; font-weight: 700; }
.request-details__card { background: rgba(var(--rgb-surface), 0.6); border: 0.08vw solid rgba(148, 163, 184, 0.15); border-radius: 1vw; padding: 2vw; }
.request-details__top { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 2vw; }
.request-details__title { color: rgb(var(--rgb-text)); margin: 0; font-size: 1.6vw; font-weight: 800; }
.request-details__subtitle { color: rgba(var(--rgb-muted), 0.5); margin: 0.5vh 0 0 0; }
.request-details__grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1vw; margin-bottom: 2vw; }
.request-info { background: rgba(var(--rgb-raised), 0.6); padding: 1vw; border-radius: 0.8vw; }
.request-info p { color: rgba(var(--rgb-muted), 0.5); margin: 0 0 0.5vh 0; font-size: 0.9vw; }
.request-info strong { color: rgb(var(--rgb-text)); font-size: 1vw; }

.text-blue { color: #60a5fa !important; }
.text-amber { color: #fbbf24 !important; }
.text-white { color: rgb(var(--rgb-text)) !important; }
.text-emerald { color: #34d399 !important; }
.text-muted { color: #64748b !important; }
.font-bold { font-weight: 700; }
.font-mono { font-family: monospace; }

.modal-overlay { position: fixed; inset: 0; background: rgba(5, 8, 22, 0.85); display: flex; justify-content: center; align-items: center; z-index: 1000; backdrop-filter: blur(8px); overflow: hidden; }
.modal-content { width: 90%; max-width: 35vw; max-height: 85vh; background: #0f172a; border: 0.08vw solid rgba(148, 163, 184, 0.15); border-radius: 1.2vw; padding: 2.2vw; box-sizing: border-box; overflow: hidden; display: flex; flex-direction: column; }
.cpv-modal-content { max-width: 78vw; }
.finalization-modal-content {
  width: 100vw;
  max-width: 100vw;
  height: 100vh;
  max-height: 100vh;
  border-radius: 0;
  padding: 1.5vw;
}
.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2.5vh; flex-shrink: 0; }
.modal-title { font-size: 1.5vw; color: #fff; font-weight: 800; }
.modal-close { background: transparent; border: none; color: rgba(var(--rgb-muted), 0.6); font-size: 1.4vw; cursor: pointer; transition: color 0.2s; }
.modal-close:hover { color: rgb(var(--rgb-text)); }

.modal-form { display: flex; flex-direction: column; flex: 1; overflow: hidden; min-height: 0; }
.modal-form__scroll-container { display: flex; flex-direction: column; gap: 1.2vw; overflow-y: auto; flex: 1; padding-right: 0.6vw; min-height: 0; margin-bottom: 1.5vh; }
.modal-form__group { display: flex; flex-direction: column; gap: 0.5vw; }
.modal-form__label { color: #94a3b8; font-size: 0.8vw; font-weight: 700; text-transform: uppercase; letter-spacing: 0.03em; }
.modal-form__input { box-sizing: border-box; padding: 0.8vw 1vw; border-radius: 0.6vw; border: 0.08vw solid rgba(148,163,184,0.2); background: rgba(15,23,42,0.7); color: rgb(var(--rgb-text)); font-size: 0.95vw; outline: none; transition: border-color 0.2s; width: 100%; }
.modal-form__input:focus { border-color: #3b82f6; }

.funding-allocation-row { display: grid; grid-template-columns: 1fr 8vw auto; gap: 0.7vw; align-items: center; }
.funding-allocation-list { display: grid; gap: 0.5vw; margin-top: 0.8vw; }
.funding-allocation-item, .funding-allocation-total { display: grid; grid-template-columns: 1fr auto auto; gap: 0.8vw; align-items: center; padding: 0.75vw; border-radius: 0.6vw; background: rgba(var(--rgb-raised), 0.62); color: rgb(var(--rgb-muted)); }
.funding-allocation-total { grid-template-columns: 1fr auto; background: rgba(59, 130, 246, 0.16); }
.plan-position-picker { grid-column: 1 / -1; display: grid; grid-template-columns: 1fr 8vw auto; gap: 0.7vw; align-items: center; }
.plan-position-list { grid-column: 1 / -1; display: grid; gap: 0.45vw; }
.plan-position-item { display: grid; grid-template-columns: 1fr auto auto; gap: 0.7vw; align-items: center; padding: 0.55vw 0.65vw; border-radius: 0.5vw; background: rgba(var(--rgb-surface), 0.55); color: rgb(var(--rgb-muted)); }
.cpv-editor-open { width: fit-content; }
.cpv-editor { display: grid; gap: 1vw; overflow-y: auto; padding-right: 0.5vw; min-height: 0; }
.cpv-main-funding { display: grid; gap: 0.45vw; padding: 0.9vw 1vw; border-radius: 0.7vw; background: rgba(var(--rgb-surface), 0.55); border: 1px solid rgba(148, 163, 184, 0.16); }
.cpv-basket { display: grid; gap: 0.8vw; padding: 1vw; border-radius: 0.7vw; background: rgba(var(--rgb-raised), 0.55); border: 1px solid rgba(148, 163, 184, 0.16); }
.cpv-basket__top { display: flex; justify-content: space-between; gap: 1vw; align-items: flex-start; }
.cpv-basket__top h3 { margin: 0; color: rgb(var(--rgb-text)); font-size: 1vw; }
.cpv-basket__top p { margin: 0.35vw 0 0 0; color: rgba(var(--rgb-muted), 0.62); font-size: 0.82vw; }
.cpv-mode-toggle { display: flex; background: rgba(var(--rgb-surface), 0.7); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 0.5vw; padding: 0.15vw; }
.cpv-mode-toggle button { border: 0; border-radius: 0.35vw; background: transparent; color: #94a3b8; padding: 0.45vw 0.75vw; font-weight: 700; cursor: pointer; }
.cpv-mode-toggle button.active { background: rgba(59, 130, 246, 0.22); color: var(--color-link); }
.cpv-single-row { display: grid; grid-template-columns: 1fr; }
.cpv-split { display: grid; gap: 0.7vw; }
.cpv-split-row { display: grid; grid-template-columns: 1fr 1.2fr 8vw auto; gap: 0.7vw; align-items: center; }
.cpv-summary { display: grid; gap: 0.8vw; }
.cpv-summary h3 { margin: 0; color: var(--color-heading); font-size: 1vw; }
.cpv-summary-table { min-width: 900px; }
.cpv-summary-table tfoot td { font-weight: 800; background: rgba(59, 130, 246, 0.1); }
.finalization-editor { display: grid; gap: 1vw; overflow-y: auto; padding-right: 0.5vw; min-height: 0; }
.finalization-grid { display: grid; grid-template-columns: 1.4fr 0.7fr 0.8fr auto; gap: 0.9vw; align-items: end; }
.finalization-cpv-shortcut { min-width: 11vw; }
.finalization-cpv-shortcut small { color: #94a3b8; font-size: 0.76vw; line-height: 1.35; }
.finalization-section { display: grid; gap: 0.75vw; padding: 1vw; border-radius: 0.7vw; background: rgba(var(--rgb-raised), 0.48); border: 1px solid rgba(148, 163, 184, 0.16); }
.finalization-section h3 { margin: 0; color: var(--color-heading); font-size: 1vw; }
.finalization-section__header { display: flex; justify-content: space-between; align-items: flex-start; gap: 1vw; }
.finalization-section__header p { margin: 0.3vw 0 0 0; color: #94a3b8; font-size: 0.82vw; }
.finalization-plan-summary { gap: 1vw; background: rgba(var(--rgb-surface), 0.58); border-color: rgba(96, 165, 250, 0.2); }
.plan-summary-toggle { display: flex; padding: 0.16vw; border-radius: 0.5vw; background: rgba(var(--rgb-surface), 0.7); border: 1px solid rgba(148, 163, 184, 0.2); }
.plan-summary-toggle button { border: 0; border-radius: 0.36vw; background: transparent; color: #94a3b8; padding: 0.42vw 0.75vw; font-weight: 800; cursor: pointer; }
.plan-summary-toggle button.active { background: rgba(59, 130, 246, 0.22); color: var(--color-heading); }
.plan-summary-metrics { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 0.7vw; }
.plan-summary-metrics div, .plan-summary-card__amounts div { display: grid; gap: 0.28vw; padding: 0.75vw; border-radius: 0.55vw; background: rgba(var(--rgb-raised), 0.62); border: 1px solid rgba(148, 163, 184, 0.12); }
.plan-summary-metrics span, .plan-summary-card__amounts span { color: #94a3b8; font-size: 0.74vw; font-weight: 800; text-transform: uppercase; }
.plan-summary-metrics strong, .plan-summary-card__amounts strong { color: rgb(var(--rgb-muted)); font-size: 0.95vw; }
.plan-summary-list { display: grid; grid-template-columns: repeat(auto-fit, minmax(360px, 1fr)); gap: 0.8vw; }
.plan-summary-card { display: grid; gap: 0.8vw; padding: 0.9vw; border-radius: 0.65vw; background: rgba(var(--rgb-raised), 0.52); border: 1px solid rgba(148, 163, 184, 0.14); }
.plan-summary-card__top { display: flex; justify-content: space-between; gap: 0.8vw; align-items: flex-start; }
.plan-summary-card__top h4 { margin: 0; color: rgb(var(--rgb-text)); font-size: 0.98vw; }
.plan-summary-card__top p { margin: 0.25vw 0 0 0; color: #94a3b8; font-size: 0.8vw; }
.plan-summary-card__badge { flex-shrink: 0; padding: 0.32vw 0.55vw; border-radius: 999px; color: #a7f3d0; background: rgba(16, 185, 129, 0.13); border: 1px solid rgba(16, 185, 129, 0.2); font-size: 0.72vw; font-weight: 800; }
.plan-summary-card__badge--changed { color: #fcd34d; background: rgba(245, 158, 11, 0.13); border-color: rgba(245, 158, 11, 0.24); }
.plan-summary-card__amounts { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0.6vw; }
.plan-summary-cpv-list { display: grid; gap: 0.45vw; }
.plan-summary-cpv { display: grid; grid-template-columns: 1fr 1fr 1.3fr auto; gap: 0.6vw; align-items: center; padding: 0.55vw 0.65vw; border-radius: 0.5vw; background: rgba(var(--rgb-surface), 0.58); color: var(--color-subtle); font-size: 0.8vw; }
.plan-summary-cpv strong { color: #34d399; }
.plan-summary-empty { padding: 0.7vw; border-radius: 0.5vw; background: rgba(var(--rgb-surface), 0.45); color: #94a3b8; font-size: 0.82vw; }
.plan-summary-research { display: grid; gap: 0.35vw; padding: 0.7vw; border-radius: 0.55vw; background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.18); }
.plan-summary-research span { color: var(--color-heading); font-weight: 800; font-size: 0.78vw; }
.plan-summary-research p { margin: 0; color: #dbeafe; font-size: 0.82vw; line-height: 1.35; }
.plan-summary-table { min-width: 1100px; }
.plan-summary-table td { vertical-align: top; }
.plan-summary-table td strong { display: block; color: rgb(var(--rgb-text)); }
.plan-summary-table td small { display: block; margin-top: 0.25vw; color: #94a3b8; max-width: 280px; }
.plan-summary-table-cpv { display: grid; gap: 0.35vw; min-width: 360px; }
.plan-summary-table-cpv span { color: var(--color-subtle); }
.plan-summary-table-cpv strong { display: inline !important; color: var(--color-heading) !important; }
.plan-summary-diff { display: inline-flex; padding: 0.28vw 0.52vw; border-radius: 999px; color: #94a3b8; background: rgba(148, 163, 184, 0.12); font-weight: 800; }
.plan-summary-diff.changed { color: #fcd34d; background: rgba(245, 158, 11, 0.14); }
.finalization-table { min-width: 760px; }
.finalization-totals { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 0.8vw; }
.finalization-totals div { display: grid; gap: 0.35vw; padding: 0.85vw; border-radius: 0.6vw; background: rgba(var(--rgb-surface), 0.58); border: 1px solid rgba(148, 163, 184, 0.12); }
.finalization-totals span { color: #94a3b8; font-size: 0.82vw; font-weight: 700; text-transform: uppercase; }
.finalization-totals strong { color: rgb(var(--rgb-muted)); font-size: 1vw; }
.finalization-remaining-tab { gap: 0.8vw; }
.remaining-funding-list { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 0.7vw; }
.remaining-funding-card { display: flex; justify-content: space-between; gap: 0.8vw; align-items: flex-start; padding: 0.8vw 0.9vw; border-radius: 0.6vw; background: rgba(var(--rgb-surface), 0.62); border: 1px solid rgba(148, 163, 184, 0.14); }
.remaining-funding-card h4 { margin: 0; color: rgb(var(--rgb-text)); font-size: 0.92vw; }
.remaining-funding-card p { margin: 0.25vw 0 0 0; color: #94a3b8; font-size: 0.78vw; }
.remaining-funding-card strong { font-size: 1vw; }
.market-research-file { color: var(--color-heading); font-weight: 700; }
.delete-inline-btn { border: 0; background: transparent; color: #fca5a5; cursor: pointer; font-weight: 700; }

.modal-actions { display: flex; justify-content: flex-end; gap: 1vw; padding-top: 1.5vh; border-top: 0.08vw solid rgba(148,163,184,0.15); flex-shrink: 0; margin-top: auto; }
.modal-btn { padding: 0.8vw 1.6vw; border-radius: 0.6vw; border: none; cursor: pointer; font-weight: 700; font-family: inherit; }
.modal-btn-cancel { background: rgba(148, 163, 184, 0.12); color: rgb(var(--rgb-muted)); }
.modal-btn-cancel:hover { background: rgba(148, 163, 184, 0.25); color: rgb(var(--rgb-text)); }
.modal-btn-save-add { padding: 0.8vw 1.2vw; border-radius: 0.6vw; background: #1e293b; border: 1px solid #3b82f6; color: #60a5fa; font-weight: 700; cursor: pointer; min-width: 15vw; }
.modal-btn-finish { background: #1e293b; border: 1px solid #e2e8f0; color: rgb(var(--rgb-muted)); margin-right: auto; }
.modal-btn-finish:hover { background: rgba(var(--rgb-muted), 0.1); color: rgb(var(--rgb-text)); }
.modal-btn-save { background: linear-gradient(135deg, #3b82f6, #2563eb); color: rgb(var(--rgb-text)); box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2); }
.modal-btn-save:not(:disabled):hover { transform: translateY(-1px); box-shadow: 0 66px 16px rgba(37, 99, 235, 0.35); }

.custom-scrollbar::-webkit-scrollbar { height: 7px; width: 6px; background: rgba(var(--rgb-raised), 0.5); border-radius: 10px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(148, 163, 184, 0.25); border-radius: 10px; }
</style>
