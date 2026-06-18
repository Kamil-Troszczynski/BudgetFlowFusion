Procesy biznesowe
=================

Proces bazowy
-------------

.. code-block:: text

   1. Skarbnik zakłada dofinansowanie.
   2. Skarbnik tworzy plan publiczny dla dofinansowania.
   3. Użytkownicy dodają przedmioty i pracują na listach zakupów.
   4. Skarbnik zamyka listy zakupów.
   5. Skarbnik tworzy wniosek.
   6. System rezerwuje budżet i pozycje planu.
   7. Skarbnik finalizuje wniosek.
   8. System zapisuje snapshot i linie rozliczeniowe.
   9. Wniosek przechodzi do rozliczeń.
   10. Faktury zamykają rozliczenie.

Dodanie przedmiotu
------------------

.. code-block:: text

   Student
      -> POST /api/items
      -> Item(status = approved)
      -> GET /api/items

Reguły:

* wymagane są nazwa, cena, waluta, podkategoria i student,
* przedmiot jest przypisany do sklepu,
* katalog pokazuje rekordy zaakceptowane,
* skarbnik może dodatkowo zatwierdzać albo odrzucać pozycje pending.

Zgłoszenie sklepu
-----------------

.. code-block:: text

   Student
      -> POST /api/shops
      -> Shop(status = pending)
      -> Skarbnik
      -> PATCH approve albo DELETE reject

Reguły:

* nazwa sklepu jest wymagana,
* próg darmowej dostawy nie może być ujemny,
* nazwa i link nie mogą duplikować aktywnego sklepu,
* zaakceptowanego sklepu nie można odrzucić endpointem reject.

Dofinansowanie
--------------

.. code-block:: text

   ProjectBudget
      -> Funding
      -> FundingTask*

Reguły:

* kwota dofinansowania musi być dodatnia,
* wymagane są nazwa, organizator i osoba podpisująca,
* suma zadań budżetowych nie może przekroczyć kwoty dofinansowania,
* dofinansowanie dziedziczy ``project_id`` i ``association_budget_id`` z
  budżetu projektu.

Plan zamówień publicznych
-------------------------

.. code-block:: text

   Funding
      -> PublicPurchasePlanList
      -> PublicPurchasePlan*

Reguły:

* jedno dofinansowanie ma najwyżej jeden nagłówek planu,
* pozycja planu ma kod CPV i dodatnią kwotę,
* kod CPV powinien być unikalny w ramach planu,
* usunięcie pozycji jest blokowane, jeżeli pozycja jest użyta przez
  wniosek lub koszyk.

Lista zakupów
-------------

.. code-block:: text

   ShopPurchaseList
      -> ShopPurchaseListItem
      -> ShopPurchaseListItemContribution

Reguły:

* lista jest przypisana do sklepu, finansowania i studenta,
* pozycja listy przechowuje ilość łączną,
* contribution przechowuje ilość dodaną przez konkretnego studenta,
* zwykły członek może usunąć tylko swój wkład,
* zamknięcie listy tworzy albo wiąże ``Settlement``.

Wniosek
-------

.. code-block:: text

   POST /api/create_purchase_requests
      |
      +-- walidacja budżetu projektu
      +-- walidacja dofinansowania
      +-- walidacja pozycji planu
      +-- zapis PurchaseRequest
      +-- zapis PurchaseRequestFundingAllocation
      +-- zapis PurchaseRequestPlanPosition

Reguły:

* ``funding_id`` musi należeć do wskazanego ``project_budget_id``,
* kwota wniosku nie może przekroczyć dostępnych środków projektu,
* kwota wniosku nie może przekroczyć dostępnych środków finansowania,
* pozycja planu musi należeć do finansowania użytego we wniosku,
* przekroczenie pozostałej kwoty planu ustawia
  ``plan_compliance_status = requires_approval``,
* status ``requires_approval`` wymaga uzasadnienia.

Wniosek z zamkniętej listy
--------------------------

.. code-block:: text

   PATCH /api/lists/{id}/close
      -> Settlement bez purchase_request_id
      -> ShopPurchaseList.settlement_id

   POST /api/create_purchase_requests
      shop_purchase_list_id = id
      -> PurchaseRequest
      -> Settlement.purchase_request_id = request.id

Reguły:

* lista musi być zamknięta,
* lista musi należeć do tego samego skarbnika,
* settlement listy nie może być już powiązany z innym wnioskiem,
* koszt wniosku jest liczony z pozycji listy.

Finalizacja
-----------

.. code-block:: text

   prepare_finalization
      -> can_add = False
      -> finalization_status = prepared

   finalize
      -> PurchaseRequestFinalizationSnapshot*
      -> PurchaseRequestFundingAllocation*
      -> PurchaseRequestSettlementLine*
      -> finalization_status = accounting_pending

Reguły:

* wniosek musi mieć koszyki,
* wniosek musi mieć pozycje CPV,
* kurs euro musi być dodatni,
* nazwa dokumentu jest wymagana,
* finalizacja zapisuje snapshot i wartości końcowe netto/brutto,
* po finalizacji nie można dalej dodawać pozycji do wniosku.

Rozliczenie
-----------

.. code-block:: text

   send_to_settlement
      -> finalization_status = settlement
      -> Settlement
      -> Invoice*
      -> complete
      -> finalization_status = settled

Reguły:

* do rozliczeń można przekazać tylko zatwierdzony wniosek,
* dodatkowe linie rozliczeniowe można dodać dopiero po przekazaniu do
  rozliczeń,
* zakończenie rozliczenia wymaga faktur,
* linie rozliczeniowe pokazują różnicę między kwotą planowaną i
  rzeczywistą.
