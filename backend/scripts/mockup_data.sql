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


INSERT INTO shop (shop_id, shop_name, address, delivery_time, is_recommended, free_delivery_threshold) VALUES
(1, 'Botland', 'Online / Kępno', NOW() + INTERVAL '2 days', true, 200.00),
(2, 'TME Electronics', 'Łódź, Ustronna 41', NOW() + INTERVAL '1 day', true, 500.00),
(3, 'Kamami', 'Online', NOW() + INTERVAL '3 days', true, 300.00),
(4, 'Allegro (Smart)', 'Online', NOW() + INTERVAL '2 days', false, 45.00),
(5, 'Mouser Electronics', 'Monachium / USA (Import)', NOW() + INTERVAL '5 days', true, 250.00),
(6, '3DJake', 'Niemcy', NOW() + INTERVAL '4 days', true, 220.00),
(7, 'Kastal', 'Warszawa', NOW() + INTERVAL '12 days', false, 0.00),
(8, 'Aluxprofile', 'Poznań', NOW() + INTERVAL '3 days', true, 600.00),
(9, 'EBMiA', 'Online', NOW() + INTERVAL '15 days', false, 400.00);

INSERT INTO grouped_shops_list_by_cpv_category_and_funding (allocated_money) VALUES
(20000.00),
(10000.00),
(5000.00);


INSERT INTO product_category (product_category_name, description, cpv, shop_purchase_list_id, public_purchase_plan_id) VALUES
('Mechanika i Napędy',          'Silniki, łożyska',    '42000000-6', NULL, NULL),
('Elektronika i Zasilanie',     'Czujniki, kable',     '31700000-3', NULL, NULL),
('Materiały Konstrukcyjne',     'Filamenty, rurki',    '44000000-0', NULL, NULL),
('Narzędzia warsztatowe',       'Klucze, lutownice',   '43800000-1', NULL, NULL),
('Oprogramowanie',              'Licencje, soft',      '48000000-8', NULL, NULL);


INSERT INTO product_subcategory (product_subcategory_name, description, product_category_id) VALUES
('Silniki DC/BLDC',    'Silniki prądu stałego', 1),
('Systemy Wizyjne',    'Kamery i optyka', 2),
('Druk 3D i Pianki',   'Filamenty i żywice', 3),
('Mikrokontrolery',    'Płytki stykowe, STM32', 2),
('Narzędzia ręczne',   'Śrubokręty, szczypce', 4);


INSERT INTO public_purchase_plan (public_purchase_plan_name, cpv_code, cost, funding_id, gslbccf_id, public_purchase_plan_list_id) VALUES
('CPV 42000000', 42000000, 5000.00, 1, 1, 1),
('CPV 31700000', 31700000, 3000.00, 2, 2, 2);


INSERT INTO item (name, price, currency, link, created_at, status, product_subcategory_id, student_id, shop_id) VALUES
('Silnik DC z przekładnią 12V',     145.50,  'PLN', 'https://botland.com.pl', NOW(), 'approved', 1, 2, 1),
('Kamera Intel RealSense D435i',   1850.00,  'PLN', 'https://botland.com.pl', NOW(), 'approved', 2, 2, 1),
('Filament PETG 1kg Czarny',         65.00,  'PLN', 'https://botland.com.pl', NOW(), 'approved', 3, 2, 1),
('Płytka STM32 Nucleo-F446RE',       99.90,  'PLN', 'https://tme.eu',         NOW(), 'approved', 4, 1, 2),
('Zestaw śrubokrętów precyzyjnych', 120.00,  'PLN', 'https://allegro.pl',     NOW(), 'pending',  5, 4, 4),
('Sterownik Silnika BLDC 30A',       85.00,  'PLN', 'https://kamami.pl',      NOW(), 'pending',  1, 3, 3),
('Przekładnia redukcyjna 12V',       45.00,  'PLN', 'https://botland.com.pl', NOW(), 'pending',  2, 2, 1),
('Kamera głębi ZED2i',               45.00,  'PLN', 'https://botland.com.pl', NOW(), 'pending',  2, 2, 1),
('Czujnik odległości VL53L0X',       45.00,  'PLN', 'https://botland.com.pl', NOW(), 'pending',  2, 2, 1),
('Zestaw przewodów żeńsko-męskich',  15.50,  'PLN', 'https://botland.com.pl', NOW(), 'pending',  2, 2, 1),
('Układ FPGA Xilinx Artix-7',        85.00,  'USD', 'https://mouser.com/xilinx', NOW(), 'approved', 4, 5, 5),
('Sensor IMU 9-osiowy Heuristic high-prec', 45.50, 'EUR', 'https://mouser.com/sensors', NOW(), 'pending', 4, 1, 5),
('Skaner laserowy LiDAR Hokuyo URG', 1200.00, 'USD', 'https://digikey.com/lidar', NOW(), 'pending', 2, 3, 6),
('Mikrokontroler ESP32-WROOM-32E 10 szt', 35.00, 'EUR', 'https://digikey.com/esp32', NOW(), 'approved', 4, 6, 6),
('Oscyloskop cyfrowy Siglent SDS1104X-E', 2450.00, 'PLN', 'https://tme.eu/aparatura', NOW(), 'approved', 4, 1, 2),
('Przewód silikonowy 14AWG Czarny 10m', 65.00, 'PLN', 'https://tme.eu/kable', NOW(), 'approved', 3, 5, 2),
('Złącza XT60 wysokoamperowe 5 par', 24.00, 'PLN', 'https://tme.eu/zlacza', NOW(), 'pending', 2, 5, 2);

INSERT INTO shop_purchase_list (priority, cost, created_at, gslbccf_id, settlement_id, funding_id, shop_id, student_id) VALUES
(1, 2562.00, NOW(), 1, NULL, 1, 1, 2),
(2,  399.60, NOW(), 2, NULL, 2, 2, 1);


INSERT INTO shop_purchase_list_item (shop_purchase_list_id, item_id, amount) VALUES
(1, 1, 4),
(1, 2, 1),
(1, 3, 2),
(2, 4, 4);


INSERT INTO purchase_request (purchase_request_name, budget_allocated_for_the_order, if_service, used_cpv_id, created_at, can_add, project_budget_id, funding_id, public_purchase_plan_id, plan_compliance_status, gslbccf_id, project_finance_manager_id) VALUES
('Wniosek: Napęd i wizja łazika',      2562.00, false, 42000000, NOW(), false, 1, 1, 1, 'compliant', 1, 1),
('Wniosek: Mikrokontrolery do ramienia', 399.60, false, 31700000, NOW(), false, 2, 2, 2, 'compliant', 2, 2);


INSERT INTO settlement (created_at, paid_by_project_finance_manager_id, purchase_request_id) VALUES
(NOW(), 1, 1),
(NOW(), 2, 2);


UPDATE shop_purchase_list SET settlement_id = 1 WHERE shop_purchase_list_id = 1;
UPDATE shop_purchase_list SET settlement_id = 2 WHERE shop_purchase_list_id = 2;


INSERT INTO invoice (number, issue_date, seller_name, seller_nip, net_total, vat_total, status, created_at, settlement_id) VALUES
('F/2026/05/HAL-001', CURRENT_DATE, 'Botland', '1234567890', 2082.93, 479.07, 'paid', NOW(), 1),
('F/2026/05/TME-002', CURRENT_DATE, 'TME', '0987654321',  324.88,  74.72, 'pending', NOW(), 2);


UPDATE product_category SET shop_purchase_list_id = 1, public_purchase_plan_id = 1 WHERE product_category_id = 1;
