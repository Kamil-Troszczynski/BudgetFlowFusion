Wprowadzenie
============

Cel projektu
------------

BudgetFlowFusion powstał po to, żeby zebrać w jednym miejscu proces,
który w kole naukowym łatwo rozchodzi się po wiadomościach, arkuszach i
ustaleniach ze skarbnikiem. Członkowie koła zgłaszają rzeczy do kupienia,
skarbnik pilnuje finansowania, a na końcu trzeba jeszcze mieć porządek w
wnioskach, planie zamówień publicznych i fakturach.

Aplikacja prowadzi ten proces od katalogu przedmiotów i list zakupów,
przez wybór dofinansowania oraz pozycji CPV, aż do finalizacji wniosku i
rozliczenia. Najważniejsze jest zachowanie śladu: skąd pochodziły
pieniądze, do którego planu podpięto zakup, kto dodał pozycje do listy i
na jakim etapie jest wniosek.

Kontekst działania
------------------

Koło naukowe może mieć kilka sekcji albo projektów. Każda sekcja ma
budżet wynikający z dofinansowań. Dofinansowanie jest konkretną pulą
pieniędzy, a nie tylko opisem w tabeli. Dla takiej puli można przygotować
plan zamówień publicznych, czyli listę kodów CPV i kwot, które mają być
wydane w danym roku.

Później, kiedy skarbnik chce realnie coś kupić, tworzy wniosek o
zamówienie. Wniosek powinien wskazywać, z którego dofinansowania
korzysta i którą pozycję planu CPV wykorzystuje. Jeżeli zakup nie mieści
się w planie albo przekracza zaplanowaną kwotę, system nie ukrywa tego
problemu, tylko wymaga uzasadnienia.

Użytkownicy systemu
-------------------

**Zwykły członek koła**
  Dodaje przedmioty, przegląda katalog i może uzupełniać otwarte koszyki
  zakupowe przypisane do wniosków dostępnych dla jego koła.

**Skarbnik**
  Zarządza koszykami, budżetami, dofinansowaniami, planami publicznymi,
  wnioskami, finalizacją oraz rozliczeniami.

**Osoba rozliczająca / księgowa w procesie**
  W obecnym systemie jej czynności są reprezentowane głównie przez moduł
  rozliczeń, faktury, statusy i kontrolę wykorzystania pozycji planu.

Główne założenia
----------------

* Jedno dofinansowanie należy do jednej sekcji/projektu.
* Budżet sekcji jest sumą dofinansowań tej sekcji.
* Budżet koła jest sumą budżetów sekcji.
* Plan zamówień publicznych jest przypisany do dofinansowania.
* Pozycja planu publicznego opisuje kod CPV i kwotę planowaną.
* Wniosek może korzystać z jednej albo wielu alokacji finansowania.
* Wniosek może wykorzystywać jedną albo wiele pozycji planu.
* Finalizacja wniosku zamyka część zakupową i tworzy dane do rozliczeń.

Zakres techniczny aplikacji
---------------------------

BudgetFlowFusion jest aplikacją typu SPA + REST API. Frontend nie
posiada własnej bazy ani warstwy offline. Wszystkie dane operacyjne są
pobierane z backendu przez endpointy ``/api/...``.

.. code-block:: text

   Vue component
      |
      | fetch(JSON)
      v
   FastAPI endpoint
      |
      | SQLModel Session
      v
   PostgreSQL table

Backend nie ma oddzielnej warstwy serwisowej. Reguły domenowe są
zaimplementowane głównie w plikach z trasami:

* ``public_purchase_plans_routes.py`` - budżety, dofinansowania i plan
  zamówień publicznych,
* ``purchase_request_routes.py`` - wnioski, alokacje, finalizacja i
  linie rozliczeniowe,
* ``lists_routes.py`` - koszyki sklepowe, wkład studentów i zamykanie
  list,
* ``settlements_routes.py`` - rozliczenia, faktury i historia,
* ``items_routes.py`` - wspólny katalog przedmiotów,
* ``fundings_routes.py`` - dofinansowania i zadania budżetowe.

Źródła prawdy danych finansowych
--------------------------------

Aktualne kwoty nie powinny być interpretowane jako pojedyncze pole
zapisane w jednej tabeli. System wylicza je dynamicznie z kilku tabel.

.. code-block:: text

   Budżet dofinansowania:
     Funding.funding_price

   Wydane z dofinansowania:
     Funding.spent_money

   Zarezerwowane we wnioskach:
     SUM(PurchaseRequestFundingAllocation.allocated_amount)
     albo legacy fallback:
     SUM(PurchaseRequest.budget_allocated_for_the_order)

   Dostępne po wnioskach:
     funding_price - spent_money - reserved

   Budżet sekcji:
     SUM(Funding.funding_price WHERE project_budget_id = X)

   Budżet koła:
     SUM(budżetów sekcji dla projektów danego Association)

Najważniejsza konsekwencja projektowa: ``ProjectBudget.total_budget`` i
``AssociationBudget.total_budget`` są synchronizowane i raportowane na
podstawie dofinansowań. Nie należy traktować ich jako niezależnych,
ręcznie ustawianych kwot.

Granice odpowiedzialności ról
-----------------------------

Rola użytkownika wynika z relacji ``Student.project_finance_manager_id``.
Jeżeli to pole jest ustawione, frontend traktuje użytkownika jako
skarbnika. Jeżeli jest puste, użytkownik jest zwykłym członkiem koła.

W obecnej implementacji autoryzacja jest uproszczona: frontend zapisuje
zalogowanego użytkownika w ``localStorage``, a backend przyjmuje
``student_id``, ``association_id`` albo ``project_finance_manager_id`` w
parametrach zapytania lub payloadzie. Dla operacji finansowych część
endpointów wykonuje dodatkowe sprawdzenia, np. czy student jest
skarbnikiem lub czy dofinansowanie należy do koła użytkownika.
