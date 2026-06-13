-- Mockup data for BudgetFlowFusion application
INSERT INTO association (association_name) VALUES
('Koło Naukowe Robotyków'),
('Koło Naukowe Obróbki Skrawaniem');


INSERT INTO project (project_name, description, allocated_budget, rest_of_budget, association_id) VALUES
('Łazik Marsjański HAL_062', 'Projekt zaawansowanego łazika badawczego.', 25000.00, 25000.00, 1),
('Ramię Robotyczne KUKA-Mini', 'Edukacyjne ramię 6-DOF do laboratorium.', 8000.00, 8000.00, 1),
('Dron Autonomiczny X-1', 'Projekt quadrocoptera do mapowania terenu.', 15000.00, 15000.00, 2);


INSERT INTO public_purchase_plan_list (public_plan_list_name) VALUES
('Plan Zamówień Publicznych Koła 2026'),
('Rezerwowy Plan Zakupowy 2026');


INSERT INTO association_budget (association_budget_name, total_budget, spent_money, public_purchase_plan_list_id) VALUES
('Budżet Główny Koła 2026', 500000.00, 0.00, 1),
('Fundusz Rozwojowy Wydziału', 100000.00, 0.00, 2);


INSERT INTO project_budget (project_budget_name, total_budget, spent_money, association_budget_id, project_id) VALUES
('Budżet projektu: Łazik Marsjański HAL_062', 25000.00, 0.00, 1, 1),
('Budżet projektu: Ramię Robotyczne KUKA-Mini', 8000.00, 0.00, 1, 2),
('Budżet projektu: Dron Autonomiczny X-1', 15000.00, 0.00, 2, 3);


INSERT INTO project_finance_manager (login, password_hash, access) VALUES
('skarbnik_glowny@kolo.edu.pl', 'hashed_123', true),
('zastepca_skarbnika@kolo.edu.pl', 'hashed_789', true);


INSERT INTO student (name, surname, login, password_hash, position, is_in_sap, project_finance_manager_id, association_id) VALUES
('Michał', 'Kowalski',   'michal.kowalski@kolo.edu.pl', 'hashed_123', 'Elektronika', true, 1, 1),
('Anna',   'Nowak',      'anna.nowak@kolo.edu.pl',      'hashed_456', 'Mechanika', false, NULL, 1),
('Piotr',  'Zieliński',  'piotr.zielinski@kolo.edu.pl', 'hashed_111', 'Autonomia', true, NULL, 2),
('Kasia',  'Wiśniewska', 'kasia.w@kolo.edu.pl',         'hashed_222', 'Mechanika', false, 2, 2);


INSERT INTO funding (funding_name, funding_price, spent_money, project_id, association_budget_id) VALUES
('Grant Rektora - HAL_062', 20000.00, 0.00, 1, 1),
('Sponsor Główny - Dron', 10000.00, 0.00, 2, 1),
('Środki Własne Instytutu', 5000.00, 0.00, 3, 2);


INSERT INTO shop (shop_name, address, delivery_time, is_recommended, free_delivery_threshold) VALUES
('Botland', 'Online', NOW() + INTERVAL '2 days', true, 200.00),
('TME', 'Łódź, Ustronna 41', NOW() + INTERVAL '1 day', true, 500.00),
('Kamami', 'Online', NOW() + INTERVAL '3 days', false, 300.00),
('Allegro', 'Online', NOW() + INTERVAL '2 days', false, 45.00);


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


INSERT INTO public_purchase_plan (public_purchase_plan_name, cost, funding_id, gslbccf_id, public_purchase_plan_list_id) VALUES
('Zakup podzespołów napędowych do łazika HAL_062', 5000.00, 1, 1, 1),
('Komponenty do systemu wizyjnego Drona X-1', 3000.00, 2, 2, 1);


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
('Zestaw przewodów żeńsko-męskich',  15.50,  'PLN', 'https://botland.com.pl', NOW(), 'pending',  2, 2, 1);


INSERT INTO shop_purchase_list (priority, cost, created_at, gslbccf_id, settlement_id, funding_id, shop_id, student_id) VALUES
(1, 2562.00, NOW(), 1, NULL, 1, 1, 2),
(2,  399.60, NOW(), 2, NULL, 2, 2, 1);


INSERT INTO shop_purchase_list_item (shop_purchase_list_id, item_id, amount) VALUES
(1, 1, 4),
(1, 2, 1),
(1, 3, 2),
(2, 4, 4);


INSERT INTO purchase_request (purchase_request_name, budget_allocated_for_the_order, if_service, used_cpv_id, created_at, can_add, project_budget_id, gslbccf_id, project_finance_manager_id) VALUES
('Wniosek: Napęd i wizja łazika',      2562.00, false, 42000000, NOW(), false, 1, 1, 1),
('Wniosek: Mikrokontrolery do ramienia', 399.60, false, 31700000, NOW(), false, 2, 2, 2);


INSERT INTO settlement (created_at, paid_by_project_finance_manager_id, purchase_request_id) VALUES
(NOW(), 1, 1),
(NOW(), 2, 2);


UPDATE shop_purchase_list SET settlement_id = 1 WHERE shop_purchase_list_id = 1;
UPDATE shop_purchase_list SET settlement_id = 2 WHERE shop_purchase_list_id = 2;


INSERT INTO invoice (number, issue_date, seller_name, seller_nip, net_total, vat_total, status, created_at, settlement_id) VALUES
('F/2026/05/HAL-001', CURRENT_DATE, 'Botland', '1234567890', 2082.93, 479.07, 'paid', NOW(), 1),
('F/2026/05/TME-002', CURRENT_DATE, 'TME', '0987654321',  324.88,  74.72, 'pending', NOW(), 2);


UPDATE product_category SET shop_purchase_list_id = 1, public_purchase_plan_id = 1 WHERE product_category_id = 1;
