Uruchomienie i testy
====================

Wymagania
---------

Do uruchomienia projektu potrzebne są:

* Docker,
* Docker Compose,
* Node.js i npm,
* przeglądarka internetowa.

Backend i baza
--------------

Uruchomienie kontenerów:

.. code-block:: bash

   docker compose up --build

Adres backendu:

.. code-block:: text

   http://localhost:8080

PostgreSQL jest wystawiony lokalnie na porcie:

.. code-block:: text

   5431

Reset bazy:

.. code-block:: bash

   docker compose down -v
   docker compose up --build

Po starcie backend tworzy tabele, wykonuje migrację i próbuje załadować:

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

Build:

.. code-block:: bash

   npm run build

Testy backendu
--------------

Katalog testów:

.. code-block:: text

   backend/tests

Uruchomienie całego pakietu w kontenerze backendu:

.. code-block:: bash

   docker exec -it backend python -m pytest tests/ -v

Uruchomienie pojedynczego pliku:

.. code-block:: bash

   docker exec -it backend python -m pytest tests/test_purchase_request.py -v

Uruchomienie jednego testu:

.. code-block:: bash

   docker exec -it backend python -m pytest tests/test_purchase_request.py::test_create_purchase_request -v

Tryb po ostatniej awarii:

.. code-block:: bash

   docker exec -it backend python -m pytest tests/ --lf -v

Testowa baza danych
-------------------

Testy backendu używają SQLite in-memory. Fixture z ``conftest.py``
podmienia zależność ``get_session`` i tworzy tabele z modeli SQLModel.

Konsekwencje:

* testy są szybkie,
* testy nie wymagają PostgreSQL,
* testy nie pokrywają w pełni różnic dialektu PostgreSQL,
* po zmianach migracji trzeba sprawdzić również start kontenerów.

Zakres testów
-------------

``test_business_logic.py``
  Kategorie, podkategorie, katalog przedmiotów, akceptacja,
  odrzucanie i izolacja danych między kołami.

``test_public_purchase_plans.py``
  Budżety, dofinansowania, dashboard, plany publiczne, CPV i walidacja
  kwot.

``test_purchase_request.py``
  Tworzenie wniosków, alokacje, plan publiczny, przekroczenia planu,
  usuwanie i aktualizacje.

``test_settlements.py``
  Rozliczenia, faktury, filtrowanie, blokady i statusy.

Generowanie dokumentacji
------------------------

Dokumentacja jest generowana skryptem:

.. code-block:: bash

   python3 doc_gen.py

Wyniki:

.. code-block:: text

   doc/build/html/index.html
   doc/build/pdf/BudgetFlowFusion_documentation.pdf

Skrypt używa tylko standardowej biblioteki Pythona.
