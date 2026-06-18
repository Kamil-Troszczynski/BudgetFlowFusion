API backendu
============

Konwencje
---------

Backend udostępnia REST API pod adresem:

.. code-block:: text

   http://localhost:8080/api

Dane są przesyłane jako JSON. Frontend komunikuje się z backendem przez
funkcję ``fetch``.

Autoryzacja w obecnym kształcie projektu jest uproszczona. Stan
użytkownika jest przechowywany po stronie frontendu w ``localStorage``,
a wiele endpointów przyjmuje identyfikatory użytkownika, skarbnika lub
koła jako parametry.

Logowanie i rejestracja
-----------------------

``POST /api/login``
  Loguje użytkownika po e-mailu i haśle.

``POST /api/register``
  Rejestruje użytkownika. Może utworzyć zwykłego członka albo skarbnika.

Członkowie
----------

``GET /api/students``
  Zwraca listę studentów/członków.

Katalog przedmiotów
-------------------

``GET /api/items``
  Pobiera katalog przedmiotów.

``GET /api/items/grouped``
  Pobiera przedmioty pogrupowane do wygodnego użycia w interfejsie.

``GET /api/items/pending``
  Pobiera przedmioty oczekujące na akceptację.

``POST /api/items``
  Dodaje nowy przedmiot.

``PATCH /api/items/{item_id}/approve``
  Akceptuje przedmiot.

``DELETE /api/items/{item_id}/reject``
  Odrzuca i usuwa przedmiot.

Kategorie
---------

``GET /api/categories``
  Lista kategorii.

``POST /api/categories``
  Dodanie kategorii wraz z CPV.

``GET /api/subcategories``
  Lista podkategorii.

``GET /api/subcategories/pending``
  Podkategorie oczekujące.

``POST /api/subcategories``
  Dodanie podkategorii.

``PATCH /api/subcategories/{subcategory_id}/assign-category``
  Przypisanie podkategorii do kategorii.

Sklepy
------

``GET /api/shops``
  Pobiera sklepy. Może uwzględniać oczekujące sklepy.

``POST /api/shops``
  Dodaje sklep.

``PATCH /api/shops/{shop_id}``
  Edytuje sklep.

``PATCH /api/shops/{shop_id}/approve``
  Akceptuje sklep.

``DELETE /api/shops/{shop_id}/reject``
  Odrzuca sklep.

Budżety i dofinansowania
------------------------

``GET /api/association_budgets``
  Pobiera budżety koła. Przyjmuje opcjonalnie ``association_id``.

``GET /api/project_budgets``
  Pobiera budżety projektów/sekcji.

``GET /api/dashboard/budget_summary``
  Zwraca agregat budżetowy dla pulpitu.

``GET /api/fundings``
  Pobiera dofinansowania, opcjonalnie filtrowane po kole.

``POST /api/fundings``
  Tworzy dofinansowanie i zadania budżetowe.

``PATCH /api/fundings/{funding_id}``
  Aktualizuje dofinansowanie.

Plany publiczne
---------------

``POST /api/public_purchase_plan_lists``
  Tworzy albo aktualizuje roczny plan publiczny dla dofinansowania.

``GET /api/public_purchase_plan_lists``
  Pobiera plany publiczne, opcjonalnie po ``association_id`` albo
  ``funding_id``.

``GET /api/public_purchase_plan_lists/{id}``
  Pobiera szczegóły planu.

``POST /api/public_purchase_plans``
  Dodaje pozycję CPV do planu.

``PATCH /api/public_purchase_plans/{id}``
  Edytuje pozycję planu.

``DELETE /api/public_purchase_plans/{id}``
  Usuwa pozycję planu, jeżeli nie została użyta w koszykach lub
  wnioskach.

Listy zakupów
-------------

``GET /api/lists``
  Pobiera koszyki sklepowe. Obsługuje filtry: użytkownik, koło, sklep,
  plan publiczny, wniosek, grupa oraz tylko otwarte.

``POST /api/lists``
  Tworzy koszyk sklepowy.

``PATCH /api/lists/{list_id}/close``
  Zamyka koszyk i tworzy/wiąże rozliczenie.

``PATCH /api/lists/{list_id}/reopen``
  Otwiera ponownie koszyk.

``GET /api/lists/closed_for_purchase_requests``
  Pobiera zamknięte koszyki, z których można utworzyć wniosek.

``GET /api/lists/{list_id}``
  Szczegóły koszyka.

``PATCH /api/lists/{list_id}/market_research``
  Zapisuje informację o rozeznaniu rynku.

``DELETE /api/lists/{list_id}``
  Usuwa koszyk.

``GET /api/lists/{list_id}/items``
  Pobiera przedmioty w koszyku.

``POST /api/lists/{list_id}/items``
  Dodaje przedmiot do koszyka.

``DELETE /api/lists/{list_id}/items/{item_id}``
  Usuwa przedmiot z koszyka.

Wnioski
-------

``GET /api/purchase_requests``
  Pobiera wnioski. Może filtrować po kole.

``GET /api/purchase_requests/detail/{purchase_request_id}``
  Szczegóły wniosku.

``GET /api/purchase_requests/{project_finance_manager_id}``
  Wnioski konkretnego skarbnika.

``POST /api/create_purchase_requests``
  Tworzy wniosek.

``PATCH /api/purchase_requests/{purchase_request_id}``
  Aktualizuje wniosek.

``DELETE /api/purchase_requests/{purchase_request_id}``
  Usuwa wniosek.

Finalizacja wniosku
-------------------

``POST /api/purchase_requests/{id}/prepare_finalization``
  Przygotowuje wniosek do finalizacji, zamyka dodawanie i tworzy
  potrzebne rozliczenia.

``PATCH /api/purchase_requests/{id}/finalization_draft``
  Zapisuje robocze dane dokumentowe finalizacji.

``POST /api/purchase_requests/{id}/finalize``
  Finalizuje wniosek, zapisuje snapshot, wylicza wartości i ustawia
  status oczekiwania na księgowość.

``POST /api/purchase_requests/{id}/send_to_settlement``
  Przekazuje wniosek do rozliczeń.

``POST /api/purchase_requests/{id}/return_to_open``
  Cofa przygotowany wniosek do otwartego stanu.

Linie rozliczeniowe wniosku
---------------------------

``GET /api/purchase_requests/{id}/settlement_lines``
  Pobiera linie rozliczenia.

``PUT /api/purchase_requests/{id}/settlement_lines``
  Zapisuje komplet linii rozliczenia.

``PATCH /api/purchase_request_settlement_lines/{id}``
  Aktualizuje pojedynczą linię.

``POST /api/purchase_requests/{id}/settlement_lines/extra``
  Dodaje dodatkową pozycję rozliczenia po przekazaniu do rozliczeń.

Rozliczenia i faktury
---------------------

``GET /api/settlements``
  Pobiera rozliczenia.

``GET /api/settlements/history``
  Pobiera historię zakończonych rozliczeń.

``GET /api/settlements/manager/{project_finance_manager_id}``
  Rozliczenia konkretnego skarbnika.

``POST /api/settlements``
  Tworzy rozliczenie.

``POST /api/settlements/{settlement_id}/invoices``
  Dodaje fakturę do rozliczenia.

``PATCH /api/invoices/{invoice_id}``
  Edytuje fakturę.

``GET /api/invoices``
  Pobiera faktury z filtrami statusu, skarbnika, wniosku i koła.

``POST /api/settlements/{settlement_id}/complete``
  Kończy rozliczenie.

``PATCH /api/settlements/{settlement_id}/status``
  Zmienia status rozliczenia.

Kontrakty danych: logowanie i użytkownik
----------------------------------------

``POST /api/login`` przyjmuje:

.. code-block:: text

   {
     "email": "student@example.com",
     "password": "haslo"
   }

Odpowiedź sukcesu:

.. code-block:: text

   {
     "id": 1,
     "firstName": "Jan",
     "lastName": "Kowalski",
     "email": "student@example.com",
     "circleName": "Koło Robotyki",
     "association_id": 1,
     "position": "member",
     "inSAP": true,
     "project_finance_manager_id": null,
     "role": "member"
   }

Jeżeli użytkownik ma ``project_finance_manager_id``, ``role`` ma wartość
``treasurer``.

``POST /api/register`` przyjmuje:

.. code-block:: text

   {
     "name": "Jan",
     "surname": "Kowalski",
     "login": "student@example.com",
     "password": "haslo",
     "position": "Sekcja mechaniczna",
     "is_in_sap": true,
     "association_name": "Koło Robotyki",
     "is_treasurer": false
   }

Dla ``is_treasurer=true`` backend tworzy dodatkowo rekord
``ProjectFinanceManager``.

Kontrakty danych: katalog i kategorie
-------------------------------------

``POST /api/items``:

.. code-block:: text

   {
     "name": "Silnik krokowy",
     "link": "https://example.com/silnik",
     "price": 120.0,
     "currency": "PLN",
     "product_subcategory_id": 1,
     "student_id": 5,
     "tax_rate": 23
   }

Reguły:

* musi istnieć co najmniej jeden sklep, bo endpoint przypisuje pierwszy
  sklep z bazy,
* ``student_id`` musi wskazywać istniejącego studenta,
* zapisany status to ``approved``,
* ``GET /api/items`` zwraca wyłącznie ``approved``.

``POST /api/categories``:

.. code-block:: text

   {
     "name": "Elektronika",
     "cpv": "31700000",
     "student_id": 2
   }

Reguły:

* ``student_id`` jest wymagany,
* student musi mieć ``project_finance_manager_id``,
* brak uprawnień kończy się ``403``.

``POST /api/subcategories``:

.. code-block:: text

   {
     "name": "Mikrokontrolery",
     "product_category_id": 1,
     "student_id": 2
   }

Jeżeli ``product_category_id`` jest podane, backend wymaga skarbnika.
Jeżeli jest puste, powstaje podkategoria oczekująca na przypisanie.

Kontrakty danych: dofinansowanie
--------------------------------

``POST /api/fundings`` oraz ``PATCH /api/fundings/{id}``:

.. code-block:: text

   {
     "funding_name": "Grant 2026",
     "organizer": "Politechnika",
     "signing_person": "Anna Testowa",
     "spending_deadline": "2026-12-31",
     "funding_price": 10000.0,
     "project_budget_id": 1,
     "tasks": [
       {
         "task_name": "Części elektroniczne",
         "task_budget": 4000.0
       }
     ]
   }

Walidacje:

* nazwa, organizator i osoba podpisująca nie mogą być puste,
* ``funding_price`` musi być dodatnie,
* ``project_budget_id`` musi istnieć,
* każde zadanie ma dodatni budżet,
* suma ``task_budget`` nie może przekroczyć ``funding_price``.

Odpowiedź zawiera pola obliczeniowe:

.. code-block:: text

   available_money = funding_price - spent_money
   purchase_requests_total_allocated = suma rezerwacji z wniosków
   available_after_purchase_requests = available_money - rezerwacje

Kontrakty danych: plany publiczne
---------------------------------

``POST /api/public_purchase_plan_lists``:

.. code-block:: text

   {
     "funding_id": 1,
     "public_plan_list_name": "Plan ZP 2026",
     "plan_year": 2026,
     "plan_number": "ZP/2026/01",
     "fund_responsible_person": "Anna Testowa",
     "euro_exchange_rate": 4.7
   }

Reguły:

* ``funding_id`` musi istnieć,
* ``euro_exchange_rate`` musi być dodatni, jeśli został podany,
* ``plan_year`` musi mieścić się w zakresie ``2000..2100``,
* dla tego samego ``funding_id`` endpoint aktualizuje istniejący plan.

``POST /api/public_purchase_plans``:

.. code-block:: text

   {
     "public_purchase_plan_list_id": 1,
     "cpv_code": "31700000",
     "plan_position_number": "1.1",
     "cost": 2500.0,
     "description": "Podzespoły elektroniczne",
     "product_category_id": 3
   }

Reguły:

* ``cost`` musi być większe od zera,
* ``cpv_code`` nie może być pusty,
* CPV musi być unikalny w ramach jednego planu dofinansowania,
* przy tworzeniu pozycji powstaje grupa
  ``GroupedShopsListByCpvCategoryAndFunding``,
* jeśli podano ``product_category_id``, kategoria zostaje powiązana z
  pozycją planu, a jej ``cpv`` zostaje ustawione na CPV pozycji.

Odpowiedź pozycji planu zawiera:

.. code-block:: text

   used_amount      suma wykorzystania przez wnioski
   remaining_amount cost - used_amount
   gslbccf_id       grupa koszyków dla pozycji planu

Kontrakty danych: listy zakupów
-------------------------------

``GET /api/lists`` obsługuje filtry:

.. code-block:: text

   student_id
   association_id
   shop_id
   public_purchase_plan_id
   purchase_request_id
   gslbccf_id
   open_only
   treasurer_view

``POST /api/lists``:

.. code-block:: text

   {
     "name": "TME - elektronika",
     "priority": 1,
     "cost": 0.0,
     "created_at": "2026-06-18T10:00:00",
     "funding_id": 1,
     "shop_id": 1,
     "student_id": 2,
     "public_purchase_plan_id": 5,
     "purchase_request_id": null,
     "gslbccf_id": null
   }

Reguły:

* student i dofinansowanie muszą istnieć,
* dofinansowanie musi należeć do koła studenta,
* zwykły użytkownik musi wskazać wniosek albo pozycję planu,
* skarbnik może utworzyć listę bez kontekstu wniosku,
* dla jednej grupy ``gslbccf_id`` nie można utworzyć drugiego koszyka
  tego samego sklepu,
* wybrane dofinansowanie musi mieć środki większe od zera.

``POST /api/lists/{list_id}/items``:

.. code-block:: text

   {
     "item_id": 10,
     "amount": 2,
     "student_id": 5
   }

albo utworzenie nowego przedmiotu przy dodaniu do listy:

.. code-block:: text

   {
     "name": "Czujnik",
     "link": "https://example.com",
     "price": 50.0,
     "currency": "PLN",
     "product_subcategory_id": 1,
     "tax_rate": 23,
     "amount": 3,
     "student_id": 5
   }

Reguły:

* lista musi być otwarta,
* ``amount`` musi być dodatnie,
* nowy przedmiot wymaga nazwy, ceny i podkategorii z kategorią,
* backend zwiększa ``ShopPurchaseListItem.amount`` i zapisuje wkład w
  ``ShopPurchaseListItemContribution``.

``DELETE /api/lists/{list_id}/items/{item_id}?student_id=5``:

* lista musi być otwarta,
* skarbnik będący właścicielem listy może usunąć całą pozycję,
* zwykły student usuwa tylko własny wkład,
* jeśli po odjęciu wkładu ilość spada do zera, usuwany jest cały
  ``ShopPurchaseListItem``.

Kontrakty danych: wniosek
-------------------------

``POST /api/create_purchase_requests``:

.. code-block:: text

   {
     "purchase_request_name": "Zakup elektroniki",
     "budget_allocated_for_the_order": 1200.0,
     "if_service": false,
     "used_cpv_id": "31700000",
     "project_budget_id": 1,
     "funding_id": 1,
     "created_at": "2026-06-18T10:00:00",
     "created_by_user_id": 2,
     "can_add": true,
     "project_finance_manager_id": 1,
     "shop_purchase_list_id": null,
     "public_purchase_plan_id": null,
     "plan_exception_justification": null,
     "funding_allocations": [
       {
         "funding_id": 1,
         "allocated_amount": 1200.0
       }
     ],
     "plan_positions": [
       {
         "shop_purchase_list_id": 3,
         "public_purchase_plan_id": 5,
         "allocated_amount": 1200.0
       }
     ]
   }

Najważniejsze walidacje:

* ``project_finance_manager_id`` jest wymagane,
* jeśli ``shop_purchase_list_id`` jest podane, koszyk musi być zamknięty
  i należeć do tego skarbnika,
* ``funding_id`` musi należeć do ``project_budget_id``,
* kwota nie może przekroczyć dostępnego budżetu sekcji,
* kwota nie może przekroczyć dostępnego dofinansowania,
* każda pozycja planu musi należeć do jednego z dofinansowań użytych we
  wniosku,
* przekroczenie pozycji planu wymaga
  ``plan_exception_justification``.

Odpowiedź ``PurchaseRequestOut`` zawiera między innymi:

.. code-block:: text

   plan_compliance_status
   budget_info
   source_shop_purchase_list
   funding_allocations
   plan_position
   plan_positions
   finalization_status

Kontrakty danych: finalizacja
-----------------------------

``POST /api/purchase_requests/{id}/prepare_finalization`` nie przyjmuje
payloadu. Odpowiedź ``PurchaseRequestFinalizationOut`` zawiera:

.. code-block:: text

   net_total
   gross_total
   main_cpv_code
   cpv_rows
   plan_rows
   funding_gross_rows
   snapshot_rows

``PATCH /api/purchase_requests/{id}/finalization_draft``:

.. code-block:: text

   {
     "document_request_name": "Wniosek ZP/12/2026",
     "euro_exchange_rate": 4.7,
     "contract_value_date": "2026-06-18"
   }

``POST /api/purchase_requests/{id}/finalize`` wymaga tego samego zestawu
danych, ale wszystkie pola są formalnie wymagane. Po sukcesie backend
ustawia:

.. code-block:: text

   can_add = false
   finalization_status = accounting_pending
   finalized_at = now()
   used_cpv_id = main_cpv_code
   budget_allocated_for_the_order = gross_total

Kontrakty danych: rozliczenia i faktury
---------------------------------------

``POST /api/settlements/{settlement_id}/invoices``:

.. code-block:: text

   {
     "number": "FV/01/2026",
     "issue_date": "2026-06-18",
     "seller_name": "Sklep testowy",
     "seller_nip": "1234567890",
     "net_total": 1000.0,
     "vat_total": 230.0,
     "status": "pending",
     "project_finance_manager_id": 1
   }

Status faktury jest enumem:

.. code-block:: text

   pending
   accepted
   rejected
   paid
   returned
   arrived

``PATCH /api/purchase_request_settlement_lines/{line_id}`` pozwala
ustawić ``invoice_id`` i ``actual_gross_amount``. ``actual_gross_amount``
nie może być ujemne.

``POST /api/settlements/{settlement_id}/complete``:

* wymaga powiązania settlementu z wnioskiem,
* wymaga faktury na każdej linii rozliczeniowej,
* ustawia ``PurchaseRequest.finalization_status = settled``.
