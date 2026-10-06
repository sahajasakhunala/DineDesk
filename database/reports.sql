-- ============================================================================
-- DineDesk Restaurant Table Reservation & Food Service Management System
-- Database Analytical Reporting & Operational Views
-- ============================================================================

-- ============================================================================
-- SECTION 1: DATABASE VIEWS
-- ============================================================================

-- View 1: Available Tables View
-- Lists all currently active tables that do not have an active dining session
CREATE OR REPLACE VIEW view_available_tables AS
SELECT 
    t.id AS table_id,
    t.table_number,
    t.capacity,
    da.name AS area_name,
    b.name AS branch_name
FROM table_entity t
JOIN dining_area da ON t.area_id = da.id
JOIN branch b ON da.branch_id = b.id
WHERE t.is_active = TRUE
  AND t.id NOT IN (
      SELECT ds.table_id 
      FROM dining_session ds 
      WHERE ds.status = 'ACTIVE'
  )
ORDER BY t.table_number ASC;

-- View 2: Daily Revenue View
-- Aggregates daily financial collections across all completed payment transactions
CREATE OR REPLACE VIEW view_daily_revenue AS
SELECT 
    DATE_TRUNC('day', p.created_at) AS transaction_date,
    COUNT(p.id) AS total_transactions,
    COUNT(DISTINCT p.bill_id) AS total_bills_settled,
    SUM(p.amount) AS gross_revenue_collected,
    AVG(p.amount) AS avg_transaction_value
FROM payment p
WHERE p.status = 'COMPLETED'
GROUP BY DATE_TRUNC('day', p.created_at)
ORDER BY transaction_date DESC;

-- View 3: Item Sales & Popularity View
-- Calculates sales volume and gross revenue for all catalog dishes
CREATE OR REPLACE VIEW view_item_sales AS
SELECT 
    mi.id AS item_id,
    mi.name AS item_name,
    mc.name AS category_name,
    mi.current_price,
    COALESCE(SUM(oi.quantity), 0) AS units_sold,
    COALESCE(SUM(oi.quantity * oi.unit_price), 0.00) AS total_sales_volume
FROM menu_item mi
JOIN menu_category mc ON mi.category_id = mc.id
LEFT JOIN order_item oi ON mi.id = oi.item_id
LEFT JOIN customer_order co ON oi.order_id = co.id AND co.status != 'CANCELLED'
GROUP BY mi.id, mi.name, mc.name, mi.current_price
ORDER BY total_sales_volume DESC;

-- View 4: Waiter / Staff Order Performance View
-- Evaluates orders taken and sales driven by restaurant service staff
CREATE OR REPLACE VIEW view_waiter_performance AS
SELECT 
    u.id AS user_id,
    u.first_name || ' ' || u.last_name AS staff_name,
    r.name AS role_name,
    COUNT(DISTINCT co.id) AS orders_handled,
    COALESCE(SUM(oi.quantity * oi.unit_price), 0.00) AS total_revenue_generated
FROM user_account u
JOIN role r ON u.role_id = r.id
LEFT JOIN customer_order co ON u.id = co.user_id AND co.status != 'CANCELLED'
LEFT JOIN order_item oi ON co.id = oi.order_id
GROUP BY u.id, u.first_name, u.last_name, r.name
ORDER BY total_revenue_generated DESC;

-- View 5: Kitchen Ticket Delays & Performance View
-- Tracks elapsed preparation durations and highlights delayed orders (>20 mins)
CREATE OR REPLACE VIEW view_kitchen_delays AS
SELECT 
    kt.id AS ticket_id,
    co.id AS order_id,
    t.table_number,
    kt.status AS ticket_status,
    kt.created_at AS ticket_created_at,
    kt.prep_start_time,
    kt.ready_time,
    CASE 
        WHEN kt.ready_time IS NOT NULL AND kt.prep_start_time IS NOT NULL 
        THEN ROUND(EXTRACT(EPOCH FROM (kt.ready_time - kt.prep_start_time)) / 60, 2)
        WHEN kt.prep_start_time IS NOT NULL 
        THEN ROUND(EXTRACT(EPOCH FROM (NOW() - kt.prep_start_time)) / 60, 2)
        ELSE 0 
    END AS elapsed_prep_minutes
FROM kitchen_ticket kt
JOIN customer_order co ON kt.order_id = co.id
JOIN dining_session ds ON co.session_id = ds.id
JOIN table_entity t ON ds.table_id = t.id
ORDER BY kt.created_at DESC;

-- View 6: Discount Usage & Reductions View
-- Details discount rules applied and authorized amounts waived
CREATE OR REPLACE VIEW view_discount_usage AS
SELECT 
    d.id AS discount_id,
    d.name AS discount_name,
    d.discount_type,
    d.value AS rule_value,
    COUNT(da.id) AS applications_count,
    COALESCE(SUM(da.discount_amount), 0.00) AS total_fixed_waived,
    COALESCE(AVG(da.discount_percentage), 0.00) AS avg_percentage_applied
FROM discount d
LEFT JOIN discount_application da ON d.id = da.discount_id
GROUP BY d.id, d.name, d.discount_type, d.value
ORDER BY applications_count DESC;


-- ============================================================================
-- SECTION 2: COMPLEX ANALYTICAL SQL QUERIES
-- ============================================================================

-- Query 1: Table Turnover Rate and Average Session Duration (GROUP BY, HAVING, AVG)
-- Identifies high-demand tables with average dining time exceeding 15 minutes
SELECT 
    t.table_number,
    da.name AS dining_area,
    t.capacity,
    COUNT(ds.id) AS total_seated_sessions,
    ROUND(AVG(EXTRACT(EPOCH FROM (ds.end_time - ds.start_time)) / 60)::numeric, 1) AS avg_duration_minutes,
    MIN(ds.guest_count) AS min_party_size,
    MAX(ds.guest_count) AS max_party_size
FROM table_entity t
JOIN dining_area da ON t.area_id = da.id
JOIN dining_session ds ON t.id = ds.table_id
WHERE ds.status = 'COMPLETED'
GROUP BY t.table_number, da.name, t.capacity
HAVING COUNT(ds.id) >= 1
ORDER BY total_seated_sessions DESC, avg_duration_minutes DESC;

-- Query 2: High-Value Customers Analysis (Nested Subquery & Aggregation)
-- Customers whose cumulative dining spend is above the overall average customer spend
SELECT 
    c.id AS customer_id,
    c.first_name || ' ' || c.last_name AS customer_name,
    c.phone,
    c.email,
    COUNT(DISTINCT ds.id) AS total_visits,
    SUM(b.total_amount) AS cumulative_spend
FROM customer c
JOIN dining_session ds ON c.id = ds.customer_id
JOIN bill b ON ds.id = b.session_id
WHERE b.status = 'PAID'
GROUP BY c.id, c.first_name, c.last_name, c.phone, c.email
HAVING SUM(b.total_amount) > (
    -- Subquery: Average spend across all customers
    SELECT AVG(cust_total) FROM (
        SELECT SUM(sub_b.total_amount) AS cust_total
        FROM dining_session sub_ds
        JOIN bill sub_b ON sub_ds.id = sub_b.session_id
        WHERE sub_b.status = 'PAID'
        GROUP BY sub_ds.customer_id
    ) AS avg_spend_table
)
ORDER BY cumulative_spend DESC;

-- Query 3: Hourly Peak Ordering Demand Heatmap (DATE_PART, COUNT, SUM)
-- Analyzes peak hours for kitchen staff capacity planning
SELECT 
    DATE_PART('hour', co.created_at) AS order_hour,
    COUNT(co.id) AS orders_placed,
    SUM(oi.quantity) AS total_dishes_ordered,
    ROUND(SUM(oi.quantity * oi.unit_price)::numeric, 2) AS total_hourly_order_value
FROM customer_order co
JOIN order_item oi ON co.id = oi.order_id
WHERE co.status != 'CANCELLED'
GROUP BY DATE_PART('hour', co.created_at)
ORDER BY orders_placed DESC;

-- Query 4: Payment Method Reconciliation Report (JOIN, SUM, CASE)
-- Audits payment settlement distribution across payment gateways
SELECT 
    p.payment_method,
    COUNT(p.id) AS transaction_count,
    SUM(p.amount) AS total_collected,
    ROUND((SUM(p.amount) / (SELECT SUM(amount) FROM payment WHERE status = 'COMPLETED') * 100)::numeric, 2) AS percentage_of_revenue
FROM payment p
WHERE p.status = 'COMPLETED'
GROUP BY p.payment_method
ORDER BY total_collected DESC;

-- Query 5: Unpaid or Partially Paid Bills Audit
-- Identifies outstanding dining balances requiring cashier reconciliation
SELECT 
    b.id AS bill_id,
    t.table_number,
    c.first_name || ' ' || c.last_name AS customer_name,
    b.subtotal,
    b.tax_amount,
    b.total_amount,
    COALESCE(SUM(p.amount), 0) AS amount_paid,
    (b.total_amount - COALESCE(SUM(p.amount), 0)) AS outstanding_balance,
    b.status AS bill_status
FROM bill b
JOIN dining_session ds ON b.session_id = ds.id
JOIN table_entity t ON ds.table_id = t.id
LEFT JOIN customer c ON ds.customer_id = c.id
LEFT JOIN payment p ON b.id = p.bill_id AND p.status = 'COMPLETED'
WHERE b.status IN ('UNPAID', 'PARTIAL')
GROUP BY b.id, t.table_number, c.first_name, c.last_name, b.subtotal, b.tax_amount, b.total_amount, b.status
ORDER BY outstanding_balance DESC;
