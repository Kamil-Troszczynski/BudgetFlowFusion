Utrzymanie i słownik pojęć
==========================

Zasady utrzymania
-----------------

1. Zmiany w modelach SQLModel powinny być odzwierciedlone w funkcji
   migracyjnej w ``backend/src/__init__.py``.
2. Zmiany w endpointach powinny być odzwierciedlone w dokumentacji API.
3. Zmiany w procesie użytkownika powinny aktualizować dokumentację
   użytkową.
4. Po zmianach finansowych należy sprawdzić dashboard budżetowy, listę
   dofinansowań, tworzenie wniosku i rozliczenia.
5. Przy zmianach w planach publicznych należy sprawdzić wykorzystanie
   pozycji planu oraz finalizację wniosku.

Miejsca wysokiego ryzyka
------------------------

Budżety
  Kwoty są liczone z kilku źródeł: dofinansowań, wydanych pieniędzy,
  alokacji wniosków i finalizacji. Należy unikać podwójnego liczenia.

Plany publiczne
  Pozycja planu może być wykorzystana przez wiele wniosków. Usunięcie
  albo zmiana pozycji wpływa na raportowanie i zgodność z planem.

Finalizacja
  Snapshot powinien chronić historię dokumentu. Nie należy usuwać
  snapshotów bez świadomej migracji.

Rozliczenia
  Faktury i linie rozliczeń są powiązane z wnioskiem. Zmiana statusów
  powinna zachować spójność historii.

Role
  Frontend ukrywa część funkcji, ale backend także powinien pilnować
  dostępu tam, gdzie operacja wpływa na finanse.

Słownik pojęć
-------------

Koło naukowe
  Organizacja użytkowników systemu. W modelu reprezentowana przez
  ``Association``.

Członek koła
  Zwykły użytkownik, który może dodawać przedmioty i pracować na
  dostępnych koszykach.

Skarbnik
  Użytkownik z powiązaniem ``ProjectFinanceManager``. Ma dostęp do
  finansów, planów, wniosków i rozliczeń.

Sekcja / projekt
  Część koła realizująca określony projekt. W modelu jest to ``Project``
  oraz jego ``ProjectBudget``.

Budżet koła
  Zbiorczy budżet na poziomie ``AssociationBudget``.

Budżet sekcji
  Budżet projektu, reprezentowany przez ``ProjectBudget``.

Dofinansowanie
  Konkretne źródło pieniędzy, reprezentowane przez ``Funding``.

Zadanie budżetowe
  Część dofinansowania przypisana do konkretnego celu, reprezentowana
  przez ``FundingTask``.

Plan zamówień publicznych
  Roczny plan dla jednego dofinansowania, reprezentowany przez
  ``PublicPurchasePlanList``.

Pozycja planu publicznego
  Wiersz planu określający CPV i kwotę, reprezentowany przez
  ``PublicPurchasePlan``.

CPV
  Kod klasyfikacji zamówień publicznych. W systemie używany do grupowania
  planów i zakupów.

Koszyk sklepowy
  Lista zakupów dla jednego sklepu, reprezentowana przez
  ``ShopPurchaseList``.

Wniosek o zamówienie
  Formalny dokument zakupowy, reprezentowany przez ``PurchaseRequest``.

Alokacja finansowania
  Przypisanie części kwoty wniosku do dofinansowania, reprezentowane
  przez ``PurchaseRequestFundingAllocation``.

Alokacja planu
  Przypisanie części kwoty wniosku do pozycji planu publicznego,
  reprezentowane przez ``PurchaseRequestPlanPosition``.

Finalizacja
  Etap zamknięcia danych zakupowych wniosku i przygotowania dokumentu do
  księgowości.

Snapshot finalizacji
  Historyczny zapis danych planu i finansowania, reprezentowany przez
  ``PurchaseRequestFinalizationSnapshot``.

Rozliczenie
  Etap obsługi faktur i rzeczywistych kwot, reprezentowany przez
  ``Settlement``.

Faktura
  Dokument księgowy, reprezentowany przez ``Invoice``.

Linia rozliczeniowa
  Pozycja w rozliczeniu wniosku, reprezentowana przez
  ``PurchaseRequestSettlementLine``.

Rekomendowane dalsze usprawnienia
---------------------------------

* Dodać pełniejsze testy procesu finalizacji i rozliczeń.
* Ujednolicić typ CPV we wszystkich testach i formularzach jako tekst.
* Rozważyć wydzielenie warstwy serwisów z endpointów.
* Dodać jawne uprawnienia backendowe dla operacji skarbnika.
* Dodać eksport dokumentów wniosku do oficjalnego szablonu.

Checklist techniczny przy zmianie modelu danych
-----------------------------------------------

1. Zmienić klasę SQLModel w ``backend/src/relations.py``.
2. Jeżeli aplikacja ma działać na istniejącej bazie, dopisać migrację w
   ``migrate_project_budgets()``.
3. Sprawdzić, czy nowe pole wymaga aktualizacji modeli Pydantic w
   ``backend/src/routes``.
4. Sprawdzić, czy frontend wysyła albo czyta nowe pole.
5. Zaktualizować testy fixture, szczególnie ``conftest.py`` i helpery w
   plikach testowych.
6. Uruchomić testy backendu i start kontenerów.
7. Zaktualizować dokumentację modelu danych i API.

Checklist techniczny przy zmianie budżetów
------------------------------------------

Zmiana finansowa powinna zostać sprawdzona w tych miejscach:

.. code-block:: text

   backend/src/routes/public_purchase_plans_routes.py
     _project_budget_amounts
     _association_budget_amounts
     _budget_out
     get_dashboard_budget_summary

   backend/src/routes/fundings_routes.py
     _funding_out

   backend/src/routes/purchase_request_routes.py
     _budget_info_for_request
     create_purchase_request
     update_purchase_request
     finalize_purchase_request

Minimalny scenariusz ręczny:

1. Utworzyć dofinansowanie w sekcji.
2. Sprawdzić, czy budżet sekcji zwiększa się o kwotę dofinansowania.
3. Sprawdzić, czy budżet koła jest sumą sekcji.
4. Utworzyć wniosek z tego dofinansowania.
5. Sprawdzić, czy ``purchase_requests_total_allocated`` rośnie.
6. Sprawdzić, czy ``available_after_purchase_requests`` maleje na
   poziomie dofinansowania, sekcji i koła.

Checklist techniczny przy zmianie planów publicznych
----------------------------------------------------

Miejsca implementacji:

.. code-block:: text

   PublicPurchasePlanList
   PublicPurchasePlan
   PurchaseRequestPlanPosition
   GroupedShopsListByCpvCategoryAndFunding
   ProductCategory.public_purchase_plan_id

Reguły do zachowania:

* jeden ``PublicPurchasePlanList`` na ``Funding``,
* unikalny ``cpv_code`` w ramach jednego planu,
* dodatni ``cost``,
* ``remaining_amount = cost - used_amount``,
* brak możliwości usunięcia pozycji użytej we wniosku,
* brak możliwości usunięcia pozycji z podpiętymi koszykami.

Checklist techniczny przy zmianie wniosków
------------------------------------------

Miejsca implementacji:

.. code-block:: text

   PurchaseRequest
   PurchaseRequestFundingAllocation
   PurchaseRequestPlanPosition
   PurchaseRequestFinalizationSnapshot
   PurchaseRequestSettlementLine

Reguły do zachowania:

* ``funding_id`` musi należeć do ``project_budget_id``,
* pozycja planu musi należeć do jednego z finansowań użytych we wniosku,
* przekroczenie planu wymaga uzasadnienia,
* brak pozycji planu oznacza ``draft``,
* finalizacja wymaga koszyków i pozycji CPV,
* finalizacja blokuje dalsze dodawanie przez ``can_add = False``,
* finalizacja zapisuje snapshot,
* przekazanie do rozliczeń ustawia ``finalization_status = settlement``.

Checklist techniczny przy zmianie list zakupów
----------------------------------------------

Reguły do zachowania:

* lista otwarta ma ``settlement_id = NULL``,
* lista zamknięta ma ``settlement_id`` i nie pozwala zmieniać pozycji,
* ``ShopPurchaseListItem.amount`` jest sumą wkładów,
* ``ShopPurchaseListItemContribution`` decyduje o tym, ile może usunąć
  zwykły student,
* skarbnik może zamknąć tylko listę utworzoną przez siebie,
* duplikat sklepu w tej samej grupie ``gslbccf_id`` jest blokowany.

Ryzyka techniczne
-----------------

Brak pełnej autoryzacji serwerowej
  Frontend zapisuje użytkownika w ``localStorage``. Backend wykonuje
  wybrane walidacje, ale nie ma centralnego middleware autoryzacji.

Logika biznesowa w endpointach
  Duża część reguł jest w funkcjach tras. Przy rozbudowie projektu warto
  wydzielić warstwę serwisów i testować ją niezależnie od HTTP.

Migracje runtime
  ``migrate_project_budgets()`` wykonuje ręczne ``ALTER TABLE`` przy
  starcie aplikacji. To wygodne w projekcie akademickim, ale w systemie
  produkcyjnym lepsze byłyby wersjonowane migracje.

SQLite w testach i PostgreSQL w runtime
  Testy używają SQLite in-memory, a aplikacja działa na PostgreSQL.
  Trzeba uważać na różnice w enumach, typach dat, ograniczeniach FK i
  składni SQL.

Kwoty netto/brutto
  Plan publiczny działa na kwotach netto, koszyki i rozliczenia na
  kwotach brutto. Finalizacja przelicza wartości przez ``1.23``.
  Zmiana VAT albo walut powinna objąć cały przepływ.

CPV jako tekst
  CPV ma format tekstowy i może zawierać myślnik. Nie należy używać
  ``int`` w nowych polach, testach ani payloadach.

Sugestia przyszłej refaktoryzacji
---------------------------------

Najbardziej opłacalne wydzielenie warstwy serwisowej:

.. code-block:: text

   services/budget_service.py
     liczenie budżetu sekcji, koła i dofinansowań

   services/public_plan_service.py
     użycie planu, remaining_amount, walidacja CPV

   services/purchase_request_service.py
     tworzenie wniosku, alokacje, status zgodności

   services/finalization_service.py
     snapshot, netto/brutto, główny CPV

   services/settlement_service.py
     linie rozliczeń, faktury, zamknięcie sprawy

Po takim wydzieleniu endpointy powinny głównie mapować HTTP na wywołania
serwisów, a większość reguł można byłoby testować bez ``TestClient``.
