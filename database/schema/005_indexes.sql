-- 005_indexes.sql
CREATE INDEX idx_reservation_table_start ON reservation(table_id, start_time);
CREATE INDEX idx_reservation_customer ON reservation(customer_id);
CREATE INDEX idx_reservation_status ON reservation(status);

CREATE INDEX idx_session_table_status ON dining_session(table_id, status);
CREATE INDEX idx_session_reservation ON dining_session(reservation_id);

CREATE INDEX idx_customer_order_session ON customer_order(session_id);
CREATE INDEX idx_customer_order_user_created ON customer_order(user_id, created_at);

CREATE INDEX idx_order_item_order ON order_item(order_id);
CREATE INDEX idx_order_item_item ON order_item(item_id);

CREATE INDEX idx_kitchen_ticket_item_order_item ON kitchen_ticket_item(order_item_id);

CREATE INDEX idx_bill_status ON bill(status);

CREATE INDEX idx_payment_bill ON payment(bill_id);

CREATE INDEX idx_user_account_branch ON user_account(branch_id);

CREATE INDEX idx_dining_area_branch ON dining_area(branch_id);
CREATE INDEX idx_table_entity_area ON table_entity(area_id);
CREATE INDEX idx_menu_item_category ON menu_item(category_id);
CREATE INDEX idx_discount_application_bill ON discount_application(bill_id);
CREATE INDEX idx_discount_application_discount ON discount_application(discount_id);
