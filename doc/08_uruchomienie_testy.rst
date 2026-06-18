Uruchomienie i testy
====================

Środowisko uruchomieniowe
-------------------------

Do uruchomienia projektu potrzebne są:

* Docker i Docker Compose,
* Node.js zgodny z wersją obsługiwaną przez Vite,
* npm,
* przeglądarka internetowa.

Backend i baza danych
---------------------

Uruchomienie backendu i bazy:

.. code-block:: bash

   docker compose up --build

Backend działa domyślnie pod adresem:

.. code-block:: text

   http://localhost:8080

Baza PostgreSQL jest wystawiona lokalnie na porcie ``5431``.

Reset bazy danych
-----------------

Reset danych wykonuje się przez usunięcie wolumenu Dockera:

.. code-block:: bash

   docker compose down -v
   docker compose up --build

Po resecie backend przy starcie tworzy tabele i próbuje załadować dane z
pliku:

.. code-block:: text

   backend/scripts/mockup_data.sql

Frontend
--------

Instalacja zależności:

.. code-block:: bash

   cd frontend
   npm install

Tryb developerski:

.. code-block:: bash

   npm run dev

Build produkcyjny:

.. code-block:: bash

   npm run build

Testy backendu
--------------

Testy są w katalogu:

.. code-block:: text

   backend/tests

Uruchomienie testów w kontenerze:

.. code-block:: bash

   docker exec -it backend python -m pytest tests/

Zakres testów
-------------

Obecne testy obejmują między innymi:

* kategorie i podkategorie,
* dodawanie przedmiotów,
* akceptację i odrzucanie przedmiotów,
* izolację danych między kołami,
* budżety i dofinansowania,
* plany publiczne,
* wnioski zakupowe,
* rozliczenia.

Uwagi dotyczące testów
----------------------

Kody CPV w aktualnym modelu są tekstem. Nowe testy powinny używać
wartości typu ``"31700000"`` albo ``"43800000-1"``, a nie liczb
całkowitych.

Generowanie dokumentacji
------------------------

Dokumentację generuje skrypt:

.. code-block:: bash

   python3 doc_gen.py

Wyniki:

.. code-block:: text

   doc/build/html/index.html
   doc/build/pdf/BudgetFlowFusion_documentation.pdf

Skrypt nie wymaga zewnętrznych bibliotek. Generuje statyczny HTML oraz
prosty PDF tekstowy.

Struktura testów backendu
-------------------------

.. code-block:: text

   backend/tests/conftest.py
     Wspólne fixture: silnik SQLite in-memory, TestClient, mock_db.

   backend/tests/test_business_logic.py
     Kategorie, podkategorie, katalog przedmiotów, akceptacja,
     odrzucenie i izolacja danych między kołami.

   backend/tests/test_public_purchase_plans.py
     Budżety koła i sekcji, dofinansowania, dashboard, plan publiczny,
     pozycje CPV, duplikaty CPV i walidacja kwot.

   backend/tests/test_purchase_request.py
     Pobieranie wniosków, tworzenie wniosku, rezerwacje budżetu,
     zgodność z planem, przekroczenie planu, alokacje finansowania,
     pozycje planu i usuwanie wniosku.

   backend/tests/test_settlements.py
     Lista rozliczeń, filtrowanie po skarbniku, faktury, blokada
     zakończenia bez faktur i zmiana statusu na settled.

Uruchamianie wybranych testów
-----------------------------

Cały pakiet:

.. code-block:: bash

   docker exec -it backend python -m pytest tests/ -v

Jeden plik:

.. code-block:: bash

   docker exec -it backend python -m pytest tests/test_purchase_request.py -v

Jeden scenariusz:

.. code-block:: bash

   docker exec -it backend python -m pytest tests/test_purchase_request.py::test_create_purchase_request -v

Szybki tryb po ostatniej awarii:

.. code-block:: bash

   docker exec -it backend python -m pytest tests/ --lf -v

Testowa baza danych
-------------------

Testy nie używają kontenerowej bazy PostgreSQL. ``conftest.py`` tworzy
SQLite in-memory przez:

.. code-block:: text

   create_engine(
     "sqlite://",
     connect_args={"check_same_thread": False},
     poolclass=StaticPool
   )

Następnie ``SQLModel.metadata.create_all(engine)`` tworzy tabele, a
``app.dependency_overrides[get_session]`` podmienia sesję backendu na
sesję testową.

Konsekwencje:

* testy są szybkie i izolowane,
* nie sprawdzają specyficznych zachowań PostgreSQL,
* migracja ``migrate_project_budgets()`` nie jest wykonywana w tym samym
  trybie co w kontenerze produkcyjnym,
* jeśli zmieniasz modele, trzeba sprawdzić zarówno testy SQLite, jak i
  start aplikacji z PostgreSQL.

Matryca pokrycia reguł biznesowych
----------------------------------

.. code-block:: text

   Reguła
     Testy

   Kategorię może utworzyć skarbnik
     test_add_category_and_subcategory

   Katalog przedmiotów jest wspólny i widoczny po dodaniu
     test_normal_student_adds_item_is_visible_in_catalog
     test_treasurer_adds_item_is_approved

   Skarbnik nie widzi pending itemów obcego koła
     test_multitenancy_isolation_for_treasurer

   Budżet koła jest sumą budżetów sekcji/dofinansowań
     test_get_association_budgets_with_fundings
     test_dashboard_budget_is_sum_of_section_fundings

   Dofinansowanie jest przypisane do jednej sekcji
     test_funding_is_assigned_to_one_section_budget

   Plan publiczny jest jeden na dofinansowanie
     test_public_purchase_plan_list_update_keeps_single_plan_per_funding

   CPV w planie nie może się dublować
     test_create_public_purchase_plan_rejects_duplicate_cpv

   Kwota pozycji planu musi być dodatnia
     test_create_public_purchase_plan_rejects_non_positive_cost

   Wniosek rezerwuje środki budżetu i dofinansowania
     test_create_purchase_request

   Przekroczenie planu wymaga uzasadnienia
     test_create_purchase_request_rejects_plan_overrun_without_justification

   Przekroczenie planu z uzasadnieniem przechodzi jako requires_approval
     test_create_purchase_request_allows_plan_overrun_with_justification

   Wniosek zapisuje wiele alokacji finansowania
     test_create_purchase_request_stores_funding_allocations

   Wniosek zapisuje pozycje planu powiązane z koszykiem
     test_create_purchase_request_stores_plan_positions_when_shop_list_is_provided

   Rozliczenia wymagają faktur na liniach
     test_complete_settlement_rejects_line_without_invoice

   Zakończenie rozliczenia ustawia status settled
     test_update_settlement_status_marks_request_as_settled

Checklist przed oddaniem zmian
------------------------------

1. Uruchomić testy backendu.
2. Uruchomić ``npm run build`` we frontendzie.
3. Odpalić ``docker compose up --build`` i sprawdzić start backendu.
4. Sprawdzić logowanie zwykłego użytkownika i skarbnika.
5. Sprawdzić scenariusz: dofinansowanie -> plan publiczny -> koszyk ->
   wniosek -> finalizacja -> rozliczenie -> faktura.
6. Wygenerować dokumentację przez ``python3 doc_gen.py``.
