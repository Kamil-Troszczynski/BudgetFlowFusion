API backendu
============

Informacje ogólne
-----------------

Base URL:

.. code-block:: text

   http://localhost:8080/api

Format danych: JSON.

Backend używa FastAPI, Pydantic i SQLModel. Sesja bazy jest przekazywana
do endpointów przez ``Depends(get_session)``.

Autoryzacja
-----------

Autoryzacja jest uproszczona. Frontend przechowuje użytkownika w
``localStorage``. Backend w wielu miejscach przyjmuje ``student_id``,
``association_id`` albo ``project_finance_manager_id`` w query string lub
payloadzie. Wybrane endpointy sprawdzają, czy student ma powiązanie z
``ProjectFinanceManager``.

Logowanie
---------

``POST /api/login``
  Loguje użytkownika.

``POST /api/register``
  Rejestruje użytkownika i opcjonalnie tworzy rolę skarbnika.

Użytkownicy
-----------

``GET /api/students``
  Lista studentów.

Kategorie
---------

``GET /api/categories``
  Lista kategorii.

``POST /api/categories``
  Tworzy kategorię. Wymaga skarbnika.

``GET /api/subcategories``
  Lista podkategorii przypisanych do kategorii.

``GET /api/subcategories/pending``
  Lista podkategorii bez przypisanej kategorii.

``POST /api/subcategories``
  Tworzy podkategorię. Przypisanie do kategorii wymaga skarbnika.

``PATCH /api/subcategories/{subcategory_id}/assign-category``
  Przypisuje podkategorię do kategorii. Wymaga skarbnika.

Przedmioty
----------

``GET /api/items``
  Lista zaakceptowanych przedmiotów.

``GET /api/items/grouped?group_by=shop|cpv|category|status``
  Lista przedmiotów pogrupowanych.

``GET /api/items/pending``
  Przedmioty oczekujące. Może filtrować po ``association_id``.

``POST /api/items``
  Tworzy przedmiot.

``PATCH /api/items/{item_id}/approve``
  Zatwierdza przedmiot.

``DELETE /api/items/{item_id}/reject``
  Odrzuca przedmiot.

Sklepy
------

``GET /api/shops?include_pending=false``
  Lista sklepów. Domyślnie tylko zaakceptowane.

``POST /api/shops``
  Zgłasza sklep.

``PATCH /api/shops/{shop_id}``
  Edytuje sklep. Wymaga skarbnika.

``PATCH /api/shops/{shop_id}/approve``
  Akceptuje sklep. Wymaga skarbnika.

``DELETE /api/shops/{shop_id}/reject?student_id=...``
  Odrzuca sklep oczekujący. Wymaga skarbnika.

Dofinansowania i budżety
------------------------

``GET /api/fundings?association_id=...``
  Lista dofinansowań z wyliczonymi kwotami dostępnymi.

``POST /api/fundings``
  Tworzy dofinansowanie i zadania budżetowe.

``PATCH /api/fundings/{funding_id}``
  Aktualizuje dofinansowanie i zastępuje jego zadania.

``GET /api/association_budgets?association_id=...``
  Budżety kół.

``GET /api/project_budgets?association_id=...``
  Budżety projektów/sekcji.

``GET /api/dashboard/budget_summary?association_id=...``
  Agregat budżetowy dla pulpitu.

Plany publiczne
---------------

``POST /api/public_purchase_plan_lists``
  Tworzy albo aktualizuje plan publiczny dla dofinansowania.

``GET /api/public_purchase_plan_lists``
  Lista planów. Obsługuje filtry ``association_id`` i ``funding_id``.

``GET /api/public_purchase_plan_lists/{public_purchase_plan_list_id}``
  Szczegóły planu.

``POST /api/public_purchase_plans``
  Dodaje pozycję planu.

``PATCH /api/public_purchase_plans/{public_purchase_plan_id}``
  Aktualizuje pozycję planu.

``DELETE /api/public_purchase_plans/{public_purchase_plan_id}``
  Usuwa pozycję planu, jeśli nie jest użyta.

Listy zakupów
-------------

``GET /api/lists``
  Lista koszyków. Endpoint obsługuje filtry użytkownika, koła, sklepu,
  planu, wniosku, grupy i statusu otwarcia.

``POST /api/lists``
  Tworzy listę zakupów.

``PATCH /api/lists/{list_id}/close``
  Zamyka listę i tworzy albo wiąże rozliczenie.

``PATCH /api/lists/{list_id}/reopen``
  Otwiera listę ponownie.

``GET /api/lists/closed_for_purchase_requests``
  Zamknięte listy dostępne do utworzenia wniosku.

``GET /api/lists/{list_id}``
  Szczegóły listy.

``PATCH /api/lists/{list_id}/market_research``
  Zapisuje komentarz i nazwę pliku rozeznania rynku.

``DELETE /api/lists/{list_id}``
  Usuwa listę.

``GET /api/lists/{list_id}/items``
  Pozycje listy.

``POST /api/lists/{list_id}/items``
  Dodaje przedmiot do listy.

``PUT /api/lists/{list_id}/items/{item_id}``
  Aktualizuje ilość pozycji.

``DELETE /api/lists/{list_id}/items/{item_id}``
  Usuwa pozycję albo wkład użytkownika.

Wnioski
-------

``GET /api/purchase_requests?association_id=...``
  Lista wniosków.

``GET /api/purchase_requests/detail/{purchase_request_id}``
  Szczegóły jednego wniosku.

``GET /api/purchase_requests/{project_finance_manager_id}``
  Wnioski skarbnika.

``POST /api/create_purchase_requests``
  Tworzy wniosek.

``PATCH /api/purchase_requests/{purchase_request_id}``
  Aktualizuje wniosek.

``DELETE /api/purchase_requests/{purchase_request_id}``
  Usuwa wniosek i odpina powiązane rozliczenia.

Finalizacja wniosku
-------------------

``POST /api/purchase_requests/{purchase_request_id}/prepare_finalization``
  Przygotowuje finalizację, blokuje dodawanie i wiąże rozliczenia z
  listami.

``PATCH /api/purchase_requests/{purchase_request_id}/finalization_draft``
  Zapisuje roboczą nazwę dokumentu, kurs euro i datę wartości umowy.

``POST /api/purchase_requests/{purchase_request_id}/finalize``
  Finalizuje wniosek, zapisuje snapshoty i ustawia
  ``accounting_pending``.

``POST /api/purchase_requests/{purchase_request_id}/send_to_settlement``
  Przekazuje wniosek do rozliczeń.

``POST /api/purchase_requests/{purchase_request_id}/return_to_open``
  Cofa wniosek ze statusu ``prepared`` do ``draft``.

Linie rozliczeniowe wniosku
---------------------------

``GET /api/purchase_requests/{purchase_request_id}/settlement_lines``
  Lista linii rozliczeniowych.

``PUT /api/purchase_requests/{purchase_request_id}/settlement_lines``
  Zapisuje zestaw linii przed przekazaniem do rozliczeń.

``PATCH /api/purchase_request_settlement_lines/{settlement_line_id}``
  Aktualizuje pojedynczą linię.

``POST /api/purchase_requests/{purchase_request_id}/settlement_lines/extra``
  Dodaje dodatkową linię po przekazaniu do rozliczeń.

Rozliczenia i faktury
---------------------

``GET /api/settlements``
  Lista rozliczeń.

``GET /api/settlements/history``
  Rozliczenia zakończone.

``GET /api/settlements/manager/{project_finance_manager_id}``
  Rozliczenia skarbnika.

``POST /api/settlements``
  Tworzy rozliczenie.

``GET /api/invoices``
  Lista faktur. Obsługuje filtry statusu, skarbnika, wniosku i koła.

``POST /api/settlements/{settlement_id}/invoices``
  Dodaje fakturę do rozliczenia.

``PATCH /api/invoices/{invoice_id}``
  Aktualizuje fakturę.

``POST /api/settlements/{settlement_id}/complete``
  Kończy rozliczenie.

``PATCH /api/settlements/{settlement_id}/status``
  Zmienia status rozliczenia/faktur według logiki endpointu.

Statusy
-------

Statusy wniosku:

.. code-block:: text

   draft
   prepared
   accounting_pending
   settlement
   settled

Statusy zgodności planu:

.. code-block:: text

   draft
   compliant
   requires_approval

Statusy faktury:

.. code-block:: text

   pending
   accepted
   rejected
   paid
   returned
   arrived
