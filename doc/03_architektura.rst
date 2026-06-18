Architektura systemu
====================

Widok logiczny
--------------

System składa się z trzech głównych warstw:

* frontend Vue,
* backend FastAPI,
* baza danych PostgreSQL.

Diagram komponentów
-------------------

.. code-block:: text

   +--------------------------+
   |      Przeglądarka        |
   |  Vue 3 / Vite frontend   |
   +------------+-------------+
                |
                | REST / JSON
                v
   +--------------------------+
   |       Backend API        |
   | FastAPI + SQLModel       |
   |                          |
   | - auth                   |
   | - katalog przedmiotów    |
   | - sklepy                 |
   | - koszyki zakupowe       |
   | - plany publiczne        |
   | - wnioski                |
   | - rozliczenia i faktury  |
   +------------+-------------+
                |
                | SQLAlchemy / SQLModel
                v
   +--------------------------+
   |       PostgreSQL         |
   | Dane trwałe aplikacji    |
   +--------------------------+

Backend
-------

Backend znajduje się w katalogu ``backend``. Główne pliki:

* ``backend/run.py`` - punkt uruchomienia serwera Uvicorn,
* ``backend/src/__init__.py`` - konfiguracja aplikacji FastAPI, CORS,
  połączenie z bazą, inicjalizacja i migracje,
* ``backend/src/relations.py`` - modele danych SQLModel,
* ``backend/src/routes`` - endpointy API.

Moduły tras:

* ``login_register_routes.py`` - logowanie i rejestracja,
* ``items_routes.py`` - przedmioty,
* ``categories_subcategories_routes.py`` - kategorie i podkategorie,
* ``shops_routes.py`` - sklepy,
* ``lists_routes.py`` - koszyki/listy zakupów,
* ``fundings_routes.py`` - dofinansowania i zadania,
* ``public_purchase_plans_routes.py`` - budżety, plany publiczne i
  dashboard budżetowy,
* ``purchase_request_routes.py`` - wnioski, alokacje, finalizacja i
  linie rozliczeń,
* ``settlements_routes.py`` - rozliczenia i faktury.

Frontend
--------

Frontend znajduje się w katalogu ``frontend``. Najważniejsze pliki:

* ``frontend/src/main.js`` - start aplikacji,
* ``frontend/src/router/index.js`` - routing,
* ``frontend/src/App.vue`` - kontener aplikacji,
* ``frontend/src/components/home_page/HomePage.vue`` - główny panel
  użytkownika,
* ``frontend/src/composables/useAuth.js`` - stan logowania.

Główne komponenty:

* ``AddedItems.vue`` - katalog dodanych przedmiotów,
* ``AddedShopPurchaseLists.vue`` - koszyki sklepowe,
* ``PublicPurchasePlans.vue`` - dofinansowania i plany publiczne,
* ``PurchaseRequest.vue`` - wnioski o zamówienie,
* ``Settlement.vue`` - rozliczenia i faktury,
* ``Shops.vue`` - sklepy.

Przepływ danych
---------------

.. code-block:: text

   Użytkownik
      |
      v
   Vue component
      |
      | fetch("http://localhost:8080/api/...")
      v
   FastAPI route
      |
      v
   SQLModel Session
      |
      v
   PostgreSQL

W projekcie nie ma oddzielnej warstwy serwisów. Logika biznesowa jest
obecnie skupiona w endpointach i funkcjach pomocniczych modułów
``routes``. Modele SQLModel pełnią rolę mapowania encji relacyjnych.

Inicjalizacja bazy
------------------

Przy starcie backend:

1. tworzy tabele przez ``SQLModel.metadata.create_all(engine)``,
2. wykonuje funkcję migracyjną ``migrate_project_budgets()``,
3. próbuje załadować dane z ``backend/scripts/mockup_data.sql``.

Funkcja migracyjna obsługuje ewolucję projektu: dodaje kolumny, tabele
pomocnicze, statusy faktur i pola używane przez finalizację wniosków.

Konfiguracja runtime
--------------------

Backend korzysta z wartości ``DATABASE_URL``. W ``docker-compose.yml``
zmienna wskazuje na kontener bazy:

.. code-block:: text

   postgresql://budgetflowfusion:budgetflowfusion@db:5432/budgetflowfusion

Porty lokalne:

.. code-block:: text

   8080  -> FastAPI backend
   5431  -> PostgreSQL host port, wewnątrz kontenera 5432

Kontener backendu montuje katalog ``./backend`` jako ``/backend``.
Dzięki temu zmiany w kodzie backendu są widoczne w kontenerze po
restarcie procesu.

Zależności techniczne
---------------------

Backend:

* ``python:3.10-slim`` jako obraz bazowy,
* ``fastapi[standard]`` jako framework HTTP,
* ``sqlmodel`` jako ORM i deklaracja schematu,
* ``psycopg2`` jako sterownik PostgreSQL,
* ``uvicorn[standard]`` jako serwer ASGI,
* ``pytest`` jako framework testowy.

Frontend:

* ``vue`` w wersji z gałęzi ``3.5``,
* ``vue-router`` do routingu SPA,
* ``vite`` jako dev server i bundler,
* ``@vitejs/plugin-vue`` do obsługi komponentów ``.vue``.

Rejestracja tras backendu
-------------------------

Plik ``backend/src/__init__.py`` tworzy globalną instancję ``app`` i na
końcu importuje ``src.routes``. Import modułu ``routes`` powoduje
załadowanie plików tras, które dekorują tę samą instancję ``app``.

.. code-block:: text

   app = FastAPI(lifespan=lifespan)
   app.add_middleware(CORSMiddleware, ...)
   import src.routes

Konsekwencje:

* endpointy są rejestrowane przez efekt uboczny importu,
* trasy używają wspólnej zależności ``get_session()``,
* testy mogą podmienić zależność ``get_session`` przez
  ``app.dependency_overrides``.

Cykl życia requestu
-------------------

.. code-block:: text

   HTTP request
      |
      v
   FastAPI route function
      |
      +--> Pydantic BaseModel waliduje payload
      |
      +--> Depends(get_session) otwiera Session(engine)
      |
      +--> SQLModel select/session.get/session.add
      |
      +--> session.commit albo rollback przy wyjątku
      |
      v
   Pydantic response_model / dict / SQLModel object

Warstwa API zwraca mieszankę:

* modeli SQLModel bezpośrednio, np. ``Shop`` albo ``ShopPurchaseList``,
* dedykowanych modeli wyjściowych ``BaseModel``, np.
  ``PurchaseRequestOut``,
* prostych słowników statusu, np. ``{"status": "success"}``.

Mapowanie frontend -> backend
-----------------------------

.. code-block:: text

   HomePage.vue
     /api/dashboard/budget_summary
     /api/project_budgets
     /api/fundings

   PublicPurchasePlans.vue
     /api/fundings
     /api/project_budgets
     /api/public_purchase_plan_lists
     /api/public_purchase_plans

   AddedShopPurchaseLists.vue + ShopPurchaseListDetails.vue
     /api/lists
     /api/lists/{id}/items
     /api/lists/{id}/close
     /api/lists/{id}/reopen
     /api/lists/{id}/market_research

   PurchaseRequest.vue
     /api/purchase_requests
     /api/create_purchase_requests
     /api/purchase_requests/{id}/prepare_finalization
     /api/purchase_requests/{id}/finalize
     /api/purchase_requests/{id}/send_to_settlement
     /api/purchase_requests/{id}/settlement_lines

   Settlement.vue
     /api/settlements
     /api/settlements/history
     /api/invoices
     /api/settlements/{id}/invoices
     /api/settlements/{id}/complete

Stan sesji frontendu
--------------------

Sesja użytkownika nie jest tokenem JWT. ``useAuth.js`` zapisuje obiekt
użytkownika w ``localStorage``:

.. code-block:: text

   {
     id,
     association_id,
     firstName,
     lastName,
     email,
     circleName,
     position,
     inSAP,
     projectFinanceManagerId,
     role
   }

Router sprawdza tylko, czy obiekt istnieje. Przy odświeżeniu strony
``restoreSession()`` odtwarza użytkownika z ``localStorage``.

Konsekwencja bezpieczeństwa: aplikacja ma kontrolę dostępu głównie na
poziomie interfejsu oraz wybranych walidacji backendowych. Pełna
produkcyjna autoryzacja wymagałaby sesji serwerowej albo tokenów i
spójnego middleware uprawnień.
