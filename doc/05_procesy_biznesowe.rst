Procesy biznesowe
=================

Proces 1: Dodanie przedmiotu do katalogu
----------------------------------------

.. code-block:: text

   Użytkownik
      |
      v
   Formularz dodania przedmiotu
      |
      v
   Backend sprawdza autora
      |
      +--> zapis Item(status = approved)
      |
      v
   Przedmiot trafia do wspólnego katalogu

Opis:

1. Użytkownik wybiera kategorię, podkategorię, sklep i podaje dane
   przedmiotu.
2. System zapisuje przedmiot.
3. Aktualny endpoint ``POST /api/items`` zapisuje ``status="approved"``.
4. ``GET /api/items`` zwraca tylko przedmioty zaakceptowane, więc nowy
   przedmiot jest od razu widoczny w katalogu.

Proces 2: Utworzenie dofinansowania
-----------------------------------

.. code-block:: text

   Skarbnik
      |
      v
   Wybór sekcji/projektu
      |
      v
   Dane dofinansowania
      |
      v
   Zadania budżetowe
      |
      v
   Funding + FundingTask

Opis:

1. Skarbnik podaje nazwę dofinansowania, organizatora, osobę podpisującą,
   termin wydatkowania i kwotę.
2. Dofinansowanie jest przypisywane do budżetu sekcji.
3. Opcjonalnie dodawane są zadania budżetowe.
4. Suma zadań nie może przekroczyć kwoty dofinansowania.

Proces 3: Utworzenie planu zamówień publicznych
-----------------------------------------------

.. code-block:: text

   Dofinansowanie
      |
      v
   PublicPurchasePlanList
      |
      v
   Pozycje CPV
      |
      v
   PublicPurchasePlan

Opis:

1. Skarbnik wybiera dofinansowanie.
2. Tworzy roczny plan dla tego dofinansowania.
3. Uzupełnia numer planu, kurs euro i osobę odpowiedzialną.
4. Dodaje pozycje planu: CPV, numer pozycji, opis i kwotę.
5. Pozycje planu mogą zostać powiązane z kategoriami produktowymi.

Proces 4: Tworzenie koszyka sklepowego
--------------------------------------

.. code-block:: text

   Skarbnik lub członek
      |
      v
   Wybór wniosku / pozycji planu
      |
      v
   Wybór sklepu i dofinansowania
      |
      v
   ShopPurchaseList
      |
      v
   Dodawanie pozycji z katalogu

Opis:

1. Koszyk sklepowy jest tworzony dla konkretnego sklepu.
2. Koszyk posiada dofinansowanie oraz kontekst grupy zakupowej.
3. Jeżeli koszyk jest tworzony przez zwykłego członka, musi być
   powiązany z istniejącym otwartym zamówieniem/wnioskiem.
4. Do koszyka dodawane są przedmioty z katalogu.
5. System zapisuje wkład poszczególnych studentów.

Proces 5: Złożenie wniosku o zamówienie
---------------------------------------

.. code-block:: text

   Skarbnik
      |
      v
   Dane wniosku
      |
      v
   Alokacje dofinansowań
      |
      v
   Pozycje planu publicznego
      |
      v
   Walidacja budżetu i planu
      |
      +--> zgodny z planem
      |
      +--> wymaga zgody i uzasadnienia
      |
      v
   PurchaseRequest

Opis:

1. Skarbnik tworzy wniosek.
2. Wniosek otrzymuje kwotę, typ zakupu i kontekst finansowy.
3. Możliwe jest wskazanie wielu alokacji dofinansowań.
4. Możliwe jest wskazanie wielu pozycji planu publicznego.
5. System sprawdza dostępne środki i wykorzystanie pozycji planu.
6. Jeżeli plan jest przekroczony, wymagane jest uzasadnienie.

Proces 6: Finalizacja wniosku
-----------------------------

.. code-block:: text

   PurchaseRequest
      |
      v
   prepare_finalization
      |
      v
   sprawdzenie koszyków i kwot
      |
      v
   finalize
      |
      v
   snapshot + linie rozliczeń
      |
      v
   accounting_pending

Opis:

1. System sprawdza, czy wniosek może być finalizowany.
2. Koszyki zostają zamknięte dla dalszych zmian.
3. System liczy wartości netto, brutto i EUR.
4. Zapisywany jest snapshot danych planu.
5. Tworzone są linie rozliczeniowe.
6. Wniosek przechodzi do statusu oczekiwania na księgowość.

Proces 7: Rozliczenie i faktury
-------------------------------

.. code-block:: text

   Wniosek po finalizacji
      |
      v
   send_to_settlement
      |
      v
   Settlement
      |
      v
   Invoice + SettlementLine
      |
      v
   complete
      |
      v
   settled

Opis:

1. Wniosek trafia do rozliczeń.
2. Skarbnik lub osoba rozliczająca dodaje faktury.
3. Linie rozliczenia są przypisywane do faktur i kwot rzeczywistych.
4. System pokazuje różnice między planem a faktycznym wydatkiem.
5. Po zakończeniu rozliczenia wniosek może trafić do historii.

Proces 8: Kontrola planu publicznego
------------------------------------

.. code-block:: text

   PublicPurchasePlan.cost
      |
      v
   minus suma PurchaseRequestPlanPosition.allocated_amount
      |
      v
   remaining_amount

Jeżeli nowa alokacja przekracza pozostałą kwotę planu, wniosek otrzymuje
status ``requires_approval``. System nie blokuje bezwzględnie takiego
wniosku, ponieważ w praktyce możliwe jest uzasadnione odstępstwo, ale
wymaga opisania powodu.

Proces techniczny: wniosek z zamkniętego koszyka
------------------------------------------------

Ten wariant odpowiada obecnemu wymaganiu, że skarbnik może utworzyć
wniosek ze swoich zamkniętych list zakupów.

.. code-block:: text

   ShopPurchaseList(settlement_id = NULL)
      |
      | PATCH /api/lists/{id}/close
      v
   Settlement(purchase_request_id = NULL)
   ShopPurchaseList(settlement_id = settlement.id)
      |
      | GET /api/lists/closed_for_purchase_requests?project_finance_manager_id=X
      v
   lista zamkniętych koszyków skarbnika
      |
      | POST /api/create_purchase_requests
      |   shop_purchase_list_id = id
      v
   PurchaseRequest
   Settlement(purchase_request_id = purchase_request.id)

Walidacje:

* koszyk musi istnieć,
* koszyk musi mieć ``settlement_id``, czyli być zamknięty,
* koszyk musi być utworzony przez studenta powiązanego z tym samym
  ``project_finance_manager_id``,
* settlement koszyka nie może być już powiązany z innym wnioskiem,
* dofinansowanie koszyka wyznacza ``funding_id`` i ``project_budget_id``
  wniosku,
* kwota wniosku jest liczona z pozycji koszyka przez
  ``_shop_purchase_list_total``.

Proces techniczny: widoczność list zakupów
------------------------------------------

Endpoint ``GET /api/lists`` obsługuje kilka trybów filtrowania.

.. code-block:: text

   treasurer_view=true + association_id
     -> listy studentów z danego koła

   student_id
     -> listy konkretnego studenta

   association_id
     -> listy studentów z danego koła

   open_only=true
     -> tylko listy z settlement_id = NULL

   purchase_request_id
     -> listy z gslbccf_id wniosku

   public_purchase_plan_id
     -> listy z gslbccf_id pozycji planu

Praktyczne reguły wynikające z frontendowego użycia:

* skarbnik widzi swoje listy oraz listy skarbników z tego samego koła,
* zwykły student widzi otwarte listy powiązane z jego kołem i kontekstem
  zamówienia,
* zamykać listę może tylko skarbnik będący jej autorem,
* zwykły student może usuwać z listy tylko ilości zapisane w swoim
  ``ShopPurchaseListItemContribution``.

Proces techniczny: kontrola budżetu przy wniosku
------------------------------------------------

``POST /api/create_purchase_requests`` wykonuje kontrolę w tej kolejności:

1. Ustala źródło danych: payload, alokacje finansowania albo zamknięty
   koszyk.
2. Ustala ``project_budget_id`` i ``funding_id``.
3. Sprawdza, czy dofinansowanie należy do wskazanego budżetu sekcji.
4. Liczy dostępny budżet sekcji.
5. Liczy dostępne środki dofinansowania.
6. Odrzuca wniosek, jeśli kwota przekracza budżet sekcji.
7. Odrzuca wniosek, jeśli kwota przekracza dofinansowanie.
8. Sprawdza pozycje planu publicznego i ich finansowanie.
9. Nadaje ``plan_compliance_status``.
10. Tworzy lub reuse'uje ``gslbccf_id`` dla grupy zakupowej.
11. Zapisuje ``PurchaseRequest``.
12. Zapisuje ``PurchaseRequestFundingAllocation``.
13. Zapisuje ``PurchaseRequestPlanPosition``.

Status zgodności z planem:

.. code-block:: text

   budget_allocated <= 0
     -> draft

   brak pozycji planu
     -> draft

   suma alokacji planu <= pozostała kwota pozycji
     -> compliant

   suma alokacji planu > pozostała kwota pozycji
     -> requires_approval

   requires_approval bez uzasadnienia
     -> HTTP 400

Proces techniczny: finalizacja
------------------------------

Finalizacja składa się z trzech endpointów:

.. code-block:: text

   POST  /api/purchase_requests/{id}/prepare_finalization
   PATCH /api/purchase_requests/{id}/finalization_draft
   POST  /api/purchase_requests/{id}/finalize

``prepare_finalization``:

* wymaga koszyków w grupie ``gslbccf_id``,
* wymaga pozycji ``PurchaseRequestPlanPosition``,
* tworzy lub aktualizuje ``Settlement`` dla każdego koszyka,
* przelicza koszt koszyka z pozycji ``ShopPurchaseListItem``,
* ustawia ``can_add = False`` i ``finalization_status = prepared``.

``finalization_draft``:

* działa tylko dla statusów ``prepared`` i ``draft``,
* zapisuje ``document_request_name``, ``euro_exchange_rate`` i
  ``contract_value_date``,
* wymaga dodatniego kursu euro, jeśli kurs został podany.

``finalize``:

* wymaga niepustej nazwy dokumentu,
* wymaga dodatniego kursu euro,
* tworzy ``PurchaseRequestFinalizationSnapshot``,
* wylicza główny CPV jako CPV z największą kwotą netto,
* przepisuje ``used_cpv_id`` na główny CPV,
* ustawia ``final_net_total`` i ``final_gross_total``,
* aktualizuje kwotę wniosku do wartości brutto,
* ustawia ``finalization_status = accounting_pending``.

Proces techniczny: rozliczenie
------------------------------

.. code-block:: text

   accounting_pending
      |
      | POST /api/purchase_requests/{id}/send_to_settlement
      v
   settlement
      |
      | faktury + przypisanie invoice_id do linii
      v
   POST /api/settlements/{id}/complete
      |
      v
   settled

Warunki zakończenia:

* settlement musi być powiązany z wnioskiem,
* wniosek musi istnieć,
* wszystkie ``PurchaseRequestSettlementLine`` muszą mieć ``invoice_id``,
* po sukcesie backend ustawia ``PurchaseRequest.finalization_status`` na
  ``settled``.
