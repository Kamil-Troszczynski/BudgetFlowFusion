Dokumentacja użytkownika
========================

Przeznaczenie aplikacji
-----------------------

BudgetFlowFusion służy do prowadzenia zakupów w kole naukowym. Aplikacja
pomaga zebrać propozycje przedmiotów, utworzyć listy zakupów,
kontrolować budżet, przypisać zakup do dofinansowania i planu zamówień
publicznych, a następnie przejść przez wniosek, finalizację, rozliczenie
i faktury.

Najważniejsza zasada pracy:

.. code-block:: text

   Najpierw środki i plan.
   Potem listy zakupów.
   Potem wniosek.
   Na końcu finalizacja, rozliczenie i faktury.

Role w aplikacji
----------------

Zwykły członek koła
~~~~~~~~~~~~~~~~~~~

Zwykły członek może:

* zalogować się do aplikacji,
* przeglądać wspólny katalog przedmiotów,
* dodawać przedmioty do katalogu,
* przeglądać dostępne listy zakupów,
* dodawać przedmioty do otwartych list,
* usuwać z list tylko te ilości, które sam dodał,
* przeglądać podstawowe informacje o swoim profilu.

Zwykły członek nie prowadzi budżetów, planów publicznych, wniosków ani
rozliczeń.

Skarbnik
~~~~~~~~

Skarbnik może:

* zarządzać dofinansowaniami,
* prowadzić plany zamówień publicznych,
* tworzyć i zamykać własne listy zakupów,
* widzieć listy skarbników z tego samego koła,
* tworzyć wnioski o zamówienie,
* przypisywać wniosek do dofinansowania i pozycji planu,
* finalizować wniosek,
* przekazywać wniosek do rozliczeń,
* dodawać faktury,
* kończyć rozliczenia,
* obserwować aktualny budżet koła i sekcji.

Logowanie i rejestracja
-----------------------

Logowanie:

1. Otwórz aplikację.
2. Wpisz e-mail i hasło.
3. Po poprawnym logowaniu aplikacja przenosi do panelu głównego.

Rejestracja:

1. Przejdź do formularza rejestracji.
2. Podaj imię, nazwisko, e-mail, hasło, koło naukowe, sekcję i status
   SAP.
3. Wybierz rolę użytkownika.
4. Po rejestracji zaloguj się na utworzone konto.

Status SAP:

* ``Jestem w SAP`` oznacza, że użytkownik figuruje w systemie SAP.
* ``Nie jestem w SAP`` oznacza brak takiej informacji w profilu.
* W obecnej wersji status jest informacyjny i nie uruchamia integracji z
  SAP.

Pulpit
------

Po zalogowaniu użytkownik widzi swoje dane:

* rolę,
* e-mail,
* koło naukowe,
* sekcję,
* status SAP.

Skarbnik widzi dodatkowo przegląd budżetu:

* budżet całkowity koła,
* kwotę wydaną,
* kwotę zarezerwowaną we wnioskach,
* kwotę dostępną po rezerwacjach,
* procent wykorzystania budżetu.

Kwoty na pulpicie nie są wpisane na sztywno. Są liczone z dofinansowań,
wydanych środków i złożonych wniosków. Po utworzeniu wniosku budżet
dostępny powinien się zmniejszyć.

Katalog przedmiotów
-------------------

Zakładka ``Dodane przedmioty`` jest wspólnym katalogiem produktów.
Katalog jest wspólny dla użytkowników, a nie prywatny dla jednej osoby.

Dodawanie przedmiotu:

1. Otwórz zakładkę ``Dodane przedmioty``.
2. Wybierz dodanie nowego przedmiotu.
3. Podaj nazwę, link, cenę, walutę i podkategorię.
4. Zapisz formularz.
5. Przedmiot pojawi się w katalogu.

Przedmiot w katalogu można później wykorzystać przy dodawaniu pozycji do
listy zakupów.

Sklepy
------

Zakładka ``Sklepy`` służy do prowadzenia listy sklepów, z których koło
może kupować przedmioty.

Dane sklepu:

* nazwa,
* link,
* opinia,
* próg darmowej dostawy,
* status.

Zwykły użytkownik może zgłosić sklep. Skarbnik może sklep zaakceptować,
edytować albo odrzucić, jeśli sklep nie został jeszcze zaakceptowany.

Listy zakupów
-------------

Lista zakupów jest koszykiem dla jednego sklepu. Lista może być otwarta
albo zamknięta.

.. code-block:: text

   Lista otwarta
     można dodawać i usuwać pozycje

   Lista zamknięta
     nie można zmieniać pozycji
     może posłużyć do utworzenia wniosku

Widok zwykłego członka:

* widzi dostępne otwarte listy zakupów z jego koła,
* może dodać przedmiot do listy,
* może usunąć tylko własny wkład z listy,
* nie może zamknąć listy.

Widok skarbnika:

* widzi własne listy,
* widzi listy skarbników z tego samego koła,
* może tworzyć nowe listy,
* może zamykać listy utworzone przez siebie,
* może ponownie otworzyć listę, jeśli proces jeszcze na to pozwala.

Dodanie przedmiotu do listy:

1. Otwórz listę zakupów.
2. Wybierz przedmiot z katalogu albo dodaj nowy.
3. Podaj ilość.
4. Zapisz.

Jeśli kilka osób doda ten sam przedmiot, aplikacja pokazuje łączną ilość,
ale pamięta wkład każdej osoby oddzielnie.

Usunięcie przedmiotu przez zwykłego członka:

1. Otwórz listę.
2. Wybierz pozycję, którą dodałeś.
3. Usuń swój wkład.

Jeżeli inni użytkownicy też dodali ten sam przedmiot, ich ilości
pozostają na liście.

Dofinansowania
--------------

Dofinansowanie jest źródłem pieniędzy. Każde dofinansowanie należy do
jednej sekcji/projektu.

Tworzenie dofinansowania przez skarbnika:

1. Otwórz zakładkę ``Plany publiczne``.
2. Wybierz sekcję/projekt.
3. Podaj nazwę dofinansowania.
4. Podaj organizatora.
5. Podaj osobę podpisującą.
6. Podaj termin wydatkowania.
7. Podaj kwotę dofinansowania.
8. Opcjonalnie dodaj zadania budżetowe.
9. Zapisz.

Zadania budżetowe pomagają opisać, na co mają zostać przeznaczone
środki. Suma zadań nie może być większa niż kwota dofinansowania.

Plany zamówień publicznych
--------------------------

Plan zamówień publicznych jest tworzony dla konkretnego dofinansowania.
Plan składa się z pozycji CPV i kwot planowanych.

Utworzenie planu:

1. Otwórz zakładkę ``Plany publiczne``.
2. Wybierz dofinansowanie.
3. Utwórz plan dla tego dofinansowania.
4. Podaj nazwę planu.
5. Podaj rok planu.
6. Podaj numer planu.
7. Podaj osobę odpowiedzialną.
8. Podaj kurs euro, jeśli jest potrzebny do finalizacji.
9. Zapisz.

Dodanie pozycji planu:

1. Otwórz plan dofinansowania.
2. Dodaj pozycję.
3. Podaj kod CPV.
4. Podaj numer pozycji.
5. Podaj opis pozycji.
6. Podaj planowaną kwotę.
7. Opcjonalnie przypisz kategorię produktu.
8. Zapisz.

Znaczenie kwot:

.. code-block:: text

   Planowana kwota
     ile przewidziano w planie na dany CPV

   Wykorzystano
     ile przypisano do tej pozycji we wnioskach

   Pozostało
     planowana kwota minus wykorzystanie

Jeśli wniosek przekracza pozycję planu, trzeba podać uzasadnienie
odstępstwa.

Wnioski o zamówienie
--------------------

Wniosek o zamówienie jest formalnym etapem zakupu. Skarbnik tworzy
wniosek wtedy, gdy chce realnie kupić przedmioty z list zakupów.

Utworzenie wniosku z zamkniętej listy:

1. Utwórz listę zakupów.
2. Dodaj do niej przedmioty.
3. Zamknij listę.
4. Przejdź do zakładki ``Wnioski zamówień``.
5. Wybierz zamkniętą listę.
6. Uzupełnij dane wniosku.
7. Wskaż dofinansowanie.
8. Wskaż pozycję planu publicznego.
9. Zapisz wniosek.

Utworzenie wniosku ręcznie:

1. Otwórz zakładkę ``Wnioski zamówień``.
2. Wybierz nowy wniosek.
3. Podaj nazwę wniosku.
4. Podaj kwotę.
5. Wybierz dofinansowanie.
6. Wybierz pozycję lub pozycje planu CPV.
7. Jeżeli kwota przekracza plan, wpisz uzasadnienie.
8. Zapisz.

Status zgodności z planem:

.. code-block:: text

   Szkic
     wniosek nie ma pełnych danych planu albo kwoty

   Zgodny z planem
     kwota mieści się w dostępnej pozycji CPV

   Wymaga zgody
     kwota przekracza plan albo zakup nie był zaplanowany

Finalizacja wniosku
-------------------

Finalizacja zamyka część zakupową wniosku. Po finalizacji dane są
traktowane jako podstawa do rozliczenia.

Przebieg:

1. Otwórz wniosek.
2. Wybierz przygotowanie finalizacji.
3. Sprawdź listy zakupów, CPV, kwoty i dofinansowania.
4. Podaj nazwę dokumentu.
5. Podaj datę wartości umowy.
6. Podaj kurs euro.
7. Zapisz finalizację.

Po finalizacji:

* nie można już dodawać pozycji do list powiązanych z wnioskiem,
* system zapisuje snapshot danych planu,
* system wylicza główny CPV,
* wniosek przechodzi do stanu oczekiwania na rozliczenie.

Rozliczenia
-----------

Rozliczenia służą do obsługi faktur i rzeczywistych kwot zakupu.

Przekazanie wniosku do rozliczeń:

1. Otwórz sfinalizowany wniosek.
2. Wybierz przekazanie do rozliczeń.
3. Przejdź do zakładki ``Rozliczenia``.

Dodanie faktury:

1. Otwórz rozliczenie.
2. Dodaj fakturę.
3. Podaj numer faktury.
4. Podaj datę wystawienia.
5. Podaj sprzedawcę i NIP.
6. Podaj kwotę netto i VAT.
7. Wybierz status faktury.
8. Zapisz.

Przypisanie faktury do linii:

1. Otwórz linię rozliczeniową.
2. Wybierz fakturę.
3. Podaj rzeczywistą kwotę brutto.
4. Zapisz.

Zakończenie rozliczenia jest możliwe dopiero wtedy, gdy każda linia
rozliczenia ma przypisaną fakturę.

Historia
--------

Po zakończeniu rozliczenia wniosek trafia do historii. Historia służy do
podglądu zakończonych spraw. Nie powinna być używana do bieżącego
edytowania zakupów.

Najczęstsze sytuacje problemowe
-------------------------------

Nie widzę listy zakupów
~~~~~~~~~~~~~~~~~~~~~~~

Możliwe przyczyny:

* lista należy do innego koła,
* lista jest zamknięta,
* lista nie jest powiązana z dostępnym kontekstem zakupowym,
* zalogowany użytkownik nie jest skarbnikiem ani autorem listy.

Nie mogę dodać pozycji do listy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Możliwe przyczyny:

* lista jest zamknięta,
* podano ilość mniejszą lub równą zero,
* przedmiot nie ma poprawnej podkategorii,
* lista należy do nieprawidłowego finansowania.

Nie mogę usunąć pozycji z listy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Możliwe przyczyny:

* lista jest zamknięta,
* próbujesz usunąć pozycję dodaną przez inną osobę,
* nie przekazano identyfikatora zalogowanego użytkownika.

Nie mogę utworzyć wniosku
~~~~~~~~~~~~~~~~~~~~~~~~~

Możliwe przyczyny:

* dofinansowanie nie należy do wybranej sekcji,
* kwota przekracza dostępne środki dofinansowania,
* kwota przekracza budżet sekcji,
* pozycja planu należy do innego dofinansowania,
* przekroczono plan i nie wpisano uzasadnienia,
* zamknięta lista należy do innego skarbnika.

Nie mogę zakończyć rozliczenia
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Możliwe przyczyny:

* rozliczenie nie jest powiązane z wnioskiem,
* co najmniej jedna linia nie ma przypisanej faktury,
* wniosek nie został przekazany do rozliczeń.

Rekomendowany pełny przebieg pracy skarbnika
--------------------------------------------

1. Utwórz albo sprawdź dofinansowanie.
2. Utwórz plan publiczny dla dofinansowania.
3. Dodaj pozycje CPV do planu.
4. Utwórz listę zakupów dla sklepu.
5. Dodaj przedmioty do listy.
6. Zamknij listę.
7. Utwórz wniosek z zamkniętej listy.
8. Przypisz wniosek do dofinansowania i pozycji planu.
9. Sprawdź budżet na pulpicie.
10. Przygotuj finalizację.
11. Zatwierdź finalizację.
12. Przekaż wniosek do rozliczeń.
13. Dodaj faktury.
14. Przypisz faktury do linii rozliczenia.
15. Zakończ rozliczenie.
