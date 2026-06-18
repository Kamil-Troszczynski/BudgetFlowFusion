Model danych
============

Źródło modelu
-------------

Model bazodanowy jest zdefiniowany w ``backend/src/relations.py`` jako
klasy ``SQLModel``. Tabele są tworzone przez
``SQLModel.metadata.create_all(engine)``. Dodatkowe zmiany dla istniejącej
bazy PostgreSQL są wykonywane w ``migrate_project_budgets()``.

Legenda diagramów
-----------------

.. code-block:: text

   PK   klucz główny
   FK   klucz obcy
   1    dokładnie jeden
   0..1 zero albo jeden
   *    wiele

Diagram głównych encji
----------------------

.. code-block:: text

   +-------------+ 1     * +---------+
   | Association |---------| Student |
   | PK id       |         | PK id   |
   +------+------+         +----+----+
          | 1                   | 0..1
          |                     v
          |              +-----------------------+
          |              | ProjectFinanceManager |
          |              | PK id                 |
          |              +-----------+-----------+
          |                          |
          | 1                        | *
          v                          v
   +---------+ 1   1 +---------------+ 1   * +---------+
   | Project |-------| ProjectBudget |-------| Funding |
   | PK id   |       | PK id         |       | PK id   |
   +----+----+       +-------+-------+       +----+----+
        |                    |                    |
        |                    | *                  | 1
        |                    v                    v 0..1
        |          +-------------------+   +------------------------+
        |          | AssociationBudget |   | PublicPurchasePlanList |
        |          | PK id             |   | PK id                  |
        |          +-------------------+   +-----------+------------+
        |                                           | 1
        |                                           | *
        |                                           v
        |                                  +--------------------+
        |                                  | PublicPurchasePlan |
        |                                  | PK id, cpv_code    |
        |                                  +--------------------+

Opis głównych encji organizacyjno-finansowych
---------------------------------------------

``Association``
  Koło naukowe. Grupuje studentów i projekty.

``Student``
  Konto użytkownika. Przechowuje dane osobowe, login, hash hasła,
  przynależność do koła i opcjonalne powiązanie ze skarbnikiem.

``ProjectFinanceManager``
  Konto/rola skarbnika. Powiązanie ze studentem nadaje uprawnienia
  skarbnika.

``Project``
  Sekcja lub projekt koła. Należy do ``Association``.

``ProjectBudget``
  Budżet projektu. Ma relację 1:1 z ``Project`` i należy do
  ``AssociationBudget``.

``AssociationBudget``
  Budżet koła. Grupuje budżety projektów i dofinansowania.

``Funding``
  Dofinansowanie. Należy do budżetu projektu i budżetu koła. Jest
  głównym źródłem pieniędzy dla list zakupów, planów i wniosków.

``FundingTask``
  Zadanie budżetowe w ramach dofinansowania. Suma zadań nie może
  przekraczać kwoty dofinansowania.

Diagram planu publicznego i wniosku
-----------------------------------

.. code-block:: text

   Funding
      | 1
      | 0..1
      v
   PublicPurchasePlanList
      | 1
      | *
      v
   PublicPurchasePlan
      ^
      | *
      | przez PurchaseRequestPlanPosition
      |
   PurchaseRequest
      |
      | * przez PurchaseRequestFundingAllocation
      v
   Funding

   PurchaseRequest
      |
      +-- PurchaseRequestFinalizationSnapshot
      +-- PurchaseRequestSettlementLine
      +-- Settlement

Opis encji planu i wniosku
--------------------------

``PublicPurchasePlanList``
  Nagłówek planu publicznego. Ma rok, numer planu, osobę
  odpowiedzialną, kurs euro i relację 1:1 z ``Funding``.

``PublicPurchasePlan``
  Pozycja planu publicznego. Przechowuje nazwę, kod CPV, numer pozycji i
  planowaną kwotę.

``PurchaseRequest``
  Wniosek o zamówienie. Łączy budżet projektu, dofinansowanie, pozycje
  planu, grupę list zakupów, status finalizacji i dane dokumentowe.

``PurchaseRequestFundingAllocation``
  Tabela asocjacyjna ``PurchaseRequest`` -> ``Funding`` z kwotą
  ``allocated_amount``. Pozwala podzielić wniosek między wiele źródeł
  finansowania.

``PurchaseRequestPlanPosition``
  Tabela asocjacyjna ``PurchaseRequest`` -> ``ShopPurchaseList`` ->
  ``PublicPurchasePlan`` z kwotą wykorzystania pozycji planu.

``PurchaseRequestFinalizationSnapshot``
  Historyczny zapis danych finalizacji. Przechowuje kopie nazw,
  numerów, CPV i kwot użytych w dokumencie.

``PurchaseRequestSettlementLine``
  Linia rozliczeniowa wniosku. Zawiera planowaną i rzeczywistą kwotę
  brutto oraz opcjonalne powiązanie z fakturą.

Diagram list zakupów
--------------------

.. code-block:: text

   GroupedShopsListByCpvCategoryAndFunding
      | 1
      | *
      v
   ShopPurchaseList
      | *                         * |
      | przez ShopPurchaseListItem  |
      v                            v
   Item                         Student
      ^                            ^
      |                            |
      +-- ShopPurchaseListItemContribution

Opis encji zakupowych
---------------------

``GroupedShopsListByCpvCategoryAndFunding``
  Grupa koszyków zakupowych. Łączy listy z tym samym kontekstem CPV i
  finansowania.

``ShopPurchaseList``
  Koszyk dla jednego sklepu. Ma koszt, priorytet, datę utworzenia,
  finansowanie, sklep, właściciela-studenta i opcjonalne rozliczenie.

``ShopPurchaseListItem``
  Pozycja koszyka. Kluczem jest para ``shop_purchase_list_id`` i
  ``item_id``. Pole ``amount`` zawiera łączną ilość.

``ShopPurchaseListItemContribution``
  Wkład konkretnego studenta w pozycję koszyka. Kluczem jest lista,
  przedmiot i student.

``Item``
  Przedmiot w katalogu. Ma cenę, walutę, link, stawkę VAT, status,
  podkategorię, autora i sklep.

``Shop``
  Sklep. Ma nazwę, link, opinię, status, próg darmowej dostawy i listy
  zakupów.

``ProductCategory``
  Kategoria produktu z kodem CPV.

``ProductSubcategory``
  Podkategoria produktu. Może być pending, gdy nie ma przypisanej
  kategorii.

Diagram rozliczeń
-----------------

.. code-block:: text

   PurchaseRequest 0..1
      |
      v
   Settlement
      | 1
      | *
      v
   Invoice

   Settlement
      |
      +-- ShopPurchaseList
      +-- PurchaseRequestSettlementLine

Opis encji rozliczeniowych
--------------------------

``Settlement``
  Rozliczenie. Może być powiązane z wnioskiem i skarbnikiem, który
  opłaca rozliczenie.

``Invoice``
  Faktura. Zawiera numer, datę wystawienia, sprzedawcę, NIP, kwoty netto
  i VAT, status oraz powiązanie z rozliczeniem.

Enumy
-----

``Currency``
  ``PLN``, ``EUR``, ``USD``.

``InvoiceStatus``
  ``pending``, ``accepted``, ``rejected``, ``paid``, ``returned``,
  ``arrived``.

``ItemStatus``
  ``draft``, ``pending``, ``approved``, ``rejected``.

Najważniejsze relacje
---------------------

.. code-block:: text

   Association 1..* Student
   Association 1..* Project
   Project 1..1 ProjectBudget
   AssociationBudget 1..* ProjectBudget
   ProjectBudget 1..* Funding
   Funding 1..0..1 PublicPurchasePlanList
   PublicPurchasePlanList 1..* PublicPurchasePlan
   Funding 1..* ShopPurchaseList
   Shop 1..* ShopPurchaseList
   Student 1..* ShopPurchaseList
   ProductCategory 1..* ProductSubcategory
   ProductSubcategory 1..* Item
   ShopPurchaseList *..* Item przez ShopPurchaseListItem
   PurchaseRequest *..* Funding przez PurchaseRequestFundingAllocation
   PurchaseRequest *..* PublicPurchasePlan przez PurchaseRequestPlanPosition
   PurchaseRequest 1..* PurchaseRequestFinalizationSnapshot
   PurchaseRequest 1..* PurchaseRequestSettlementLine
   Settlement 1..* Invoice

Reguły spójności danych
-----------------------

* Jedno dofinansowanie może mieć najwyżej jeden plan publiczny.
* Pozycje planu muszą mieć dodatni koszt.
* Kod CPV powinien być tekstem, nie liczbą.
* Pozycja planu nie powinna być usuwana, jeśli jest użyta przez listę lub
  wniosek.
* Wniosek musi wskazywać budżet projektu i finansowanie.
* Alokacja planu musi należeć do finansowania użytego we wniosku.
* Finalizacja ustawia ``can_add = False`` i zapisuje snapshot.
* Rozliczenie zakończone wymaga faktur.
