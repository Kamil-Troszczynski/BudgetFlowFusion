Dokumentacja analityczno-projektowa
===================================

Cel analizy
-----------

W projekcie najważniejsze było uchwycenie zależności, które przy
zakupach w kole naukowym często są rozproszone. Przedmiot na liście to
tylko początek. Trzeba jeszcze wiedzieć, z jakiego finansowania będzie
opłacony, czy pasuje do planu zamówień publicznych, jaką część planu
zużywa i czy później da się go rozliczyć fakturą.

Z tego powodu model aplikacji został ułożony wokół kilku prostych zasad:

* pieniądz w systemie pochodzi z dofinansowania,
* dofinansowanie należy do jednej sekcji/projektu,
* sekcje składają się na budżet koła,
* każde dofinansowanie może mieć własny plan zamówień publicznych,
* pozycja planu opisuje kod CPV i kwotę zaplanowaną na przyszły zakup,
* wniosek o zamówienie zużywa środki z dofinansowania i pozycje planu,
* rozliczenie potwierdza zakup fakturą i kwotą rzeczywistą.

Kontekst organizacyjny
----------------------

.. code-block:: text

   Koło naukowe
      |
      +-- członkowie
      |
      +-- skarbnicy
      |
      +-- sekcje/projekty
            |
            +-- budżety sekcji
                  |
                  +-- dofinansowania
                        |
                        +-- plany zamówień publicznych
                        |
                        +-- listy zakupów
                        |
                        +-- wnioski
                              |
                              +-- finalizacja
                              |
                              +-- rozliczenie
                                    |
                                    +-- faktury

System nie modeluje pełnego obiegu dokumentów uczelni. Modeluje tę
część procesu, którą skarbnik koła musi mieć pod kontrolą: dostępne
środki, uzasadnienie wydatku, zgodność z planem CPV, historię wniosku i
stan rozliczenia.

Aktorzy
-------

Zwykły członek koła
~~~~~~~~~~~~~~~~~~~

Zwykły członek pracuje przede wszystkim na katalogu i otwartych listach
zakupów. Może dodać przedmiot do wspólnego katalogu, dopisać swoją
ilość do listy zakupów oraz usunąć wkład, który sam dodał.

W modelu danych jest to rekord ``Student`` bez
``project_finance_manager_id``.

Skarbnik
~~~~~~~~

Skarbnik odpowiada za finanse koła. Tworzy dofinansowania, plany
publiczne, listy zakupów, wnioski, finalizuje wnioski i prowadzi
rozliczenia.

W modelu danych jest to ``Student`` połączony z
``ProjectFinanceManager`` przez ``Student.project_finance_manager_id``.

Osoba rozliczająca
~~~~~~~~~~~~~~~~~~

W aplikacji nie jest osobną rolą logowania. Jej praca jest
reprezentowana przez moduł rozliczeń: faktury, linie rozliczenia,
statusy faktur i status ``settled`` na wniosku.

Główne obiekty dziedziny
------------------------

.. code-block:: text

   Association
     Koło naukowe. Granica danych użytkowników, projektów i budżetów.

   Student
     Użytkownik aplikacji. Może być zwykłym członkiem albo skarbnikiem.

   Project
     Sekcja lub projekt działający w ramach koła.

   ProjectBudget
     Budżet sekcji. Kwota wynika z dofinansowań przypiętych do sekcji.

   AssociationBudget
     Budżet całego koła. Jest sumą budżetów sekcji.

   Funding
     Konkretne dofinansowanie. Jest źródłem pieniędzy dla zakupów.

   PublicPurchasePlanList
     Roczny plan zamówień publicznych dla jednego dofinansowania.

   PublicPurchasePlan
     Pozycja planu: kod CPV, numer pozycji, opis i planowana kwota.

   ShopPurchaseList
     Lista zakupów dla jednego sklepu w ramach grupy zakupowej.

   Item
     Przedmiot w katalogu zakupowym.

   PurchaseRequest
     Wniosek o zamówienie. Łączy środki, CPV, listy zakupów i statusy.

   Settlement
     Rozliczenie wniosku lub zamkniętej listy.

   Invoice
     Faktura przypisana do rozliczenia.

Decyzje projektowe
------------------

Budżet jest liczony od dofinansowań
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Budżet sekcji nie jest niezależną kwotą wpisaną ręcznie. Sekcja ma tyle
środków, ile wynosi suma jej dofinansowań.

.. code-block:: text

   Funding 1  10 000 PLN
   Funding 2   5 000 PLN
      |
      v
   ProjectBudget 15 000 PLN

Analogicznie budżet koła jest sumą budżetów sekcji.

Plan publiczny należy do dofinansowania
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Plan zamówień publicznych nie jest wspólny dla całego koła. Jest
powiązany z dofinansowaniem, ponieważ to dofinansowanie określa, z
jakiej puli pieniędzy zakup będzie finansowany.

.. code-block:: text

   Funding
      |
      | 1 : 0..1
      v
   PublicPurchasePlanList
      |
      | 1 : *
      v
   PublicPurchasePlan

Pozycja planu nie jest konkretnym koszykiem zakupowym. Opisuje zamiar:
kod CPV i kwotę planowaną na zakupy w danym kodzie.

Wniosek zużywa plan i rezerwuje środki
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Wniosek o zamówienie jest dokumentem operacyjnym: skarbnik chce
zrealizować zakup teraz. Wniosek wskazuje dofinansowanie i pozycje planu,
z których korzysta. Kwota wniosku zmniejsza dostępny budżet już na
etapie złożenia, ponieważ pieniądze są traktowane jako zarezerwowane.

.. code-block:: text

   Funding.funding_price
      - Funding.spent_money
      - SUM(PurchaseRequestFundingAllocation.allocated_amount)
      = available_after_purchase_requests

Koszyk jest roboczą listą zakupów
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Lista zakupów jest roboczym koszykiem dla jednego sklepu. Do jednej
grupy zakupowej może należeć wiele koszyków, np. gdy wniosek obejmuje
zakupy z kilku sklepów.

.. code-block:: text

   GroupedShopsListByCpvCategoryAndFunding
      |
      +-- ShopPurchaseList: sklep A
      +-- ShopPurchaseList: sklep B
      +-- ShopPurchaseList: sklep C

Użytkownicy dopisują do koszyka swoje ilości. Łączna ilość jest w
``ShopPurchaseListItem``, a informacja kto ile dodał jest w
``ShopPurchaseListItemContribution``.

Finalizacja zapisuje stan historyczny
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Plan, dofinansowanie i koszyk mogą później zostać zmienione. Dlatego
finalizacja tworzy ``PurchaseRequestFinalizationSnapshot``. Snapshot
zapisuje dane potrzebne do dokumentu: CPV, numer planu, osobę
odpowiedzialną, finansowanie i kwoty.

.. code-block:: text

   PurchaseRequest
      |
      | finalize
      v
   PurchaseRequestFinalizationSnapshot
      |
      +-- dane CPV
      +-- dane planu
      +-- dane dofinansowania
      +-- kwoty netto, brutto i EUR

Granice systemu
---------------

System obejmuje:

* użytkowników koła,
* katalog przedmiotów i sklepów,
* listy zakupów,
* dofinansowania i zadania budżetowe,
* plany zamówień publicznych,
* wnioski o zamówienie,
* finalizację wniosku,
* rozliczenia i faktury.

System nie obejmuje w pełni:

* podpisu elektronicznego,
* integracji z SAP,
* automatycznego pobierania faktur,
* oficjalnego obiegu akceptacji uczelnianej,
* wersjonowanych migracji bazodanowych typu Alembic,
* pełnej autoryzacji tokenowej.

Mapa odpowiedzialności modułów
------------------------------

.. code-block:: text

   Moduł frontendowy                        Odpowiedzialność

   HomePage.vue                             pulpit, budżet, nawigacja
   AddedItems.vue                           katalog przedmiotów
   AddedShopPurchaseLists.vue               listy zakupów
   ShopPurchaseListDetails.vue              pozycje listy i wkłady studentów
   PublicPurchasePlans.vue                  dofinansowania i plany CPV
   PurchaseRequest.vue                      wnioski i finalizacja
   Settlement.vue                           rozliczenia i faktury
   Shops.vue                                sklepy

.. code-block:: text

   Moduł backendowy                         Odpowiedzialność

   relations.py                             model relacyjny
   public_purchase_plans_routes.py          budżety, dofinansowania, plany
   lists_routes.py                          koszyki i wkłady użytkowników
   purchase_request_routes.py               wnioski, alokacje, finalizacja
   settlements_routes.py                    rozliczenia, faktury, historia
   items_routes.py                          katalog przedmiotów
   shops_routes.py                          sklepy
   login_register_routes.py                 logowanie i rejestracja

Stany najważniejszych obiektów
------------------------------

.. code-block:: text

   Shop.status
     pending -> approved
     pending -> rejected

   Item.status
     approved
     pending -> approved
     pending -> rejected

   ShopPurchaseList
     settlement_id = NULL       lista otwarta
     settlement_id != NULL      lista zamknięta

   PurchaseRequest.finalization_status
     draft -> prepared -> accounting_pending -> settlement -> settled

   PurchaseRequest.plan_compliance_status
     draft
     compliant
     requires_approval

Najważniejsze reguły spójności
------------------------------

1. Dofinansowanie musi należeć do wybranego budżetu sekcji.
2. Plan publiczny jest przypisany do dokładnie jednego dofinansowania.
3. W ramach jednego planu nie powinno być dwóch pozycji z tym samym CPV.
4. Wniosek nie może przekroczyć dostępnych środków dofinansowania.
5. Wniosek nie może przekroczyć dostępnego budżetu sekcji.
6. Przekroczenie pozycji planu wymaga uzasadnienia.
7. Lista zamknięta nie przyjmuje nowych pozycji.
8. Student może usunąć z listy tylko własny wkład.
9. Zakończenie rozliczenia wymaga faktury na każdej linii rozliczenia.
10. Finalizacja wniosku zapisuje snapshot danych historycznych.
