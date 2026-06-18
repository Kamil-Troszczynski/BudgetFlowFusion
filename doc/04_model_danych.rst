Model danych
============

Charakter modelu
----------------

Model danych jest relacyjnym modelem domeny zakupowo-budżetowej koła
naukowego. Encje są zdefiniowane w ``backend/src/relations.py`` jako
klasy ``SQLModel``. W runtime tabele tworzone są przez
``SQLModel.metadata.create_all(engine)``, a brakujące kolumny i tabele
historyczne uzupełnia funkcja ``migrate_project_budgets()``.

Konwencje diagramów:

.. code-block:: text

   PK   klucz główny
   FK   klucz obcy
   1    dokładnie jeden
   0..1 zero albo jeden
   *    wiele

Diagram logiczny całego modelu
------------------------------

.. code-block:: text

   +------------------+       +--------------------+
   |   Association    | 1   * |      Student       |
   | association_id PK|-------| student_id PK      |
   +------------------+       | association_id FK  |
          |                   | pfm_id FK          |
          |                   +--------------------+
          |                              |
          |                              | 0..1
          |                              v
          |                   +--------------------------+
          |                   | ProjectFinanceManager    |
          |                   | project_finance_manager_id PK
          |                   +--------------------------+
          |
          | 1   *
          v
   +------------------+ 1   1 +--------------------+ 1   * +-----------+
   |     Project      |-------|   ProjectBudget    |-------|  Funding  |
   | project_id PK    |       | project_budget_id PK|      | funding_id PK
   | association_id FK|       | association_budget FK|     | project_budget FK
   +------------------+       +--------------------+       +-----------+
                                         |                         |
                                         |                         | 1
                                         |                         | 0..1
                                         v                         v
                              +--------------------+    +-------------------------+
                              | AssociationBudget |    | PublicPurchasePlanList  |
                              | association_budget_id PK| public_purchase_plan_list_id PK
                              +--------------------+    | funding_id FK unique    |
                                                        +-------------------------+
                                                                  |
                                                                  | 1   *
                                                                  v
                                                        +-------------------------+
                                                        |   PublicPurchasePlan    |
                                                        | public_purchase_plan_id PK
                                                        | cpv_code                |
                                                        | funding_id FK           |
                                                        +-------------------------+

   +-------------------------+ 1   * +------------------+ *   * +-------+
   | GroupedShopsList...     |-------| ShopPurchaseList |-------| Item  |
   | gslbccf_id PK           |       | shop_purchase_list_id PK  | item_id PK
   +-------------------------+       | funding_id FK     |       +-------+
                |                    | shop_id FK        |
                |                    | student_id FK     |
                |                    | settlement_id FK  |
                |                    +------------------+
                |                              |
                |                              | 1   *
                |                              v
                |                    +------------------------------+
                |                    | ShopPurchaseListContribution |
                |                    | list_id PK/FK                |
                |                    | item_id PK/FK                |
                |                    | student_id PK/FK             |
                |                    +------------------------------+
                |
                | 1   *
                v
   +-------------------+ 1   * +--------------------------------+
   | PurchaseRequest   |-------| PurchaseRequestPlanPosition    |
   | purchase_request_id PK    | request_id PK/FK               |
   | funding_id FK             | list_id PK/FK                  |
   | project_budget_id FK      | public_plan_id PK/FK           |
   | gslbccf_id FK             +--------------------------------+
   +-------------------+
          |
          | 1   *
          v
   +-----------------------------------+
   | PurchaseRequestFundingAllocation |
   +-----------------------------------+
          |
          | 1   *
          v
   +-------------------------------------+
   | PurchaseRequestFinalizationSnapshot |
   +-------------------------------------+
          |
          | 1   *
          v
   +-----------------------------------+
   | PurchaseRequestSettlementLine     |
   +-----------------------------------+
          |
          | 0..1
          v
   +------------+ 1   * +---------+
   | Settlement |-------| Invoice |
   +------------+       +---------+

Podmodel użytkowników i organizacji
-----------------------------------

.. code-block:: text

   Association
     association_id PK
     association_name

   Student
     student_id PK
     name
     surname
     login
     password_hash
     position
     is_in_sap
     association_id FK
     project_finance_manager_id FK nullable

   ProjectFinanceManager
     project_finance_manager_id PK
     login
     password_hash
     access

   Project
     project_id PK
     project_name
     description
     allocated_budget
     rest_of_budget
     association_id FK

Opis:

* ``Association`` jest granicą organizacyjną. Po tej encji filtrowane są
  projekty, użytkownicy, budżety, listy i wnioski.
* ``Student`` reprezentuje konto użytkownika. Rola skarbnika wynika z
  ustawionego ``project_finance_manager_id``.
* ``ProjectFinanceManager`` jest rekordem uprawniającym do funkcji
  skarbnika.
* ``Project`` reprezentuje sekcję lub projekt koła. Z projektem jest
  połączony dokładnie jeden ``ProjectBudget``.

Kardynalności:

.. code-block:: text

   Association 1 -- * Student
   Association 1 -- * Project
   Project 1 -- 0..1 ProjectBudget
   Student 0..1 -- 1 ProjectFinanceManager

Podmodel budżetów i dofinansowań
--------------------------------

.. code-block:: text

   AssociationBudget
     association_budget_id PK
     association_budget_name
     total_budget
     spent_money

   ProjectBudget
     project_budget_id PK
     project_budget_name
     total_budget
     spent_money
     association_budget_id FK
     project_id FK unique

   Funding
     funding_id PK
     funding_name
     organizer
     signing_person
     spending_deadline
     funding_price
     spent_money
     project_id FK
     project_budget_id FK
     association_budget_id FK

   FundingTask
     funding_task_id PK
     funding_id FK
     task_name
     task_budget

Opis:

* ``AssociationBudget`` jest budżetem zbiorczym koła.
* ``ProjectBudget`` jest budżetem sekcji/projektu.
* ``Funding`` jest faktycznym źródłem pieniędzy i najważniejszą encją
  finansową.
* ``FundingTask`` rozbija dofinansowanie na zadania opisowe.

Decyzja projektowa:

.. code-block:: text

   Budżet sekcji = suma Funding.funding_price dla tej sekcji.
   Budżet koła   = suma budżetów sekcji.

Dlatego ``ProjectBudget.total_budget`` i
``AssociationBudget.total_budget`` nie powinny być traktowane jako
niezależne kwoty biznesowe. Są zgodne z dofinansowaniami albo pełnią
rolę danych bazowych po migracji.

Wzory:

.. code-block:: text

   project_total_budget =
     SUM(Funding.funding_price WHERE project_budget_id = X)

   project_spent_money =
     SUM(Funding.spent_money WHERE project_budget_id = X)

   project_reserved =
     SUM(PurchaseRequest.budget_allocated_for_the_order
         WHERE project_budget_id = X)

   project_available =
     project_total_budget - project_spent_money - project_reserved

Podmodel planów zamówień publicznych
------------------------------------

.. code-block:: text

   Funding
      |
      | 1 : 0..1
      v
   PublicPurchasePlanList
      public_purchase_plan_list_id PK
      public_plan_list_name
      plan_year
      plan_number
      fund_responsible_person
      euro_exchange_rate
      funding_id FK unique
      |
      | 1 : *
      v
   PublicPurchasePlan
      public_purchase_plan_id PK
      public_purchase_plan_name
      cpv_code
      plan_position_number
      cost
      funding_id FK
      gslbccf_id FK
      public_purchase_plan_list_id FK

Opis:

* ``PublicPurchasePlanList`` jest nagłówkiem planu dla jednego
  dofinansowania i roku.
* ``PublicPurchasePlan`` jest pozycją planu. W praktyce reprezentuje
  kod CPV i planowaną kwotę.
* ``cpv_code`` jest tekstem, nie liczbą.
* ``gslbccf_id`` łączy pozycję planu z grupą koszyków zakupowych.

Reguły:

* jedno dofinansowanie ma najwyżej jeden ``PublicPurchasePlanList``,
* CPV musi być unikalny w ramach jednego planu,
* koszt pozycji planu musi być dodatni,
* pozycji użytej we wniosku nie wolno usuwać,
* pozycja z podpiętym koszykiem nie powinna być usuwana.

Wykorzystanie pozycji planu:

.. code-block:: text

   used_amount =
     SUM(PurchaseRequestPlanPosition.allocated_amount)
     + legacy SUM(PurchaseRequest.budget_allocated_for_the_order)

   remaining_amount =
     PublicPurchasePlan.cost - used_amount

Podmodel katalogu i list zakupów
--------------------------------

.. code-block:: text

   ProductCategory
     product_category_id PK
     product_category_name
     description
     cpv
     shop_purchase_list_id FK nullable
     public_purchase_plan_id FK nullable

   ProductSubcategory
     product_subcategory_id PK
     product_subcategory_name
     description
     product_category_id FK nullable

   Shop
     shop_id PK
     shop_name
     link
     opinion
     status
     created_by_student_id
     address
     delivery_time
     is_recommended
     free_delivery_threshold

   Item
     item_id PK
     name
     price
     currency
     link
     created_at
     tax_rate
     status
     product_subcategory_id FK
     student_id FK
     shop_id FK

   ShopPurchaseList
     shop_purchase_list_id PK
     priority
     name
     cost
     created_at
     market_research_comment
     market_research_file_name
     gslbccf_id FK nullable
     settlement_id FK nullable
     funding_id FK
     shop_id FK
     student_id FK

   ShopPurchaseListItem
     shop_purchase_list_id PK/FK
     item_id PK/FK
     amount

   ShopPurchaseListItemContribution
     shop_purchase_list_id PK/FK
     item_id PK/FK
     student_id PK/FK
     amount
     created_at

Opis:

* ``ProductCategory`` może być powiązana z pozycją planu, dzięki czemu
  CPV przechodzi z planu do katalogu.
* ``ProductSubcategory`` grupuje przedmioty wewnątrz kategorii.
* ``Item`` jest wspólnym katalogowym przedmiotem. Aktualnie nowe
  przedmioty trafiają do katalogu jako ``approved``.
* ``Shop`` przechowuje sklep i jego status.
* ``ShopPurchaseList`` jest koszykiem jednego sklepu.
* ``ShopPurchaseListItem`` zapisuje łączną ilość przedmiotu na liście.
* ``ShopPurchaseListItemContribution`` zapisuje wkład konkretnego
  studenta.

Diagram wkładów studentów:

.. code-block:: text

   Student Jan dodaje 2 szt.
   Student Ola dodaje 3 szt.
          |
          v
   ShopPurchaseListItem.amount = 5
          |
          +-- Contribution Jan = 2
          +-- Contribution Ola = 3

Dzięki temu usunięcie pozycji przez zwykłego studenta usuwa tylko jego
wkład, a nie cały przedmiot z koszyka.

Stan listy zakupów:

.. code-block:: text

   settlement_id = NULL
     lista otwarta, można dodawać i usuwać pozycje

   settlement_id != NULL
     lista zamknięta, nie można zmieniać pozycji

Podmodel wniosków
-----------------

.. code-block:: text

   PurchaseRequest
     purchase_request_id PK
     purchase_request_name
     budget_allocated_for_the_order
     if_service
     used_cpv_id
     created_at
     can_add
     document_request_name
     contract_value_date
     euro_exchange_rate
     main_cpv_code
     final_net_total
     final_gross_total
     finalization_status
     finalized_at
     project_budget_id FK
     funding_id FK
     public_purchase_plan_id FK nullable
     plan_exception_justification
     plan_compliance_status
     gslbccf_id FK nullable
     project_finance_manager_id FK

   PurchaseRequestFundingAllocation
     purchase_request_id PK/FK
     funding_id PK/FK
     allocated_amount

   PurchaseRequestPlanPosition
     purchase_request_id PK/FK
     shop_purchase_list_id PK/FK
     public_purchase_plan_id PK/FK
     allocated_amount

Opis:

* ``PurchaseRequest`` jest głównym dokumentem zakupowym.
* ``funding_id`` jest głównym finansowaniem wniosku.
* wiele finansowań obsługuje
  ``PurchaseRequestFundingAllocation``.
* ``public_purchase_plan_id`` jest główną lub historyczną pozycją planu.
* wiele pozycji planu obsługuje ``PurchaseRequestPlanPosition``.
* ``gslbccf_id`` wiąże wniosek z koszykami.

Diagram alokacji:

.. code-block:: text

   PurchaseRequest "Zakup elektroniki"
      |
      +-- FundingAllocation: Grant A, 1000 PLN
      +-- FundingAllocation: Grant B,  500 PLN
      |
      +-- PlanPosition: CPV 31700000, koszyk TME, 900 PLN
      +-- PlanPosition: CPV 30200000, koszyk X-kom, 600 PLN

Status zgodności z planem:

.. code-block:: text

   draft
     wniosek bez pełnych danych planu albo kwota 0

   compliant
     alokacje mieszczą się w pozycjach planu

   requires_approval
     alokacja przekracza plan i wymaga uzasadnienia

Status finalizacji:

.. code-block:: text

   draft
      |
      v
   prepared
      |
      v
   accounting_pending
      |
      v
   settlement
      |
      v
   settled

Podmodel finalizacji i rozliczeń
--------------------------------

.. code-block:: text

   PurchaseRequestFinalizationSnapshot
     snapshot_id PK
     purchase_request_id FK
     shop_purchase_list_id FK
     public_purchase_plan_id FK
     funding_id FK
     shop_name
     funding_name
     plan_name
     plan_number
     fund_responsible_person
     plan_position_number
     cpv_code
     planned_net_amount
     allocated_net_amount
     allocated_eur_amount
     allocated_gross_amount
     is_main_cpv
     created_at

   PurchaseRequestSettlementLine
     settlement_line_id PK
     purchase_request_id FK
     shop_purchase_list_id FK
     invoice_id FK nullable
     shop_name
     purchase_description
     planned_gross_amount
     actual_gross_amount
     is_extra
     created_at
     updated_at

   Settlement
     settlement_id PK
     created_at
     paid_by_project_finance_manager_id FK nullable
     purchase_request_id FK nullable

   Invoice
     invoice_id PK
     number
     issue_date
     seller_name
     seller_nip
     net_total
     vat_total
     status
     created_at
     settlement_id FK
     project_finance_manager_id FK nullable

Opis:

* ``PurchaseRequestFinalizationSnapshot`` chroni dokument historyczny
  przed zmianami w planie i finansowaniu.
* ``PurchaseRequestSettlementLine`` jest linią rozliczenia wniosku.
* ``Settlement`` grupuje faktury i listy zakupów na etapie rozliczeń.
* ``Invoice`` reprezentuje dokument księgowy.

Diagram rozliczenia:

.. code-block:: text

   PurchaseRequest
      |
      | send_to_settlement
      v
   Settlement
      |
      +-- Invoice FV/01/2026
      +-- Invoice FV/02/2026
      |
      +-- SettlementLine sklep A -> invoice FV/01/2026
      +-- SettlementLine sklep B -> invoice FV/02/2026

Reguła zakończenia:

.. code-block:: text

   Każda PurchaseRequestSettlementLine musi mieć invoice_id.
   Dopiero wtedy Settlement może ustawić wniosek jako settled.

Enumy i statusy
---------------

.. code-block:: text

   InvoiceStatus
     pending
     accepted
     rejected
     paid
     returned
     arrived

   Currency
     PLN
     EUR
     USD

   ItemStatus
     draft
     pending
     approved
     rejected

Najważniejsze zależności obliczeniowe
-------------------------------------

Budżet dofinansowania:

.. code-block:: text

   available_money =
     Funding.funding_price - Funding.spent_money

   purchase_requests_total_allocated =
     SUM(PurchaseRequestFundingAllocation.allocated_amount)

   available_after_purchase_requests =
     available_money - purchase_requests_total_allocated

Budżet sekcji:

.. code-block:: text

   total_budget =
     SUM(Funding.funding_price)

   spent_money =
     SUM(Funding.spent_money)

   reserved =
     SUM(PurchaseRequest.budget_allocated_for_the_order)

   available_after_purchase_requests =
     total_budget - spent_money - reserved

Budżet koła:

.. code-block:: text

   total_budget =
     SUM(ProjectBudget.total_budget liczonych z Funding)

   spent_money =
     SUM(ProjectBudget.spent_money liczonych z Funding)

   reserved =
     SUM(PurchaseRequest.budget_allocated_for_the_order dla projektów koła)

   available_after_purchase_requests =
     total_budget - spent_money - reserved

Kwoty planu:

.. code-block:: text

   used_amount =
     SUM(PurchaseRequestPlanPosition.allocated_amount)

   remaining_amount =
     PublicPurchasePlan.cost - used_amount

Uwagi projektowe
----------------

* Model przechowuje część pól historycznych dla zgodności z wcześniejszą
  wersją projektu, np. ``PurchaseRequest.public_purchase_plan_id`` obok
  ``PurchaseRequestPlanPosition``.
* ``GroupedShopsListByCpvCategoryAndFunding`` jest techniczną grupą
  spinającą plan, wniosek i koszyki.
* ``settlement_id`` na liście zakupów jest praktycznym znacznikiem
  zamknięcia listy.
* ``used_cpv_id`` jest tekstem, bo CPV może zawierać zera wiodące albo
  myślnik.
* Finalizacja pracuje na kwotach netto dla planu i brutto dla koszyków,
  dlatego snapshot zapisuje oba warianty kwot.
