-- 004_constraints.sql

-- Foreign Keys
ALTER TABLE dining_area ADD CONSTRAINT fk_dining_area_branch FOREIGN KEY (branch_id) REFERENCES branch(id) ON DELETE CASCADE;
ALTER TABLE table_entity ADD CONSTRAINT fk_table_entity_area FOREIGN KEY (area_id) REFERENCES dining_area(id) ON DELETE CASCADE;
ALTER TABLE user_account ADD CONSTRAINT fk_user_account_role FOREIGN KEY (role_id) REFERENCES role(id);
ALTER TABLE user_account ADD CONSTRAINT fk_user_account_branch FOREIGN KEY (branch_id) REFERENCES branch(id);
ALTER TABLE reservation ADD CONSTRAINT fk_reservation_table FOREIGN KEY (table_id) REFERENCES table_entity(id);
ALTER TABLE reservation ADD CONSTRAINT fk_reservation_customer FOREIGN KEY (customer_id) REFERENCES customer(id);
ALTER TABLE dining_session ADD CONSTRAINT fk_dining_session_table FOREIGN KEY (table_id) REFERENCES table_entity(id);
ALTER TABLE dining_session ADD CONSTRAINT fk_dining_session_reservation FOREIGN KEY (reservation_id) REFERENCES reservation(id);
ALTER TABLE dining_session ADD CONSTRAINT fk_dining_session_customer FOREIGN KEY (customer_id) REFERENCES customer(id);
ALTER TABLE menu_item ADD CONSTRAINT fk_menu_item_category FOREIGN KEY (category_id) REFERENCES menu_category(id);
ALTER TABLE customer_order ADD CONSTRAINT fk_customer_order_session FOREIGN KEY (session_id) REFERENCES dining_session(id);
ALTER TABLE customer_order ADD CONSTRAINT fk_customer_order_user FOREIGN KEY (user_id) REFERENCES user_account(id);
ALTER TABLE order_status_history ADD CONSTRAINT fk_order_status_history_order FOREIGN KEY (order_id) REFERENCES customer_order(id) ON DELETE CASCADE;
ALTER TABLE order_item ADD CONSTRAINT fk_order_item_order FOREIGN KEY (order_id) REFERENCES customer_order(id) ON DELETE CASCADE;
ALTER TABLE order_item ADD CONSTRAINT fk_order_item_item FOREIGN KEY (item_id) REFERENCES menu_item(id);
ALTER TABLE kitchen_ticket ADD CONSTRAINT fk_kitchen_ticket_order FOREIGN KEY (order_id) REFERENCES customer_order(id) ON DELETE CASCADE;
ALTER TABLE kitchen_ticket_item ADD CONSTRAINT fk_kitchen_ticket_item_ticket FOREIGN KEY (ticket_id) REFERENCES kitchen_ticket(id) ON DELETE CASCADE;
ALTER TABLE kitchen_ticket_item ADD CONSTRAINT fk_kitchen_ticket_item_order_item FOREIGN KEY (order_item_id) REFERENCES order_item(id) ON DELETE CASCADE;
ALTER TABLE bill ADD CONSTRAINT fk_bill_session FOREIGN KEY (session_id) REFERENCES dining_session(id);
ALTER TABLE bill_item ADD CONSTRAINT fk_bill_item_bill FOREIGN KEY (bill_id) REFERENCES bill(id) ON DELETE CASCADE;
ALTER TABLE bill_item ADD CONSTRAINT fk_bill_item_order_item FOREIGN KEY (order_item_id) REFERENCES order_item(id);
ALTER TABLE discount_application ADD CONSTRAINT fk_discount_application_bill FOREIGN KEY (bill_id) REFERENCES bill(id) ON DELETE CASCADE;
ALTER TABLE discount_application ADD CONSTRAINT fk_discount_application_discount FOREIGN KEY (discount_id) REFERENCES discount(id);
ALTER TABLE discount_application ADD CONSTRAINT fk_discount_application_user FOREIGN KEY (authorized_by_user_id) REFERENCES user_account(id);
ALTER TABLE payment ADD CONSTRAINT fk_payment_bill FOREIGN KEY (bill_id) REFERENCES bill(id) ON DELETE CASCADE;

-- Exclusion Constraints
ALTER TABLE reservation ADD CONSTRAINT excl_reservation_overlap 
    EXCLUDE USING gist (table_id WITH =, tstzrange(start_time, end_time) WITH &&) 
    WHERE (status IN ('PENDING', 'CONFIRMED'));

ALTER TABLE dining_session ADD CONSTRAINT excl_dining_session_overlap 
    EXCLUDE USING gist (table_id WITH =, tstzrange(start_time, COALESCE(end_time, 'infinity')) WITH &&) 
    WHERE (status = 'ACTIVE');
