Architektura systemu
====================

Widok warstwowy
---------------

.. code-block:: text

   +--------------------------------------------------+
   | Przeglądarka                                     |
   | Vue 3, Vue Router, komponenty .vue               |
   +-------------------------+------------------------+
                             |
                             | HTTP REST / JSON
                             v
   +--------------------------------------------------+
   | Backend FastAPI                                  |
   | endpointy, walidacja Pydantic, logika domenowa   |
   +-------------------------+------------------------+
                             |
                             | SQLModel / SQLAlchemy
                             v
   +--------------------------------------------------+
   | PostgreSQL                                       |
   | tabele tworzone z modeli SQLModel + migracja     |
   +--------------------------------------------------+

Backend
-------

Katalog: ``backend``.

Najważniejsze pliki:

* ``backend/run.py`` - uruchomienie Uvicorn na porcie ``8080``,
* ``backend/src/__init__.py`` - konfiguracja FastAPI, CORS, silnik bazy,
  lifecycle i migracja,
* ``backend/src/relations.py`` - encje SQLModel,
* ``backend/src/routes`` - moduły endpointów.

Rejestracja tras
----------------

``backend/src/__init__.py`` tworzy globalny obiekt ``app``. Import
``src.routes`` ładuje wszystkie moduły z katalogu tras i rejestruje
dekoratory ``@app.get``, ``@app.post``, ``@app.patch``, ``@app.delete``.

.. code-block:: text

   src.__init__
      |
      +-- app = FastAPI(...)
      +-- engine = create_engine(DATABASE_URL)
      +-- get_session()
      +-- prepare_database()
      +-- import src.routes
              |
              +-- login_register_routes
              +-- members_routes
              +-- items_routes
              +-- shops_routes
              +-- lists_routes
              +-- fundings_routes
              +-- public_purchase_plans_routes
              +-- purchase_request_routes
              +-- settlements_routes

Moduły backendu
---------------

``login_register_routes.py``
  Rejestracja i logowanie.

``members_routes.py``
  Lista studentów.

``items_routes.py``
  Katalog przedmiotów, statusy pending/approved/rejected, grupowanie.

``shops_routes.py``
  Sklepy, zgłaszanie, akceptacja, edycja i odrzucenie.

``categories_subcategories_routes.py``
  Kategorie, podkategorie i przypisanie CPV.

``lists_routes.py``
  Listy zakupów, pozycje, wkład użytkowników, zamykanie i otwieranie.

``fundings_routes.py``
  Dofinansowania, zadania budżetowe i dostępne środki.

``public_purchase_plans_routes.py``
  Budżety, dashboard, listy planów i pozycje planu publicznego.

``purchase_request_routes.py``
  Wnioski, alokacje finansowania, pozycje planu, finalizacja i linie
  rozliczeniowe.

``settlements_routes.py``
  Rozliczenia, faktury, historia i statusy.

Frontend
--------

Katalog: ``frontend``.

Najważniejsze pliki:

* ``frontend/src/main.js`` - start aplikacji,
* ``frontend/src/router/index.js`` - routing SPA,
* ``frontend/src/App.vue`` - główny kontener,
* ``frontend/src/composables/useAuth.js`` - stan zalogowanego
  użytkownika,
* ``frontend/src/composables/useToast.js`` - komunikaty UI.

Główne widoki:

* ``HomePage.vue`` - panel użytkownika i dashboard,
* ``AddedItems.vue`` - katalog przedmiotów,
* ``AddedShopPurchaseLists.vue`` i ``ShopPurchaseListDetails.vue`` -
  listy zakupów,
* ``PublicPurchasePlans.vue`` - dofinansowania, budżety i plany,
* ``PurchaseRequest.vue`` - wnioski,
* ``Settlement.vue`` - rozliczenia i faktury,
* ``Shops.vue`` - sklepy.

Przepływ requestu
-----------------

.. code-block:: text

   komponent Vue
      |
      | fetch("http://localhost:8080/api/...")
      v
   endpoint FastAPI
      |
      | Pydantic BaseModel / query params
      v
   Session(engine)
      |
      | select / get / add / delete / commit
      v
   PostgreSQL
      |
      | response_model albo dict
      v
   JSON w przeglądarce

Konfiguracja środowiska
-----------------------

Backend wymaga ``DATABASE_URL``. W ``docker-compose.yml`` baza jest
dostępna dla backendu jako:

.. code-block:: text

   postgresql://budgetflowfusion:budgetflowfusion@db:5432/budgetflowfusion

Porty:

.. code-block:: text

   8080  backend FastAPI
   5431  PostgreSQL wystawiony na hosta

Inicjalizacja bazy
------------------

Przy starcie backend:

1. tworzy tabele przez ``SQLModel.metadata.create_all(engine)``,
2. wykonuje ``migrate_project_budgets()`` dla PostgreSQL,
3. próbuje załadować ``backend/scripts/mockup_data.sql``.

Migracja w ``src.__init__`` dodaje brakujące kolumny i tabele używane
przez nowsze funkcje: alokacje finansowania, pozycje planu wniosku,
snapshot finalizacji, linie rozliczeniowe i zadania dofinansowań.

Ograniczenia architektury
-------------------------

* Brak oddzielnej warstwy serwisowej: logika domenowa znajduje się w
  trasach.
* Autoryzacja jest uproszczona: frontend przechowuje użytkownika w
  ``localStorage``, a backend często przyjmuje identyfikatory w payloadzie
  lub query string.
* Część endpointów zwraca modele SQLModel bez dedykowanego DTO.
* Testy używają SQLite, a runtime używa PostgreSQL.
