"""
Generator script to build the complete, production-grade DBMS REPORT.docx
with Woxsen University Logo, School of Technology header, and Sakhunala Sahaja as Student Name.
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

DOCX_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "docx"))
LOGO_PATH = os.path.join(DOCX_DIR, "woxsen_logo.png")
ER_IMG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "dinedesk_chen_er_diagram.png"))
OUTPUT_DOCX = os.path.join(DOCX_DIR, "DBMS REPORT.docx")
OUTPUT_DOCX_ALT = os.path.join(DOCX_DIR, "DBMS_REPORT.docx")

def set_cell_background(cell, fill_hex):
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=120, bottom=120, left=180, right=180):
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def add_heading_1(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = 'Calibri'
    run.font.size = Pt(16)
    run.font.bold = True
    run.font.color.rgb = RGBColor(15, 23, 42) # Slate 900
    return p

def add_heading_2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = 'Calibri'
    run.font.size = Pt(13)
    run.font.bold = True
    run.font.color.rgb = RGBColor(2, 132, 199) # Sky 600
    return p

def add_body_p(doc, text, bold=False, italic=False):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.15
    run = p.add_run(text)
    run.font.name = 'Calibri'
    run.font.size = Pt(11)
    run.font.color.rgb = RGBColor(51, 65, 85)
    run.bold = bold
    run.italic = italic
    return p

def add_code_block(doc, code_text):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "0F172A") # Dark slate
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    run = p.add_run(code_text)
    run.font.name = 'Consolas'
    run.font.size = Pt(9.5)
    run.font.color.rgb = RGBColor(56, 189, 248) # Sky 400
    
    # Empty paragraph after table for spacing
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(6)

def add_styled_table(doc, headers, rows):
    tbl = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    # Header row
    hdr_cells = tbl.rows[0].cells
    for i, h in enumerate(headers):
        hdr_cells[i].text = h
        set_cell_background(hdr_cells[i], "1E293B")
        set_cell_margins(hdr_cells[i], top=120, bottom=120, left=150, right=150)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for r in p.runs:
            r.font.name = 'Calibri'
            r.font.size = Pt(10)
            r.font.bold = True
            r.font.color.rgb = RGBColor(248, 250, 252)

    # Data rows
    for r_idx, row_data in enumerate(rows):
        row_cells = tbl.rows[r_idx + 1].cells
        bg_color = "F8FAFC" if r_idx % 2 == 0 else "FFFFFF"
        for c_idx, val in enumerate(row_data):
            row_cells[c_idx].text = str(val)
            set_cell_background(row_cells[c_idx], bg_color)
            set_cell_margins(row_cells[c_idx], top=100, bottom=100, left=150, right=150)
            p = row_cells[c_idx].paragraphs[0]
            for r in p.runs:
                r.font.name = 'Calibri'
                r.font.size = Pt(9.5)
                r.font.color.rgb = RGBColor(51, 65, 85)

    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_after = Pt(6)

def build_docx():
    doc = docx.Document()

    # Set Margins (1 inch)
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # ==========================================
    # FRONT / COVER PAGE
    # ==========================================
    if os.path.exists(LOGO_PATH):
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_before = Pt(10)
        p_logo.paragraph_format.space_after = Pt(20)
        p_logo.add_run().add_picture(LOGO_PATH, width=Inches(2.5))

    p_dept = doc.add_paragraph()
    p_dept.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_dept.paragraph_format.space_after = Pt(4)
    run_dept = p_dept.add_run("SCHOOL OF TECHNOLOGY")
    run_dept.font.name = 'Calibri'
    run_dept.font.size = Pt(18)
    run_dept.font.bold = True
    run_dept.font.color.rgb = RGBColor(15, 23, 42)

    p_subdept = doc.add_paragraph()
    p_subdept.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_subdept.paragraph_format.space_after = Pt(24)
    run_sub = p_subdept.add_run("DATABASE MANAGEMENT SYSTEMS (DBMS) COURSE PROJECT REPORT")
    run_sub.font.name = 'Calibri'
    run_sub.font.size = Pt(12)
    run_sub.font.bold = True
    run_sub.font.color.rgb = RGBColor(71, 85, 105)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_after = Pt(36)
    run_t = p_title.add_run("DINEDESK: RESTAURANT RESERVATION, REAL-TIME DINING & BILLING MANAGEMENT SYSTEM")
    run_t.font.name = 'Calibri'
    run_t.font.size = Pt(20)
    run_t.font.bold = True
    run_t.font.color.rgb = RGBColor(2, 132, 199)

    # Student Details Box Table
    tbl_box = doc.add_table(rows=1, cols=1)
    tbl_box.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell_box = tbl_box.cell(0, 0)
    set_cell_background(cell_box, "F1F5F9")
    set_cell_margins(cell_box, top=180, bottom=180, left=240, right=240)

    p_box = cell_box.paragraphs[0]
    p_box.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_box.paragraph_format.line_spacing = 1.3
    
    r1 = p_box.add_run("SUBMITTED BY:\n")
    r1.font.bold = True
    r1.font.size = Pt(11)
    r1.font.color.rgb = RGBColor(15, 23, 42)

    r2 = p_box.add_run("Student Name: ")
    r2.font.size = Pt(11)
    r3 = p_box.add_run("Sakhunala Sahaja\n")
    r3.font.bold = True
    r3.font.size = Pt(12)
    r3.font.color.rgb = RGBColor(2, 132, 199)

    r4 = p_box.add_run("Roll Number: 25WU0102237\n")
    r4.font.size = Pt(11)

    r5 = p_box.add_run("Course: CS301 - Database Management Systems Laboratory\n\n")
    r5.font.size = Pt(11)

    r6 = p_box.add_run("UNDER THE GUIDANCE OF:\n")
    r6.font.bold = True
    r6.font.size = Pt(11)

    r7 = p_box.add_run("Faculty Name: Dr. Kiran Mayee\n")
    r7.font.size = Pt(11)

    r8 = p_box.add_run("Academic Year: 2025 – 2026")
    r8.font.size = Pt(11)

    p_univ = doc.add_paragraph()
    p_univ.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_univ.paragraph_format.space_before = Pt(40)
    run_u = p_univ.add_run("WOXSEN UNIVERSITY")
    run_u.font.name = 'Calibri'
    run_u.font.size = Pt(14)
    run_u.font.bold = True
    run_u.font.color.rgb = RGBColor(15, 23, 42)

    doc.add_page_break()

    # ==========================================
    # CHAPTERS & SECTIONS
    # ==========================================

    # 1. Executive Summary
    add_heading_1(doc, "1. Executive Summary")
    add_body_p(doc, "Modern culinary establishments face immense logistical bottlenecks when coordinating tableside dining experiences, including table allocation overbooking, fragmented kitchen-line communications, disjointed item-level billing, and data loss during customer draft sessions.")
    add_body_p(doc, "DineDesk is an enterprise-grade, relational database-driven Fine Dining & Lounge Management System engineered to bridge the disconnect between patrons, executive kitchen brigades, and front-of-house staff. Built on a Third Normal Form (3NF) relational architecture using SQLite and FastAPI backend microservices, DineDesk delivers end-to-end operational visibility.")

    # 2. Abstract
    add_heading_1(doc, "2. Abstract")
    add_body_p(doc, "This project presents the full lifecycle design, relational normalization, implementation, and operational validation of DineDesk. The database architecture is normalized to 3NF/BCNF, comprising 20 interconnected relational tables that manage physical dining areas, seating tables, guest reservations, floor dining sessions, digital menu catalogs, customer orders, Kitchen Display System (KDS) prep tickets, invoices, promotional discounts, and payment settlements.")

    # 3. System Architecture & Objectives
    add_heading_1(doc, "3. System Architecture and Scope")
    add_heading_2(doc, "3.1 Primary Objectives")
    add_body_p(doc, "• Design and normalize a robust relational schema up to 3NF/BCNF enforcing strict entity and referential integrity.")
    add_body_p(doc, "• Develop automated RESTful CRUD microservices for floor seating, menu cataloging, dining sessions, orders, and payment receipts.")
    add_body_p(doc, "• Enforce business rules at the database level: foreign key cascades, unique table constraints, timestamp range queries, and reservation lead-time guarantees.")
    add_body_p(doc, "• Provide an intuitive, responsive frontend with persistent state caching, dynamic filtering, locked table indicators, and kitchen progress visualization.")

    add_heading_2(doc, "3.2 Technical Stack")
    add_styled_table(doc, ["Component", "Technology", "Purpose"], [
        ["Backend Language", "Python 3.10+", "Core business logic and microservice routing"],
        ["Web Framework", "FastAPI (Uvicorn)", "Asynchronous REST API dispatch"],
        ["Database Engine", "SQLite 3 / PostgreSQL", "ACID-compliant relational persistence"],
        ["ORM Layer", "SQLAlchemy 2.0", "Declarative schema modeling and query composition"],
        ["Frontend UI", "HTML5, CSS3, ES6 JavaScript", "Responsive front-of-house and KDS interfaces"]
    ])

    # 4. Entity Relationship (ER) Diagram
    add_heading_1(doc, "4. Entity Relationship (ER) Diagram")
    add_body_p(doc, "The DineDesk database architecture models 20 core entities connected through foreign-key relationships. Below is the comprehensive Chen-Style Entity-Relationship Diagram highlighting physical dining areas, floor tables, customer reservations, active dining sessions, menu categories, customer orders, kitchen display tickets, invoices, and payment receipts:")

    if os.path.exists(ER_IMG_PATH):
        p_er = doc.add_paragraph()
        p_er.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_er.paragraph_format.space_before = Pt(10)
        p_er.paragraph_format.space_after = Pt(14)
        p_er.add_run().add_picture(ER_IMG_PATH, width=Inches(6.2))
        add_body_p(doc, "Figure 4.1: DineDesk 20-Entity Chen ER Diagram Architecture", italic=True)

    # 5. Relational Schema & Normalization
    add_heading_1(doc, "5. Relational Schema and Normalization")
    add_heading_2(doc, "5.1 Relational Schema Representation")
    schema_text = """
1. BRANCH (branch_id [PK], name, phone, address, created_at, updated_at)
2. DINING_AREA (area_id [PK], branch_id [FK->BRANCH.branch_id], name, created_at, updated_at)
3. TABLE_ENTITY (table_id [PK], area_id [FK->DINING_AREA.area_id], table_number [UQ], capacity, is_active, created_at, updated_at)
4. ROLE (role_id [PK], name [UQ], description)
5. USER_ACCOUNT (user_id [PK], role_id [FK->ROLE.role_id], branch_id [FK->BRANCH.branch_id], email [UQ], first_name, last_name, password_hash, created_at)
6. CUSTOMER (customer_id [PK], first_name, last_name, phone [UQ], email [UQ], created_at, updated_at)
7. RESERVATION (reservation_id [PK], table_id [FK->TABLE_ENTITY.table_id], customer_id [FK->CUSTOMER.customer_id], start_time, end_time, guest_count, status, special_requests, created_at, updated_at)
8. DINING_SESSION (session_id [PK], table_id [FK->TABLE_ENTITY.table_id], customer_id [FK->CUSTOMER.customer_id], reservation_id [FK->RESERVATION.reservation_id], guest_count, status, start_time, end_time, created_at, updated_at)
9. MENU_CATEGORY (category_id [PK], name [UQ], description)
10. MENU_ITEM (item_id [PK], category_id [FK->MENU_CATEGORY.category_id], name, description, current_price, is_active, image_url, created_at, updated_at)
11. CUSTOMER_ORDER (order_id [PK], session_id [FK->DINING_SESSION.session_id], user_id [FK->USER_ACCOUNT.user_id], status, created_at, updated_at)
12. ORDER_ITEM (order_item_id [PK], order_id [FK->CUSTOMER_ORDER.order_id], item_id [FK->MENU_ITEM.item_id], quantity, unit_price, special_requests, created_at, updated_at)
13. ORDER_STATUS_HISTORY (history_id [PK], order_id [FK->CUSTOMER_ORDER.order_id], status, changed_at)
14. KITCHEN_TICKET (ticket_id [PK], order_id [FK->CUSTOMER_ORDER.order_id], status, prep_start_time, ready_time, created_at, updated_at)
15. KITCHEN_TICKET_ITEM (ticket_item_id [PK], ticket_id [FK->KITCHEN_TICKET.ticket_id], order_item_id [FK->ORDER_ITEM.order_item_id], status)
16. BILL (bill_id [PK], session_id [FK->DINING_SESSION.session_id], subtotal, tax_amount, total_amount, status, created_at, updated_at)
17. BILL_ITEM (bill_item_id [PK], bill_id [FK->BILL.bill_id], order_item_id [FK->ORDER_ITEM.order_item_id], item_name_snapshot, quantity, total_price)
18. DISCOUNT (discount_id [PK], code [UQ], discount_type, percentage_off, fixed_amount_off, is_active)
19. DISCOUNT_APPLICATION (discount_app_id [PK], bill_id [FK->BILL.bill_id], discount_id [FK->DISCOUNT.discount_id], authorized_by [FK->USER_ACCOUNT.user_id], applied_amount)
20. PAYMENT (payment_id [PK], bill_id [FK->BILL.bill_id], amount, payment_method, status, transaction_ref [UQ], created_at, updated_at)
    """
    add_code_block(doc, schema_text.strip())

    add_heading_2(doc, "5.2 Normalization Proofs")
    add_body_p(doc, "• First Normal Form (1NF): All attributes across all 20 relations are strictly atomic (single-valued). Multi-valued elements such as dietary tags or special chef requests are decoupled into child tables or structured string attributes.")
    add_body_p(doc, "• Second Normal Form (2NF): The schema satisfies 1NF and exhibits no partial functional dependencies. Non-key attributes in associative entities (such as quantity and unit_price in ORDER_ITEM) depend fully on the complete primary key.")
    add_body_p(doc, "• Third Normal Form (3NF): The schema satisfies 2NF and has zero transitive dependencies. Historical prices and invoice line totals are snapshotted into immutable BILL_ITEM records to protect historical billing records against future menu price updates.")

    # 6. Data Dictionary & Table Specifications
    add_heading_1(doc, "6. Data Dictionary and Schema Specifications")
    add_heading_2(doc, "6.1 Table Specification: TABLE_ENTITY")
    add_styled_table(doc, ["Field Name", "Data Type", "Constraints", "Description"], [
        ["id", "VARCHAR(36)", "PRIMARY KEY", "Unique UUID string identifier"],
        ["area_id", "VARCHAR(36)", "FOREIGN KEY", "References dining_area(id) ON DELETE SET NULL"],
        ["table_number", "VARCHAR(10)", "NOT NULL, UNIQUE", "Physical floor table code (e.g. T01, R03, F01)"],
        ["capacity", "INTEGER", "NOT NULL, CHECK(>0)", "Maximum seating guest capacity"],
        ["is_active", "BOOLEAN", "DEFAULT 1", "Active status indicator flag"]
    ])

    add_heading_2(doc, "6.2 Table Specification: RESERVATION")
    add_styled_table(doc, ["Field Name", "Data Type", "Constraints", "Description"], [
        ["id", "VARCHAR(36)", "PRIMARY KEY", "Unique reservation booking identifier"],
        ["table_id", "VARCHAR(36)", "FOREIGN KEY", "References table_entity(id) ON DELETE CASCADE"],
        ["customer_id", "VARCHAR(36)", "FOREIGN KEY", "References customer(id) ON DELETE CASCADE"],
        ["start_time", "DATETIME", "NOT NULL", "Booking window commencement timestamp"],
        ["end_time", "DATETIME", "NOT NULL", "Booking window conclusion timestamp"],
        ["guest_count", "INTEGER", "NOT NULL, CHECK(>0)", "Number of booked dining guests"],
        ["status", "VARCHAR(20)", "DEFAULT 'CONFIRMED'", "Booking status (PENDING, CONFIRMED, CANCELLED)"]
    ])

    add_heading_2(doc, "6.3 Table Specification: KITCHEN_TICKET & KITCHEN_TICKET_ITEM")
    add_styled_table(doc, ["Field Name", "Data Type", "Constraints", "Description"], [
        ["id", "VARCHAR(36)", "PRIMARY KEY", "Unique kitchen ticket identifier"],
        ["order_id", "VARCHAR(36)", "FOREIGN KEY", "References customer_order(id) ON DELETE CASCADE"],
        ["status", "VARCHAR(20)", "DEFAULT 'PENDING'", "Ticket status (PENDING, IN_PROGRESS, READY)"],
        ["prep_start_time", "DATETIME", "NULLABLE", "Timestamp chef commenced cooking"],
        ["ready_time", "DATETIME", "NULLABLE", "Timestamp all dishes completed prep"]
    ])

    # 7. SQL Data Definition & Seeding (DDL & DML)
    add_heading_1(doc, "7. SQL Implementation (DDL and DML)")
    add_heading_2(doc, "7.1 Data Definition Language (DDL)")
    ddl_sample = """
CREATE TABLE dining_area (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN DEFAULT 1
);

CREATE TABLE table_entity (
    id VARCHAR(36) PRIMARY KEY,
    area_id VARCHAR(36) REFERENCES dining_area(id) ON DELETE SET NULL,
    table_number VARCHAR(10) NOT NULL UNIQUE,
    capacity INTEGER NOT NULL CHECK (capacity > 0),
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE reservation (
    id VARCHAR(36) PRIMARY KEY,
    table_id VARCHAR(36) NOT NULL REFERENCES table_entity(id) ON DELETE CASCADE,
    customer_id VARCHAR(36) NOT NULL REFERENCES customer(id) ON DELETE CASCADE,
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    guest_count INTEGER NOT NULL CHECK (guest_count > 0),
    status VARCHAR(20) DEFAULT 'CONFIRMED',
    special_notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
    """
    add_code_block(doc, ddl_sample.strip())

    add_heading_2(doc, "7.2 Data Manipulation Language (DML)")
    dml_sample = """
INSERT INTO dining_area (id, name, description) VALUES
('AREA-01', 'Romantic Terrace (Rooftop)', 'Sunset ambiance with panoramic city skyline views'),
('AREA-02', 'Main Dining Hall', 'Opulent crystal chandeliers and live classical lounge acoustics'),
('AREA-03', 'Family & Kids Lounge', 'Spacious plush seating with interactive dessert stations'),
('AREA-04', 'Chef''s Private Dining', 'Exclusive private suite featuring sommelier pairings');

INSERT INTO table_entity (id, area_id, table_number, capacity) VALUES
('TBL-R01', 'AREA-01', 'R01', 2),
('TBL-R02', 'AREA-01', 'R02', 2),
('TBL-R03', 'AREA-01', 'R03', 4),
('TBL-T01', 'AREA-02', 'T01', 4),
('TBL-T02', 'AREA-02', 'T02', 4),
('TBL-F01', 'AREA-03', 'F01', 6),
('TBL-P01', 'AREA-04', 'P01', 8);
    """
    add_code_block(doc, dml_sample.strip())

    # 8. Analytical Queries and Output Results
    add_heading_1(doc, "8. Database Queries and Verification Results")
    add_heading_2(doc, "8.1 Real-Time Kitchen Display Ticket Inspection")
    add_body_p(doc, "Query execution output demonstrating live ticket items, quantities, ticket prep statuses, and chef special requests:")
    
    add_styled_table(doc, ["Ticket Ref", "Table", "Ticket Status", "Item Name", "Qty", "Item Status", "Chef Notes"], [
        ["6eb2cf3a", "T01", "PENDING", "Baked New York Raspberry Cheesecake", "1", "PENDING", "None"],
        ["6eb2cf3a", "T01", "PENDING", "Cold Brew Iced Vanilla Latte", "1", "PENDING", "None"],
        ["593a572f", "F01", "PENDING", "Crispy Corn & Jalapeno Croquettes", "1", "PENDING", "None"],
        ["593a572f", "F01", "PENDING", "Dal Makhani Bukhara", "1", "PENDING", "None"],
        ["6349d9db", "R03", "IN_PROGRESS", "Chicken Alfredo Fettuccine", "1", "PREPARING", "None"],
        ["6349d9db", "R03", "IN_PROGRESS", "Classic Margherita Pizza", "1", "PREPARING", "None"],
        ["dd12373f", "F01", "IN_PROGRESS", "Classic Margherita Pizza", "1", "PREPARING", "Extra mild sauce & small triangles for kid"],
        ["dd12373f", "F01", "IN_PROGRESS", "Butter Garlic Naan", "3", "PREPARING", "Well done, crispy edges"],
        ["7985c3ce", "T03", "READY", "Dum Murgh Awadhi Biryani", "2", "COMPLETED", "Authentic Dum prep with raita"],
        ["7985c3ce", "T03", "READY", "Sizzling Chocolate Walnut Brownie", "2", "COMPLETED", "Extra vanilla scoop"]
    ])

    # 9. Conclusion
    add_heading_1(doc, "9. Conclusion")
    add_body_p(doc, "The DineDesk restaurant platform successfully demonstrates a robust 3NF relational database architecture designed for high-concurrency fine dining operations. By linking front-of-house table seating with live Kitchen Display System (KDS) streams and automated invoice settlements, DineDesk eliminates communication bottlenecks and guarantees complete transactional integrity.")

    # Save to file
    doc.save(OUTPUT_DOCX)
    doc.save(OUTPUT_DOCX_ALT)
    print(f"Successfully generated {OUTPUT_DOCX} and {OUTPUT_DOCX_ALT}")

if __name__ == "__main__":
    build_docx()
