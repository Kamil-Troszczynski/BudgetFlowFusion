Dokumentacja użytkownika
========================

Przeznaczenie
-------------

Aplikacja służy do prowadzenia zakupów koła naukowego od zgłoszenia
przedmiotu do rozliczenia faktury. Użytkownik pracuje w przeglądarce.
Dane są zapisywane na backendzie.

Role użytkowników
-----------------

Zwykły członek może:

* logować się i przeglądać swój profil,
* dodawać przedmioty,
* zgłaszać sklepy,
* przeglądać dostępne listy zakupów,
* dodawać przedmioty do otwartych list,
* usuwać własny wkład z listy.

Skarbnik może dodatkowo:

* zarządzać sklepami i kategoriami,
* tworzyć dofinansowania,
* tworzyć plany zamówień publicznych,
* tworzyć i zamykać listy zakupów,
* tworzyć wnioski,
* finalizować wnioski,
* przekazywać wnioski do rozliczeń,
* dodawać faktury,
* kończyć rozliczenia,
* kontrolować budżet koła i sekcji.

Logowanie
---------

1. Otwórz aplikację.
2. Wpisz login/e-mail i hasło.
3. Zatwierdź formularz.
4. Po poprawnym logowaniu aplikacja pokazuje panel główny.

Rejestracja
-----------

1. Otwórz formularz rejestracji.
2. Podaj imię, nazwisko, login/e-mail i hasło.
3. Wybierz koło i sekcję/projekt.
4. Ustaw informację SAP.
5. Wybierz rolę.
6. Zapisz konto.

Status SAP jest informacyjny. Aplikacja nie łączy się z SAP.

Panel główny
------------

Panel pokazuje dane użytkownika:

* imię i nazwisko,
* login/e-mail,
* koło,
* sekcję,
* rolę,
* status SAP.

Skarbnik widzi dodatkowo podsumowanie budżetu:

* budżet całkowity,
* wydane środki,
* środki zarezerwowane we wnioskach,
* środki dostępne po rezerwacjach,
* procent wykorzystania.

Katalog przedmiotów
-------------------

Dodanie przedmiotu:

1. Przejdź do widoku dodanych przedmiotów.
2. Wybierz dodanie nowego przedmiotu.
3. Podaj nazwę, link, cenę, walutę, sklep i podkategorię.
4. Zapisz formularz.

Przedmiot trafia do katalogu i może zostać użyty na liście zakupów.

Kategorie i podkategorie
------------------------

Skarbnik może tworzyć kategorie z kodem CPV. Użytkownik może zgłosić
podkategorię. Podkategoria bez kategorii trafia do oczekujących i może
zostać przypisana przez skarbnika.

Sklepy
------

Zgłoszenie sklepu:

1. Przejdź do widoku sklepów.
2. Dodaj sklep.
3. Podaj nazwę, link, opinię i próg darmowej dostawy.
4. Zapisz.

Skarbnik może:

* zaakceptować sklep,
* edytować sklep,
* odrzucić sklep oczekujący.

Listy zakupów
-------------

Lista zakupów jest koszykiem dla jednego sklepu.

Stany listy:

.. code-block:: text

   otwarta   - można dodawać i usuwać pozycje
   zamknięta - nie można zmieniać pozycji, można użyć we wniosku

Dodanie pozycji do listy:

1. Otwórz listę.
2. Wybierz przedmiot z katalogu.
3. Podaj ilość.
4. Zapisz.

Jeżeli kilku użytkowników dodaje ten sam przedmiot, aplikacja pokazuje
łączną ilość, ale pamięta wkład każdego użytkownika oddzielnie.

Zamknięcie listy:

1. Otwórz listę jako skarbnik.
2. Sprawdź pozycje i koszt.
3. Zamknij listę.

Zamknięta lista może zostać użyta do utworzenia wniosku.

Dofinansowania
--------------

Tworzenie dofinansowania:

1. Przejdź do widoku planów publicznych/budżetów.
2. Wybierz sekcję/projekt.
3. Podaj nazwę dofinansowania.
4. Podaj organizatora.
5. Podaj osobę podpisującą.
6. Podaj termin wydatkowania.
7. Podaj kwotę.
8. Opcjonalnie dodaj zadania budżetowe.
9. Zapisz.

Suma zadań budżetowych nie może przekroczyć kwoty dofinansowania.

Plany publiczne
---------------

Utworzenie planu:

1. Wybierz dofinansowanie.
2. Utwórz plan.
3. Podaj rok, numer planu, osobę odpowiedzialną i kurs euro.
4. Zapisz.

Dodanie pozycji planu:

1. Otwórz plan.
2. Dodaj pozycję.
3. Podaj nazwę, CPV, numer pozycji i kwotę.
4. Zapisz.

Znaczenie kwot:

.. code-block:: text

   kwota planowana  - limit pozycji planu
   wykorzystano     - suma alokacji z wniosków
   pozostało        - kwota planowana minus wykorzystanie

Wnioski
-------

Utworzenie wniosku:

1. Przejdź do widoku wniosków.
2. Utwórz wniosek albo wybierz zamkniętą listę.
3. Podaj nazwę i typ zakupu.
4. Wybierz finansowanie.
5. Wskaż pozycje planu CPV i kwoty.
6. Jeżeli system wymaga uzasadnienia, uzupełnij powód odstępstwa.
7. Zapisz.

Po zapisaniu wniosek rezerwuje środki. Budżet dostępny zmniejsza się o
kwotę alokacji.

Finalizacja wniosku
-------------------

1. Otwórz wniosek.
2. Przygotuj finalizację.
3. Sprawdź koszyki, kwoty i CPV.
4. Podaj nazwę dokumentu.
5. Podaj datę wartości umowy.
6. Podaj kurs euro.
7. Finalizuj.

Po finalizacji:

* dodawanie pozycji jest zablokowane,
* zapisywany jest snapshot danych,
* tworzone są linie rozliczeniowe,
* wniosek przechodzi do oczekiwania na księgowość.

Rozliczenia i faktury
---------------------

Przekazanie do rozliczeń:

1. Otwórz sfinalizowany wniosek.
2. Wybierz przekazanie do rozliczeń.
3. Sprawdź linie rozliczeniowe.

Dodanie faktury:

1. Otwórz rozliczenie.
2. Dodaj fakturę.
3. Podaj numer, datę, sprzedawcę, NIP, kwotę netto i VAT.
4. Zapisz.

Zakończenie rozliczenia:

1. Uzupełnij faktury.
2. Przypisz kwoty rzeczywiste do linii.
3. Zakończ rozliczenie.

Historia
--------

Historia rozliczeń pokazuje wnioski zakończone. Widok służy do kontroli
faktur, kwot rzeczywistych i różnic względem planu.
