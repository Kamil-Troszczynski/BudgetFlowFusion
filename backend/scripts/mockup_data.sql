-- Mockup data for BudgetFlowFusion application
INSERT INTO project (project_name, description, allocated_budget, rest_of_budget) VALUES
('Łazik Marsjański HAL_062', 'Projekt zaawansowanego łazika badawczego.', 25000.00, 25000.00),
('Platforma VTOL Tail-sitter', 'Bezzałogowiec o pionowym starcie.', 8000.00, 8000.00);

INSERT INTO public_purchase_plan_list (public_plan_list_name) VALUES
('Plan Zamówień Publicznych Koła 2026');

INSERT INTO association_budget (association_budget_name, total_budget, spent_money, public_purchase_plan_list_id) VALUES
('Budżet Główny Koła 2026', 500000.00, 0.00, 1);

INSERT INTO project_finance_manager (login, password_hash, access, purchase_request_id) VALUES
('skarbnik_glowny@kolo.edu.pl', 'hashed_123', true, NULL);

INSERT INTO student (name, surname, login, password_hash, position, is_in_sap, project_finance_manager_id) VALUES
('Michał', 'Kowalski', 'michal.kowalski@kolo.edu.pl', 'hashed_123', 'Elektronik', true, 1),
('Anna',   'Nowak',    'anna.nowak@kolo.edu.pl',    'hashed_456', 'Mechanik', false, NULL);

INSERT INTO funding (funding_name, funding_price, spent_money, project_id, association_budget_id) VALUES
('Grant Rektora - HAL_062', 20000.00, 0.00, 1, 1);

INSERT INTO shop (shop_name, address, delivery_time, is_recommended, free_delivery_threshold) VALUES
('Botland', 'Online', NOW() + INTERVAL '2 days', true, 200.00);

INSERT INTO grouped_shops_list_by_cpv_category_and_funding (allocated_money) VALUES
(20000.00);

INSERT INTO product_category (product_category_name, description, cpv_id, shop_purchase_list_id, public_purchase_plan_id) VALUES
('Mechanika i Napędy',          'Silniki',    42000000, NULL, NULL),
('Elektronika i Zasilanie',     'Czujniki',   31700000, NULL, NULL),
('Materiały Konstrukcyjne',     'Filamenty',  44000000, NULL, NULL);

INSERT INTO product_subcategory (product_subcategory_name, description, product_category_id) VALUES
('Silniki DC/BLDC',    '', 1),
('Systemy Wizyjne',    '', 2),
('Druk 3D i Pianki',   '', 3);

INSERT INTO public_purchase_plan (public_purchase_plan_name, cost, funding_id, gslbccf_id, public_purchase_plan_list_id) VALUES
('Zakup podzespołów napędowych do łazika HAL_062', 5000.00, 1, 1, 1);

INSERT INTO item (name, price, currency, link, created_at, product_subcategory_id, student_id, shop_id) VALUES
('Silnik DC z przekładnią 12V',     145.50,  'PLN', 'https://botland.com.pl', NOW(), 1, 2, 1),
('Kamera Intel RealSense D435i',   1850.00,  'PLN', 'https://botland.com.pl', NOW(), 2, 2, 1),
('Filament PETG 1kg Czarny',         65.00,  'PLN', 'https://botland.com.pl', NOW(), 3, 2, 1);

INSERT INTO shop_purchase_list (priority, cost, created_at, gslbccf_id, settlement_id, funding_id, shop_id, student_id) VALUES
(1, 2562.00, NOW(), 1, NULL, 1, 1, 2);

INSERT INTO shop_purchase_list_item (shop_purchase_list_id, item_id, amount) VALUES
(1, 1, 4),
(1, 2, 1),
(1, 3, 2);

INSERT INTO purchase_request (purchase_request_name, budget_allocated_for_the_order, if_service, used_cpv_id, created_at, can_add, association_budget_id, gslbccf_id) VALUES
('Wniosek: Napęd i wizja łazika', 2562.00, false, 42000000, NOW(), false, 1, 1);

INSERT INTO settlement (created_at, paid_by_project_finance_manager_id, purchase_request_id) VALUES
(NOW(), 1, 1);

UPDATE shop_purchase_list SET settlement_id = 1 WHERE shop_purchase_list_id = 1;

UPDATE project_finance_manager SET purchase_request_id = 1 WHERE project_finance_manager_id = 1;

INSERT INTO invoice (number, issue_date, seller_name, seller_nip, net_total, vat_total, status, created_at, settlement_id) VALUES
('F/2026/05/HAL-001', CURRENT_DATE, 'Botland', '1234567890', 2082.93, 479.07, 'paid', NOW(), 1);

UPDATE product_category SET shop_purchase_list_id = 1, public_purchase_plan_id = 1 WHERE product_category_id = 1;