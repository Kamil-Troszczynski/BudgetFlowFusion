Dokumentacja analityczno-projektowa
===================================

Problem
-------

Koło naukowe prowadzi zakupy z wielu źródeł finansowania. Każdy zakup
musi być przypisany do sekcji/projektu, dofinansowania, pozycji planu
zamówień publicznych oraz późniejszego rozliczenia. Bez systemu dane są
rozproszone między listami zakupów, arkuszami budżetowymi, wnioskami i
fakturami.

Cel projektowy
--------------

Celem systemu jest utrzymanie spójnego przebiegu:

.. code-block:: text

   dofinansowanie
      -> plan zamówień publicznych
      -> lista zakupów
      -> wniosek
      -> finalizacja
      -> rozliczenie
      -> faktura

Aplikacja ma pilnować:

* dostępności środków,
* zgodności wniosku z pozycją CPV,
* wykorzystania planu publicznego,
* powiązania koszyków z wnioskiem,
* historii finalizacji,
* statusów faktur i rozliczeń.

Aktorzy
-------

.. code-block:: text

   +-------------------+----------------------------------------------+
   | Aktor             | Odpowiedzialność                             |
   +===================+==============================================+
   | Członek koła      | przedmioty, sklepy, wkład do list zakupów    |
   | Skarbnik          | budżety, finansowania, plany, wnioski        |
   | Obsługa rozliczeń | faktury, statusy, kwoty rzeczywiste          |
   +-------------------+----------------------------------------------+

Obsługa rozliczeń nie jest osobnym typem konta w modelu. Jej czynności
są realizowane przez moduł ``Settlement`` i ``Invoice``.

Model ról
---------

.. code-block:: text

   Student
      |
      | project_finance_manager_id IS NULL
      v
   zwykły członek

   Student
      |
      | project_finance_manager_id -> ProjectFinanceManager
      v
   skarbnik

Frontend ukrywa funkcje zależnie od roli. Backend dodatkowo sprawdza
część operacji skarbnika, np. zarządzanie kategoriami, sklepami i
finansami.

Wymagania funkcjonalne
----------------------

RF-01. Użytkownik może się zarejestrować i zalogować.

RF-02. System rozróżnia zwykłego członka i skarbnika.

RF-03. Członek może dodać przedmiot do katalogu.

RF-04. Członek może zgłosić sklep. Skarbnik może sklep zaakceptować,
edytować albo odrzucić.

RF-05. Skarbnik może tworzyć dofinansowania wraz z zadaniami
budżetowymi.

RF-06. Skarbnik może utworzyć plan zamówień publicznych dla
dofinansowania.

RF-07. Skarbnik może tworzyć listy zakupów i przypisywać je do sklepu,
dofinansowania oraz grupy zakupowej.

RF-08. Użytkownicy mogą dodawać wkład do otwartych list zakupów.

RF-09. Skarbnik może zamknąć listę i użyć jej przy wniosku.

RF-10. Skarbnik może utworzyć wniosek o zamówienie z alokacją środków.

RF-11. Wniosek może korzystać z jednej lub wielu pozycji planu.

RF-12. Przekroczenie pozycji planu wymaga uzasadnienia.

RF-13. Finalizacja wniosku zapisuje dane historyczne w snapshotach.

RF-14. Rozliczenie wymaga obsługi faktur i kwot rzeczywistych.

Wymagania niefunkcjonalne
-------------------------

* Backend udostępnia API REST w formacie JSON.
* Frontend działa jako SPA w Vue 3.
* Dane trwałe są przechowywane w PostgreSQL.
* Modele bazodanowe są definiowane w SQLModel.
* Testy backendu używają SQLite in-memory.
* Dokumentacja jest generowana z plików ``doc/*.rst`` przez
  ``doc_gen.py``.

Decyzje projektowe
------------------

Budżet wynika z dofinansowań
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``ProjectBudget.total_budget`` i ``AssociationBudget.total_budget`` nie
powinny być traktowane jako niezależne źródło prawdy. W raportowaniu
kwoty są liczone z tabeli ``Funding`` i rezerwacji wniosków.

Plan jest przy dofinansowaniu
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``PublicPurchasePlanList`` ma relację 1:1 z ``Funding``. Dzięki temu
pozycje CPV są kontrolowane w kontekście konkretnego źródła pieniędzy.

Wniosek rezerwuje środki
~~~~~~~~~~~~~~~~~~~~~~~~

Tabela ``PurchaseRequestFundingAllocation`` przechowuje kwoty
zarezerwowane na wniosek. Jeżeli wniosek nie ma rekordów alokacji,
backend używa pola legacy
``PurchaseRequest.budget_allocated_for_the_order`` jako fallback.

Finalizacja zapisuje snapshot
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``PurchaseRequestFinalizationSnapshot`` przechowuje skopiowane dane
planu i finansowania: CPV, numer planu, nazwę finansowania, kwoty netto,
brutto i EUR. Snapshot jest potrzebny, ponieważ plan albo finansowanie
mogą zostać później zmienione.

Koszyk przechowuje wkład użytkowników
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``ShopPurchaseListItem`` przechowuje łączną ilość przedmiotu na liście.
``ShopPurchaseListItemContribution`` przechowuje ile dodał konkretny
student. To pozwala zwykłemu członkowi usuwać tylko własny wkład.

Zakres ryzyka
-------------

Największe ryzyka projektowe:

* podwójne liczenie kwot z dofinansowań i wniosków,
* niespójność planu CPV po edycji lub usunięciu pozycji,
* brak pełnej autoryzacji backendowej dla każdej operacji finansowej,
* różnice między PostgreSQL runtime i SQLite w testach,
* logika biznesowa umieszczona bezpośrednio w endpointach.
