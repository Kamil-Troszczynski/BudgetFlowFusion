-- Mockup data for BudgetFlowFusion application
INSERT INTO association (association_name) VALUES
('Koło Naukowe Robotyków'),
('Koło Naukowe Obróbki Skrawaniem');


INSERT INTO project (project_name, description, allocated_budget, rest_of_budget, association_id) VALUES
('KNR Rover Team', 'Projekt łazika marsjańskiego.', 150000.00, 150000.00, 1),
('Sekcja Robotów Kroczących', 'Melsony i Meldogi.', 8000.00, 8000.00, 1),
('KNR Drone', 'Sekcja dronów.', 70000.00, 70000.00, 1),
('Rezerwa koła', 'Środki ogólnokołowe.', 10000.00, 10000.00, 1),
('Sekcja Druku 3D', 'Druk 3D', 15000.00, 15000.00, 1);


INSERT INTO association_budget (association_budget_name, total_budget, spent_money, public_purchase_plan_list_id) VALUES
('Dofinansowanie dziekana MEiL', 30000.00, 0.00, NULL),
('Fundusz Promocji Uczelnii', 50000.00, 0.00, NULL);


INSERT INTO project_budget (project_budget_name, total_budget, spent_money, association_budget_id, project_id) VALUES
('KNR Rover Team', 20000.00, 0.00, 1, 1),
('Sekcja Robotów Kroczących', 10000.00, 0.00, 1, 2),
('KNR Drone', 5000.00, 0.00, 1, 3),
('Rezerwa koła', 10000.00, 0.00, 1, 4),
('Sekcja Druku 3D', 15000.00, 0.00, 1, 5);


INSERT INTO project_finance_manager (login, password_hash, access) VALUES
('skarbnik_glowny@kolo.edu.pl', 'hashed_123', true),
('zastepca_skarbnika@kolo.edu.pl', 'hashed_789', true);



INSERT INTO student (student_id, name, surname, login, password_hash, position, is_in_sap, project_finance_manager_id, association_id) VALUES
(1, 'Michał', 'Kowalski', 'michal.kowalski@kolo.edu.pl', 'hashed_123', 'KNR Rover Team - Lider', true, 1, 1),
(2, 'Anna', 'Nowak', 'anna.nowak@kolo.edu.pl', 'hashed_456', 'Sekcja Druku 3D - Koordynator', false, NULL, 1),
(3, 'Piotr', 'Adamczyk', 'piotr.adamczyk@kolo.edu.pl', 'hashed_111', 'KNR Drone - Konstruktor', true, NULL, 1),
(4, 'Kasia', 'Wiśniewska', 'kasia.w@kolo.edu.pl', 'hashed_222', 'Sekcja Robotów Kroczących', false, 2, 1),
(5, 'Jan', 'Zieliński', 'jan.zielinski@kolo.edu.pl', 'hashed_333', 'KNR Rover Team - Elektronik', true, NULL, 1),
(6, 'Mateusz', 'Wójcik', 'mateusz.w@kolo.edu.pl', 'hashed_555', 'KNR Drone - Programista', false, NULL, 1),
(7, 'Aleksandra', 'Dubaj', 'ola.dubaj@kolo.edu.pl', 'hashed_666', 'Sekcja Druku 3D - Technolog', true, NULL, 1),
(8, 'Łukasz', 'Mazur', 'lukasz.m@kolo.edu.pl', 'hashed_000', 'Sekcja Robotów Kroczących - Lider', true, 2, 1);

INSERT INTO funding (funding_name, funding_price, spent_money, project_id, project_budget_id, association_budget_id) VALUES
('Grant Rektora - KNR Rover Team', 20000.00, 0.00, 1, 1, 1),
('VWFS - KNR Rover Team', 10000.00, 0.00, 1, 1, 1),
('LMCO - KNR Rover Team', 20000.00, 0.00, 1, 1, 1),
('KNTI - KNR Rover Team', 70000.00, 0.00, 1, 1, 1),
('NZN - KNR Rover Team', 10000.00, 0.00, 1, 1, 1),
('KNTI - KNR Drone', 70000.00, 0.00, 3, 3, 1),
('Orlen - KNR Drone', 50000.00, 0.00, 3, 3, 1),
('Grant Rektora - Meldog', 50000.00, 0.00, 2, 2, 1);


INSERT INTO public_purchase_plan_list (public_plan_list_name, plan_year, funding_id) VALUES
('Plan ZP - Grant Rektora - KNR Rover Team', 2026, 1),
('Plan ZP - VWFS - KNR Rover Team', 2026, 2),
('Plan ZP - LMCO - KNR Rover Team', 2026, 3),
('Plan ZP - KNTI - KNR Rover Team', 2026, 4),
('Plan ZP - NZN - KNR Rover Team', 2026, 5),
('Plan ZP - KNTI - KNR Drone', 2026, 6),
('Plan ZP - Orlen - KNR Drone', 2026, 7),
('Plan ZP - Grant Rektora - Meldog', 2026, 8);


INSERT INTO shop (shop_id, shop_name, link, opinion, address, delivery_time, is_recommended, free_delivery_threshold, status) VALUES
(1, 'Botland', 'https://botland.com.pl', 'Ocena 4.8/5. Bardzo dobry sklep na robotykę i elektronikę, szybkie dostawy, sensowna dostępność i mało problemów reklamacyjnych.', 'Online / Kępno', NOW() + INTERVAL '2 days', true, 200.00, 'approved'),
(2, 'TME Electronics', 'https://www.tme.eu/pl', 'Ocena 4.9/5. Jeden z najlepszych sklepów na elektronikę w Polsce, szeroki katalog, pewne stany magazynowe i bardzo szybka logistyka.', 'Łódź, Ustronna 41', NOW() + INTERVAL '1 day', true, 500.00, 'approved'),
(3, 'Kamami', 'https://kamami.pl', 'Ocena 4.6/5. Dobry wybór modułów embedded i części do prototypowania, czasem mniejsza dostępność niż w TME, ale nadal bardzo solidnie.', 'Online', NOW() + INTERVAL '3 days', true, 300.00, 'approved'),
(4, 'Allegro (Smart)', 'https://allegro.pl', 'Ocena 2.4/5. Nie szukać nic tam, bo często są chińskie faktury.', 'Online', NOW() + INTERVAL '2 days', false, 45.00, 'approved'),
(5, 'Mouser Electronics', 'https://www.mouser.pl', 'Ocena 4.7/5. Bardzo mocny wybór specjalistycznych komponentów, świetny przy trudniejszych BOM-ach, ale import bywa droższy.', 'Monachium / USA (Import)', NOW() + INTERVAL '5 days', true, 250.00, 'approved'),
(6, '3DJake', 'https://www.3djake.pl', 'Ocena 4.7/5. Bardzo dobry sklep do druku 3D, sensowne ceny filamentów', 'Niemcy', NOW() + INTERVAL '4 days', true, 220.00, 'approved'),
(7, 'Kastal', 'https://www.kastal.pl', 'Ocena 3.4/5. Przydatny przy bardziej przemysłowych zamówieniach, ale terminy i komunikacja potrafią być odczuwalnie gorsze.', 'Warszawa', NOW() + INTERVAL '12 days', false, 0.00, 'approved'),
(8, 'Aluxprofile', 'https://www.aluxprofile.pl', 'Ocena 4.4/5. Dobry dostawca profili i akcesoriów konstrukcyjnych, rozsądna jakość i przewidywalne terminy.', 'Poznań', NOW() + INTERVAL '3 days', true, 600.00, 'approved'),
(9, 'EBMiA', 'https://www.ebmia.pl', 'Ocena 2.8/5. Sklep ma szeroką ofertę mechaniki, ale bywa chaotyczny w dostępności i terminach, więc do ważnych zamówień lepiej mieć alternatywę.', 'Online', NOW() + INTERVAL '15 days', false, 400.00, 'approved'),
(10, 'Farnell', 'https://pl.farnell.com', 'Ocena 4.7/5. Bardzo solidny dystrybutor dla inżynierii elektronicznej, dobry wybór przemysłowych komponentów i dokumentacji.', 'Europa / Magazyn centralny', NOW() + INTERVAL '4 days', true, 300.00, 'approved'),
(11, 'RS Components', 'https://pl.rs-online.com', 'Ocena 4.7/5. Mocny sklep na aparaturę, automatykę i elektronikę, zwykle wysoka pewność zakupu i dobra obsługa firmowa.', 'Warszawa / Europa', NOW() + INTERVAL '3 days', true, 250.00, 'approved'),
(12, 'DigiKey', 'https://www.digikey.pl', 'Ocena 4.8/5. Świetny do specjalistycznych układów i trudnych komponentów, bardzo dobry katalog i szybka wysyłka jak na import.', 'USA / Europa', NOW() + INTERVAL '5 days', true, 250.00, 'approved'),
(13, 'LCSC', 'https://www.lcsc.com', 'Ocena 1/5. Nie kupować nic od nich', 'Shenzhen, Chiny', NOW() + INTERVAL '10 days', false, 0.00, 'approved'),
(14, 'JLCPCB', 'https://jlcpcb.com', 'Ocena 3.6/5. Bardzo opłacalne PCB', 'Shenzhen, Chiny', NOW() + INTERVAL '9 days', false, 0.00, 'approved'),
(15, 'AliExpress', 'https://www.aliexpress.com', 'Ocena 1/5. Zakaz zamawiania, bo sie nie rozliczymy xd', 'Chiny / marketplace', NOW() + INTERVAL '14 days', false, 0.00, 'approved'),
(16, 'Banggood', 'https://www.banggood.com', 'Ocena 1/5. Chinczyk, zakaz zamawiania', 'Chiny / marketplace', NOW() + INTERVAL '12 days', false, 0.00, 'approved'),
(17, 'Maritex', 'https://www.maritex.com.pl', 'Ocena 4.5/5. Dobry polski dystrybutor elektroniki, szczególnie przy komponentach przemysłowych i zasilaniu.', 'Gdynia', NOW() + INTERVAL '2 days', true, 350.00, 'approved'),
(18, 'Conrad', 'https://www.conrad.pl', 'Ocena 4.2/5. Sensowny sklep na aparaturę i wyposażenie stanowisk, zwykle drożej niż u dystrybutorów stricte inżynierskich.', 'Europa / Online', NOW() + INTERVAL '4 days', true, 199.00, 'approved');

INSERT INTO grouped_shops_list_by_cpv_category_and_funding (allocated_money) VALUES
(20000.00),
(10000.00),
(5000.00);


INSERT INTO product_category (product_category_name, description, cpv, shop_purchase_list_id, public_purchase_plan_id) VALUES
('Elektronika i Mikrokontrolery', 'Płytki drukowane, układy scalone, elementy SMD/THT', '31700000-3', NULL, NULL),
('Zasilanie i Okablowanie',       'Akumulatory, przetwornice, przewody i złącza prądowe', '31700000-3', NULL, NULL),
('Mechanika i Konstrukcje',       'Materiały bazowe, profile, ramy, elementy CNC', '44000000-0', NULL, NULL),
('Napędy i Aktuatory',            'Silniki, serwomechanizmy, przekładnie, sterowniki ESC', '42000000-6', NULL, NULL),
('Systemy Wizyjne i Sensoryka',   'Kamery, LIDARy, czujniki dedykowane, optyka', '35120000-1', NULL, NULL),
('Komunikacja i Telemetria',      'Moduły radiowe, GPS, anteny, aparatura RC', '35120000-1', NULL, NULL),
('Druk 3D i Prototypowanie',      'Filamenty, żywice, części zamienne drukarek', '19520000-7', NULL, NULL),
('Warsztat i Narzędzia',          'Wyposażenie stanowisk, narzędzia ręczne i pomiarowe', '43800000-1', NULL, NULL),
('Oprogramowanie i Licencje',     'Soft inżynieryjny, licencje CAD, pakiety cloud', '48000000-8', NULL, NULL);


INSERT INTO product_subcategory (product_subcategory_name, description, product_category_id) VALUES
('Komputery jednopłytkowe (SBC)', 'Raspberry Pi, Nvidia Jetson, Orange Pi i akcesoria', 1),
('Mikrokontrolery i płytki deweloperskie', 'Arduino, STM32, ESP32, Teensy, płytki stykowe', 1),
('Komponenty elektroniczne SMD/THT', 'Rezystory, kondensatory, diody, tranzystory, układy scalone', 1),
('Płytki drukowane (PCB)',        'Zamówienia na wykonanie dedykowanych płytek w seriach/prototypach', 1),

('Akumulatory i pakiety Li-Po',   'Pakiety zasilające Li-Po, Li-Ion, ogniwa, ładowarki, BMS', 2),
('Przetwornice i regulatory napięcia', 'Moduły BEC/UBEC, przetwornice step-up/step-down, filtry zasilania', 2),
('Złącza i konektory',            'Wtyki XT60, XT90, JST, Goldbee, MR30, kołki goldpin', 2),
('Przewody i izolacje',           'Kable silikonowe, taśmy sygnałowe, oploty, rurki termokurczliwe', 2),

('Profile i łączniki konstrukcyjne', 'Profile aluminiowe T-SLOT/V-SLOT, narożniki, wpusty teowe', 3),
('Materiały surowe (Formatki)',    'Płyty z włókna węglowego (karbon), aluminium, PMMA, poliwęglan', 3),
('Elementy złączne (Drobnica)',   'Śruby imbusowe, nakrętki samohamowne, podkładki, dystanse mosiężne', 3),
('Łożyskowanie i prowadzenie liniowe', 'Łożyska kulkowe, liniowe, wałki hartowane, podpory wałków', 3),

('Silniki bezszczotkowe (BLDC)',   'Silniki do dronów, bezszczotkowe silniki napędowe o dużym momencie', 4),
('Silniki DC i krokowe',          'Silniki szczotkowe z przekładniami, silniki krokowe do osi/manipulatorów', 4),
('Serwomechanizmy',               'Serwa modelarskie cyfrowe/analogowe, serwa klasy robotycznej', 4),
('Sterowniki silników i ESC',     'Regulatory obrotów ESC, sterowniki mostkowe H, drivery krokowe', 4),
('Przeniesienie napędu',          'Paski zębate, koła pasowe, sprzęgła elastyczne, koła zębate, łańcuchy', 4),

('Kamery i moduły optyczne',      'Kamery MIPI CSI, kamery USB, obiektywy, filtry IR, kamery głębi', 5),
('Sensory IMU i orientacji',      'Żyroskopy, akcelerometry, magnetometry, kompasy elektroniczne', 5),
('Dalmierze i LIDARy',            'Skanery laserowe, czujniki sonarowe, czujniki czasu lotu (ToF)', 5),
('Czujniki środowiskowe i krańcowe', 'Krańcówki mechaniczne/optyczne, czujniki temperatury, nacisku', 5),

('Aparatury i odbiorniki RC',     'Nadajniki i odbiorniki sterowania radiowego (np. Elrs, Crossfire)', 6),
('Moduły telemetryczne i radiomodem', 'Moduły LoRa, telemetria 433/868/915 MHz, transceivery radiowe', 6),
('Moduły lokalizacji (GPS/GNSS)', 'Odbiorniki GPS, GLONASS, RTK, anteny GPS', 6),
('Moduły sieciowe (Wi-Fi/BT/GSM)', 'Modemy LTE/5G, karty sieciowe, moduły Bluetooth dużej mocy', 6),

('Filamenty FDM',                 'Szpule PLA, PETG, ABS, ASA, TPU, Nylon', 7),
('Żywice fotopolimerowe (SLA/DLP)', 'Żywice UV standardowe, inżynieryjne (tough/flexible)', 7),
('Części zamienne drukarek 3D',   'Dysze, rurki PTFE, bloki, grzałki, paski, folie FEP, folie PEI', 7),

('Narzędzia lutownicze i ESD',    'Stacje lutownicze, groty, cyny, topniki, plecionki, maty ESD', 8),
('Elektronarzędzia warsztatowe',  'Wkrętarki, mini-szlifierki (Dremel), wiertarki, wyrzynarki', 8),
('Narzędzia ręczne montażowe',    'Klucze imbusowe, szczypce precyzyjne, obcinaczki, śrubokręty, pilniki', 8),
('Aparatura pomiarowa',           'Multimetry, suwmiarki cyfrowe, oscyloskopy, analizatory stanów', 8);


INSERT INTO public_purchase_plan (public_purchase_plan_name, cpv_code, cost, funding_id, gslbccf_id, public_purchase_plan_list_id) VALUES
('CPV 42000000', 42000000, 5000.00, 1, 1, 1),
('CPV 31700000', 31700000, 3000.00, 2, 2, 2);


INSERT INTO item (name, price, currency, link, created_at, tax_rate, status, product_subcategory_id, student_id, shop_id) VALUES
('Silnik DC z przekładnią 12V',     145.50,  'PLN', 'https://botland.com.pl', NOW(), 23.00, 'approved', 1, 2, 1),
('Kamera Intel RealSense D435i',   1850.00,  'PLN', 'https://botland.com.pl', NOW(), 23.00, 'approved', 2, 2, 1),
('Filament PETG 1kg Czarny',         65.00,  'PLN', 'https://botland.com.pl', NOW(), 23.00, 'approved', 3, 2, 1),
('Płytka STM32 Nucleo-F446RE',       99.90,  'PLN', 'https://tme.eu',         NOW(), 23.00, 'approved', 4, 1, 2),
('Zestaw śrubokrętów precyzyjnych', 120.00,  'PLN', 'https://allegro.pl',     NOW(), 23.00, 'pending',  5, 4, 4),
('Sterownik Silnika BLDC 30A',       85.00,  'PLN', 'https://kamami.pl',      NOW(), 23.00, 'pending',  1, 3, 3),
('Przekładnia redukcyjna 12V',       45.00,  'PLN', 'https://botland.com.pl', NOW(), 23.00, 'pending',  2, 2, 1),
('Kamera głębi ZED2i',               45.00,  'PLN', 'https://botland.com.pl', NOW(), 23.00, 'pending',  2, 2, 1),
('Czujnik odległości VL53L0X',       45.00,  'PLN', 'https://botland.com.pl', NOW(), 23.00, 'pending',  2, 2, 1),
('Zestaw przewodów żeńsko-męskich',  15.50,  'PLN', 'https://botland.com.pl', NOW(), 23.00, 'pending',  2, 2, 1),
('Układ FPGA Xilinx Artix-7',        85.00,  'USD', 'https://mouser.com/xilinx', NOW(), 23.00, 'approved', 4, 5, 5),
('Sensor IMU 9-osiowy Heuristic high-prec', 45.50, 'EUR', 'https://mouser.com/sensors', NOW(), 23.00, 'pending', 4, 1, 5),
('Skaner laserowy LiDAR Hokuyo URG', 1200.00, 'USD', 'https://digikey.com/lidar', NOW(), 23.00, 'pending', 2, 3, 6),
('Mikrokontroler ESP32-WROOM-32E 10 szt', 35.00, 'EUR', 'https://digikey.com/esp32', NOW(), 23.00, 'approved', 4, 6, 6),
('Oscyloskop cyfrowy Siglent SDS1104X-E', 2450.00, 'PLN', 'https://tme.eu/aparatura', NOW(), 23.00, 'approved', 4, 1, 2),
('Przewód silikonowy 14AWG Czarny 10m', 65.00, 'PLN', 'https://tme.eu/kable', NOW(), 23.00, 'approved', 3, 5, 2),
('Złącza XT60 wysokoamperowe 5 par', 24.00, 'PLN', 'https://tme.eu/zlacza', NOW(), 23.00, 'pending', 2, 5, 2);

INSERT INTO shop_purchase_list (priority, cost, created_at, gslbccf_id, settlement_id, funding_id, shop_id, student_id) VALUES
(1, 2562.00, NOW(), 1, NULL, 1, 1, 2),
(2,  399.60, NOW(), 2, NULL, 2, 2, 1);


INSERT INTO shop_purchase_list_item (shop_purchase_list_id, item_id, amount) VALUES
(1, 1, 4),
(1, 2, 1),
(1, 3, 2),
(2, 4, 4);


INSERT INTO purchase_request (purchase_request_name, budget_allocated_for_the_order, if_service, used_cpv_id, created_at, can_add, project_budget_id, funding_id, public_purchase_plan_id, plan_compliance_status, gslbccf_id, project_finance_manager_id, finalization_status) VALUES
('Wniosek: Napęd i wizja łazika',      2562.00, false, 42000000, NOW(), false, 1, 1, 1, 'compliant', 1, 1, 'settlement'),
('Wniosek: Mikrokontrolery do ramienia', 399.60, false, 31700000, NOW(), false, 2, 2, 2, 'compliant', 2, 2, 'settlement');


INSERT INTO settlement (created_at, paid_by_project_finance_manager_id, purchase_request_id) VALUES
(NOW(), 1, 1),
(NOW(), 2, 2);


UPDATE shop_purchase_list SET settlement_id = 1 WHERE shop_purchase_list_id = 1;
UPDATE shop_purchase_list SET settlement_id = 2 WHERE shop_purchase_list_id = 2;


INSERT INTO invoice (number, issue_date, seller_name, seller_nip, net_total, vat_total, status, created_at, settlement_id) VALUES
('F/2026/05/HAL-001', CURRENT_DATE, 'Botland', '1234567890', 2082.93, 479.07, 'paid', NOW(), 1),
('F/2026/05/TME-002', CURRENT_DATE, 'TME', '0987654321',  324.88,  74.72, 'pending', NOW(), 2);


UPDATE product_category SET shop_purchase_list_id = 1, public_purchase_plan_id = 1 WHERE product_category_id = 1;


-- Extended demo data for public plans, finalization and settlements

UPDATE funding SET
    organizer = CASE funding_id
        WHEN 1 THEN 'Politechnika Warszawska'
        WHEN 2 THEN 'Volkswagen Financial Services'
        WHEN 3 THEN 'Lockheed Martin'
        WHEN 4 THEN 'Ministerstwo Nauki i Szkolnictwa Wyższego'
        WHEN 5 THEN 'Ministerstwo Nauki i Szkolnictwa Wyższego'
        WHEN 6 THEN 'Ministerstwo Nauki i Szkolnictwa Wyższego'
        WHEN 7 THEN 'Orlen'
        WHEN 8 THEN 'Politechnika Warszawska'
        ELSE organizer
    END,
    signing_person = CASE funding_id
        WHEN 1 THEN 'dr inż. Kamil Futyma'
        WHEN 2 THEN 'dr inż. Krzysztof Mianowski'
        WHEN 3 THEN 'dr inż. Krzysztof Mianowski'
        WHEN 4 THEN 'dr inż. Krzysztof Mianowski'
        WHEN 5 THEN 'dr inż. Krzysztof Mianowski'
        WHEN 6 THEN 'dr inż. Krzysztof Mianowski'
        WHEN 7 THEN 'dr inż. Krzysztof Mianowski'
        WHEN 8 THEN 'dr inż. Kamil Futyma'
        ELSE signing_person
    END,
    spending_deadline = CASE funding_id
        WHEN 1 THEN DATE '2026-06-30'
        WHEN 2 THEN DATE '2026-12-31'
        WHEN 3 THEN DATE '2026-12-31'
        WHEN 4 THEN DATE '2026-10-21'
        WHEN 5 THEN DATE '2026-02-28'
        WHEN 6 THEN DATE '2026-06-10'
        WHEN 7 THEN DATE '2026-08-31'
        WHEN 8 THEN DATE '2027-06-30'
        ELSE spending_deadline
    END;

UPDATE public_purchase_plan_list SET
    plan_number = 'ZP/2026/' || LPAD(public_purchase_plan_list_id::TEXT, 2, '0'),
    fund_responsible_person = CASE
        WHEN funding_id IN (1, 3, 4, 5) THEN 'Michał Kowalski'
        ELSE 'Kasia Wiśniewska'
    END,
    euro_exchange_rate = 4.6371;

INSERT INTO project_finance_manager (login, password_hash, access) VALUES
('rozliczenia@kolo.edu.pl', 'hashed_444', true);

INSERT INTO student (student_id, name, surname, login, password_hash, position, is_in_sap, project_finance_manager_id, association_id) VALUES
(9, 'Natalia', 'Szymańska', 'natalia.szymanska@kolo.edu.pl', 'hashed_444', 'Skarbnik ds. rozliczeń', true, 3, 1),
(10, 'Tomasz', 'Lewandowski', 'tomasz.lewandowski@kolo.edu.pl', 'hashed_777', 'KNR Rover Team - Mechanik', false, NULL, 1),
(11, 'Maria', 'Kamińska', 'maria.kaminska@kolo.edu.pl', 'hashed_888', 'KNR Drone - Elektronika', true, NULL, 1),
(12, 'Paweł', 'Kaczmarek', 'pawel.kaczmarek@kolo.edu.pl', 'hashed_999', 'Sekcja Druku 3D - Operator', false, NULL, 1);

INSERT INTO funding (funding_name, organizer, signing_person, spending_deadline, funding_price, spent_money, project_id, project_budget_id, association_budget_id) VALUES
('Grant Rektora - Druk 3D', 'Politechnika Warszawska', 'dr inż. Kamil Futyma', DATE '2026-12-20', 18000.00, 1200.00, 5, 5, 1),
('Rezerwa koła', 'w', 'dr inż. Kamil Futyma', DATE '2026-06-30', 9000.00, 900.00, 4, 4, 1),
('Duża pula', 'RKN SSPW', 'Wiceprzewodniczący RKN', DATE '2026-08-05', 15000.00, 0.00, 3, 3, 1);

INSERT INTO funding_task (funding_id, task_name, task_budget) VALUES
(1, 'Napęd i systemy wizyjne łazika', 12000.00),
(1, 'Elementy konstrukcyjne łazika', 5000.00),
(6, 'Elektronika pokładowa drona', 18000.00),
(8, 'Podzespoły robota kroczącego', 22000.00),
(9, 'Materiały i filamenty do prototypowania', 9000.00),
(9, 'Serwis drukarek 3D', 4500.00),
(10, 'Zakupy awaryjne i eksploatacyjne', 9000.00),
(11, 'Czujniki i moduły AI', 16000.00);

INSERT INTO public_purchase_plan_list (public_plan_list_name, plan_year, plan_number, fund_responsible_person, euro_exchange_rate, funding_id) VALUES
('Plan ZP - Grant Rektora - Druk 3D', 2026, 'ZP/2026/09', 'dr inż. Kamil Futyma', 4.6371, 9),
('Plan ZP - Rezerwa koła', 2026, 'ZP/2026/10', 'dr inż. Kamil Futyma', 4.6371, 10),
('Plan ZP - Duża pula', 2026, 'ZP/2026/11', 'Wiceprzewodniczący RKN', 4.6371, 11);

INSERT INTO grouped_shops_list_by_cpv_category_and_funding (allocated_money) VALUES
(9000.00),
(4500.00),
(12000.00),
(1800.00),
(3200.00),
(6200.00);

INSERT INTO public_purchase_plan (public_purchase_plan_name, cpv_code, plan_position_number, cost, funding_id, gslbccf_id, public_purchase_plan_list_id) VALUES
('Elementy elektroniczne do prototypów', '31700000-3', '1.1', 8000.00, 1, 1, 1),
('Materiały konstrukcyjne do łazika', '44000000-0', '1.2', 4500.00, 1, 3, 1),
('Licencje i oprogramowanie CAD', '48000000-8', '4.1', 6000.00, 4, NULL, 4),
('Filamenty i żywice do druku 3D', '19520000-7', '9.1', 9000.00, 9, 4, 9),
('Serwis urządzeń laboratoryjnych', '50300000-8', '9.2', 4500.00, 9, 5, 9),
('Czujniki wizyjne i AI dla drona', '35120000-1', '11.1', 12000.00, 11, 6, 11),
('Materiały eksploatacyjne koła', '30192000-1', '10.1', 1800.00, 10, 7, 10),
('Narzędzia warsztatowe', '43800000-1', '10.2', 3200.00, 10, 8, 10);


INSERT INTO item (name, price, currency, link, created_at, tax_rate, status, product_subcategory_id, student_id, shop_id) VALUES
('Filament PA-CF 1kg', 219.00, 'PLN', 'https://3djake.pl/pa-cf', NOW(), 23.00, 'approved', 3, 7, 6),
('Żywica techniczna Tough Resin 1L', 355.00, 'PLN', 'https://3djake.pl/resin', NOW(), 23.00, 'approved', 3, 12, 6),
('Zestaw dysz hardened steel', 129.00, 'PLN', 'https://3djake.pl/nozzles', NOW(), 23.00, 'approved', 3, 12, 6),
('Czujnik optyczny flow PMW3901', 89.00, 'PLN', 'https://botland.com.pl/pmw3901', NOW(), 23.00, 'approved', 4, 11, 1),
('Kamera global shutter Arducam', 620.00, 'PLN', 'https://botland.com.pl/arducam', NOW(), 23.00, 'approved', 2, 11, 1),
('Komputer pokładowy Raspberry Pi 5 8GB', 399.00, 'PLN', 'https://botland.com.pl/rpi5', NOW(), 23.00, 'approved', 4, 6, 1),
('Taśma kaptonowa 50mm', 39.00, 'PLN', 'https://allegro.pl/kapton', NOW(), 23.00, 'approved', 5, 10, 4),
('Smar silikonowy techniczny', 48.00, 'PLN', 'https://allegro.pl/smar', NOW(), 23.00, 'approved', 5, 10, 4),
('Profil aluminiowy 2020 1m', 33.00, 'PLN', 'https://aluxprofile.pl/2020', NOW(), 23.00, 'approved', 3, 10, 8),
('Łożysko liniowe LM8UU 10 szt', 42.00, 'PLN', 'https://ebmia.pl/lm8uu', NOW(), 23.00, 'pending', 1, 5, 9),
('Licencja KiCad plugin premium', 499.00, 'PLN', 'https://example.com/kicad-plugin', NOW(), 23.00, 'pending', 4, 3, 4),
('Moduł telemetryczny LoRa 868MHz', 159.00, 'PLN', 'https://kamami.pl/lora', NOW(), 23.00, 'approved', 4, 6, 3);

INSERT INTO shop_purchase_list (priority, cost, created_at, gslbccf_id, settlement_id, funding_id, shop_id, student_id, market_research_comment, market_research_file_name) VALUES
(1, 1026.00, NOW() - INTERVAL '18 days', 4, NULL, 9, 6, 7, 'Porównano ceny 3DJake, Botland i Allegro. Wybrano najniższy koszt z dostawą.', 'porownanie_filamenty_3d.pdf'),
(2, 450.00, NOW() - INTERVAL '14 days', 5, NULL, 9, 6, 12, NULL, NULL),
(1, 1108.00, NOW() - INTERVAL '10 days', 6, NULL, 11, 1, 11, 'Porównano Botland i Kamami, Botland miał krótszy termin dostawy.', 'czujniki_ai_dron_porownanie.xlsx'),
(3, 174.00, NOW() - INTERVAL '9 days', 7, NULL, 10, 4, 10, NULL, NULL),
(2, 990.00, NOW() - INTERVAL '7 days', 8, NULL, 10, 8, 10, 'Zakup powyżej 500 zł, porównano Aluxprofile i EBMiA.', 'profile_narzedzia_porownanie.pdf'),
(1, 318.00, NOW() - INTERVAL '4 days', 6, NULL, 11, 3, 6, NULL, NULL);

INSERT INTO shop_purchase_list_item (shop_purchase_list_id, item_id, amount) VALUES
(3, 18, 2),
(3, 19, 1),
(3, 20, 1),
(4, 19, 1),
(4, 20, 1),
(5, 21, 1),
(5, 22, 1),
(5, 23, 1),
(6, 24, 2),
(6, 25, 2),
(6, 26, 20),
(7, 27, 5),
(7, 28, 3),
(7, 26, 15),
(8, 29, 2);

INSERT INTO shop_purchase_list_item_contribution (shop_purchase_list_id, item_id, student_id, amount, created_at) VALUES
(1, 1, 2, 2, NOW() - INTERVAL '17 days'),
(1, 2, 2, 1, NOW() - INTERVAL '17 days'),
(1, 3, 7, 1, NOW() - INTERVAL '17 days'),
(4, 19, 12, 1, NOW() - INTERVAL '12 days'),
(5, 21, 11, 1, NOW() - INTERVAL '9 days'),
(6, 25, 10, 2, NOW() - INTERVAL '6 days');

INSERT INTO purchase_request (
    purchase_request_name,
    budget_allocated_for_the_order,
    if_service,
    used_cpv_id,
    created_at,
    can_add,
    document_request_name,
    contract_value_date,
    euro_exchange_rate,
    main_cpv_code,
    final_net_total,
    final_gross_total,
    finalization_status,
    finalized_at,
    project_budget_id,
    funding_id,
    public_purchase_plan_id,
    plan_compliance_status,
    gslbccf_id,
    project_finance_manager_id
) VALUES
('Wniosek: Materiały do druku 3D', 1026.00, false, '19520000-7', NOW() - INTERVAL '17 days', false, 'WN/DRUK3D/2026/01', CURRENT_DATE - INTERVAL '17 days', 4.6371, '19520000-7', 834.15, 1026.00, 'settlement', NOW() - INTERVAL '16 days', 5, 9, 6, 'compliant', 4, 3),
('Wniosek: Serwis drukarki laboratoryjnej', 450.00, true, '50300000-8', NOW() - INTERVAL '14 days', false, 'WN/SERWIS/2026/02', CURRENT_DATE - INTERVAL '14 days', 4.6371, '50300000-8', 365.85, 450.00, 'accounting_pending', NOW() - INTERVAL '13 days', 5, 9, 7, 'compliant', 5, 3),
('Wniosek: Czujniki AI do drona', 1108.00, false, '35120000-1', NOW() - INTERVAL '10 days', false, 'WN/DRON/2026/03', CURRENT_DATE - INTERVAL '10 days', 4.6371, '35120000-1', 900.81, 1108.00, 'settlement', NOW() - INTERVAL '9 days', 3, 11, 8, 'compliant', 6, 2),
('Wniosek: Materiały eksploatacyjne rezerwa', 174.00, false, '30192000-1', NOW() - INTERVAL '9 days', false, 'WN/REZERWA/2026/04', CURRENT_DATE - INTERVAL '9 days', 4.6371, '30192000-1', 141.46, 174.00, 'prepared', NULL, 4, 10, 9, 'compliant', 7, 1),
('Wniosek: Profile i narzędzia warsztatowe', 990.00, false, '43800000-1', NOW() - INTERVAL '7 days', false, 'WN/WARSZTAT/2026/05', CURRENT_DATE - INTERVAL '7 days', 4.6371, '43800000-1', 804.88, 990.00, 'settled', NOW() - INTERVAL '6 days', 4, 10, 10, 'compliant', 8, 1),
('Wniosek: Telemetria LoRa', 318.00, false, '35120000-1', NOW() - INTERVAL '4 days', true, NULL, NULL, NULL, NULL, NULL, NULL, 'draft', NULL, 3, 11, 8, 'compliant', 6, 2);

INSERT INTO purchase_request_funding_allocation (purchase_request_id, funding_id, allocated_amount) VALUES
(3, 9, 1026.00),
(4, 9, 450.00),
(5, 11, 1108.00),
(6, 10, 174.00),
(7, 10, 990.00),
(8, 11, 318.00);

INSERT INTO purchase_request_plan_position (purchase_request_id, shop_purchase_list_id, public_purchase_plan_id, allocated_amount) VALUES
(3, 3, 6, 834.15),
(4, 4, 7, 365.85),
(5, 5, 8, 900.81),
(6, 6, 9, 141.46),
(7, 7, 10, 804.88),
(8, 8, 8, 258.54);

INSERT INTO purchase_request_finalization_snapshot (
    purchase_request_id,
    shop_purchase_list_id,
    public_purchase_plan_id,
    funding_id,
    shop_name,
    funding_name,
    plan_name,
    plan_number,
    fund_responsible_person,
    plan_position_number,
    cpv_code,
    planned_net_amount,
    allocated_net_amount,
    allocated_eur_amount,
    allocated_gross_amount,
    is_main_cpv,
    created_at
) VALUES
(3, 3, 6, 9, '3DJake', 'Grant Rektora - Druk 3D', 'Filamenty i żywice do druku 3D', 'ZP/2026/09', 'Natalia Szymańska', '9.1', '19520000-7', 9000.00, 834.15, 179.88, 1026.00, true, NOW() - INTERVAL '16 days'),
(4, 4, 7, 9, '3DJake', 'Grant Rektora - Druk 3D', 'Serwis urządzeń laboratoryjnych', 'ZP/2026/09', 'Natalia Szymańska', '9.2', '50300000-8', 4500.00, 365.85, 78.90, 450.00, true, NOW() - INTERVAL '13 days'),
(5, 5, 8, 11, 'Botland', 'Partner technologiczny - Laboratorium AI', 'Czujniki wizyjne i AI dla drona', 'ZP/2026/11', 'Natalia Szymańska', '11.1', '35120000-1', 12000.00, 900.81, 194.27, 1108.00, true, NOW() - INTERVAL '9 days'),
(7, 7, 10, 10, 'Aluxprofile', 'Budżet specjalny - Rezerwa koła', 'Narzędzia warsztatowe', 'ZP/2026/10', 'Michał Kowalski', '10.2', '43800000-1', 3200.00, 804.88, 173.58, 990.00, true, NOW() - INTERVAL '6 days');

INSERT INTO settlement (created_at, paid_by_project_finance_manager_id, purchase_request_id) VALUES
(NOW() - INTERVAL '15 days', 3, 3),
(NOW() - INTERVAL '8 days', 2, 5),
(NOW() - INTERVAL '5 days', 1, 7);

UPDATE shop_purchase_list SET settlement_id = 3 WHERE shop_purchase_list_id = 3;
UPDATE shop_purchase_list SET settlement_id = 4 WHERE shop_purchase_list_id = 5;
UPDATE shop_purchase_list SET settlement_id = 5 WHERE shop_purchase_list_id = 7;

INSERT INTO invoice (number, issue_date, seller_name, seller_nip, net_total, vat_total, status, created_at, settlement_id, project_finance_manager_id) VALUES
('3DJ/2026/06/114', CURRENT_DATE - INTERVAL '15 days', '3DJake GmbH', 'DE123456789', 834.15, 191.85, 'accepted', NOW() - INTERVAL '15 days', 3, 3),
('BOT/AI/2026/044', CURRENT_DATE - INTERVAL '8 days', 'Botland B. Derkacz Sp.k.', '7770001122', 900.81, 207.19, 'pending', NOW() - INTERVAL '8 days', 4, 2),
('ALX/2026/0199', CURRENT_DATE - INTERVAL '5 days', 'Aluxprofile Sp. z o.o.', '5551112233', 804.88, 185.12, 'arrived', NOW() - INTERVAL '5 days', 5, 1),
('KOSZT/ZWROT/2026/03', CURRENT_DATE - INTERVAL '3 days', 'Allegro Lokalnie', '0000000000', 141.46, 32.54, 'returned', NOW() - INTERVAL '3 days', 5, 1),
('SERW/DRUK/2026/02', CURRENT_DATE - INTERVAL '2 days', 'Serwis 3D Warszawa', '5210000001', 365.85, 84.15, 'rejected', NOW() - INTERVAL '2 days', 3, 3);

INSERT INTO purchase_request_settlement_line (
    purchase_request_id,
    shop_purchase_list_id,
    invoice_id,
    shop_name,
    purchase_description,
    planned_gross_amount,
    actual_gross_amount,
    is_extra,
    created_at,
    updated_at
) VALUES
(1, 1, 1, 'Botland', 'Napęd i system wizyjny łazika', 2562.00, 2562.00, false, NOW() - INTERVAL '20 days', NOW() - INTERVAL '19 days'),
(2, 2, 2, 'TME Electronics', 'Mikrokontrolery do ramienia', 399.60, NULL, false, NOW() - INTERVAL '19 days', NULL),
(3, 3, 3, '3DJake', 'Materiały do druku 3D - filamenty i żywice', 1026.00, 1026.00, false, NOW() - INTERVAL '15 days', NOW() - INTERVAL '15 days'),
(5, 5, 4, 'Botland', 'Czujniki optyczne i komputer pokładowy do drona', 1108.00, 1108.00, false, NOW() - INTERVAL '8 days', NOW() - INTERVAL '8 days'),
(7, 7, 5, 'Aluxprofile', 'Profile aluminiowe i elementy warsztatowe', 990.00, 990.00, false, NOW() - INTERVAL '5 days', NOW() - INTERVAL '5 days'),
(7, NULL, 6, 'Allegro Lokalnie', 'Dodatkowy zwrot za materiały pomocnicze', 174.00, 174.00, true, NOW() - INTERVAL '3 days', NOW() - INTERVAL '3 days'),
(3, NULL, NULL, 'Kurier DHL', 'Dopłata do dostawy materiałów 3D', 49.00, NULL, true, NOW() - INTERVAL '2 days', NULL);

UPDATE purchase_request SET finalization_status = 'settlement' WHERE purchase_request_id IN (1, 2, 3, 5);
UPDATE purchase_request SET finalization_status = 'settled' WHERE purchase_request_id = 7;
UPDATE purchase_request SET finalization_status = 'accounting_pending' WHERE purchase_request_id = 4;
UPDATE purchase_request SET finalization_status = 'prepared' WHERE purchase_request_id = 6;
