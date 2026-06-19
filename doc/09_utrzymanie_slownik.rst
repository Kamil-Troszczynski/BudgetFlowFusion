Utrzymanie i słownik pojęć
==========================

Zasady utrzymania
-----------------

1. Zmiana modelu w ``relations.py`` wymaga sprawdzenia migracji w
   ``src/__init__.py``.
2. Zmiana endpointu wymaga aktualizacji dokumentacji API.
3. Zmiana procesu użytkownika wymaga aktualizacji dokumentacji
   użytkowej.
4. Zmiana budżetów wymaga testów dofinansowań, dashboardu, wniosków i
   rozliczeń.
5. Zmiana planów publicznych wymaga testów wykorzystania CPV i
   finalizacji.
6. Zmiana finalizacji wymaga sprawdzenia snapshotów i linii
   rozliczeniowych.

Miejsca wysokiego ryzyka
------------------------

Budżety
  Kwoty są liczone z ``Funding``, ``PurchaseRequestFundingAllocation`` i
  ``Funding.spent_money``. Należy unikać podwójnego liczenia.

Plany publiczne
  Pozycje planu są używane przez wnioski i listy. Usuwanie lub edycja
  pozycji wpływa na raportowanie wykorzystania.

Finalizacja
  Snapshot jest historią dokumentu. Nie powinien być kasowany poza
  świadomą operacją ponownej finalizacji.

Rozliczenia
  Faktury, settlementy i linie rozliczeniowe są powiązane z wnioskiem.
  Zmiana statusu powinna zachować historię kwot.

Autoryzacja
  Frontend ukrywa część funkcji, ale backend powinien walidować operacje
  finansowe niezależnie od UI.

Checklist: zmiana modelu danych
-------------------------------

1. Zmień klasę SQLModel w ``backend/src/relations.py``.
2. Dodaj migrację PostgreSQL w ``migrate_project_budgets()``, jeżeli baza
   może już istnieć.
3. Zaktualizuj modele Pydantic w trasach.
4. Zaktualizuj frontendowe payloady i odczyty odpowiedzi.
5. Zaktualizuj testy fixture.
6. Uruchom testy backendu.
7. Uruchom backend z PostgreSQL.
8. Zaktualizuj dokumentację.

Checklist: zmiana budżetów
--------------------------

Sprawdź:

* ``public_purchase_plans_routes.py`` - agregaty budżetowe,
* ``fundings_routes.py`` - dostępne środki dofinansowania,
* ``purchase_request_routes.py`` - rezerwacje i finalizacja,
* dashboard frontendu,
* testy public purchase plans i purchase request.

Minimalny scenariusz ręczny:

1. Utwórz dofinansowanie.
2. Sprawdź budżet sekcji.
3. Sprawdź budżet koła.
4. Utwórz wniosek.
5. Sprawdź spadek dostępnych środków.
6. Sfinalizuj wniosek.
7. Sprawdź rozliczenie.

Checklist: zmiana planów publicznych
------------------------------------

Sprawdź:

* jeden plan dla jednego dofinansowania,
* dodatnie kwoty pozycji,
* unikalność CPV w planie,
* ``remaining_amount``,
* blokadę usunięcia użytej pozycji,
* walidację pozycji planu przy wniosku,
* snapshot finalizacji.

Checklist: zmiana wniosków
--------------------------

Sprawdź:

* zgodność ``funding_id`` z ``project_budget_id``,
* alokacje finansowania,
* alokacje pozycji planu,
* uzasadnienie odstępstwa,
* przejścia statusów,
* finalizację,
* przekazanie do rozliczeń,
* usunięcie wniosku z odpięciem settlementów.

Słownik
-------

Koło naukowe
  ``Association``.

Członek koła
  ``Student`` bez powiązania z ``ProjectFinanceManager``.

Skarbnik
  ``Student`` z ustawionym ``project_finance_manager_id``.

Sekcja/projekt
  ``Project``.

Budżet sekcji
  ``ProjectBudget``.

Budżet koła
  ``AssociationBudget``.

Dofinansowanie
  ``Funding``.

Zadanie budżetowe
  ``FundingTask``.

Plan publiczny
  ``PublicPurchasePlanList``.

Pozycja planu
  ``PublicPurchasePlan``.

Koszyk/lista zakupów
  ``ShopPurchaseList``.

Pozycja koszyka
  ``ShopPurchaseListItem``.

Wkład użytkownika
  ``ShopPurchaseListItemContribution``.

Wniosek
  ``PurchaseRequest``.

Alokacja finansowania
  ``PurchaseRequestFundingAllocation``.

Alokacja planu
  ``PurchaseRequestPlanPosition``.

Snapshot finalizacji
  ``PurchaseRequestFinalizationSnapshot``.

Rozliczenie
  ``Settlement``.

Faktura
  ``Invoice``.

Linia rozliczeniowa
  ``PurchaseRequestSettlementLine``.
