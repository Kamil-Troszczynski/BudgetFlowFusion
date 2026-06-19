Wprowadzenie
============

Cel systemu
-----------

BudgetFlowFusion jest aplikacją do obsługi zakupów, budżetów,
dofinansowań, planów zamówień publicznych, wniosków i rozliczeń w kole
naukowym. System zastępuje rozproszone arkusze i ustalenia ręczne jednym
modelem danych oraz jednym procesem operacyjnym.

Zakres funkcjonalny
-------------------

System obsługuje:

* rejestrację i logowanie użytkowników,
* rozróżnienie zwykłego członka i skarbnika,
* katalog przedmiotów oraz zgłaszanie sklepów,
* listy zakupów prowadzone dla konkretnego sklepu i finansowania,
* budżety koła, sekcji i dofinansowań,
* roczne plany zamówień publicznych powiązane z dofinansowaniem,
* wnioski o zamówienie z alokacją środków i pozycji planu,
* finalizację wniosku wraz ze snapshotem danych,
* rozliczenia, faktury i linie rozliczeniowe.

Role
----

``Student``
  Użytkownik aplikacji. Może dodawać przedmioty, zgłaszać sklepy i
  pracować na otwartych listach zakupów.

``ProjectFinanceManager``
  Skarbnik. Jest powiązany ze studentem przez
  ``Student.project_finance_manager_id``. Zarządza finansami, planami,
  listami, wnioskami i rozliczeniami.

Granice systemu
---------------

System nie integruje się z SAP ani z zewnętrznym systemem księgowym.
Pole ``Student.is_in_sap`` ma charakter informacyjny. Dokumenty i
faktury są odwzorowane jako dane w bazie, bez obsługi uploadu pełnych
plików dokumentów poza nazwą pliku rozeznania rynku.

Główna reguła finansowa
-----------------------

Źródłem pieniędzy w systemie jest ``Funding``. Budżety sekcji i koła są
wyliczane z dofinansowań oraz zarezerwowanych/wykorzystanych kwot.

.. code-block:: text

   Funding.funding_price
      - Funding.spent_money
      - SUM(PurchaseRequestFundingAllocation.allocated_amount)
      = dostępne środki po rezerwacjach

Główna reguła projektowa
------------------------

Plan zamówień publicznych jest przypisany do jednego dofinansowania.
Wniosek rezerwuje środki i zużywa wskazane pozycje planu. Finalizacja
zapisuje snapshot, żeby późniejsze zmiany planu lub dofinansowania nie
zmieniły historii dokumentu.
