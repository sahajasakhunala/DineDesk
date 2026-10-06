-- ============================================================================
-- DineDesk Comprehensive Database Seed Script
-- Categories:
--   1. Appetizers
--   2. Soups & Salads
--   3. Main Course
--   4. Indian Specialties
--   5. Italian/Continental
--   6. Desserts
--   7. Beverages
--   8. Chef’s Specials
-- Includes:
--   - Staff accounts & roles
--   - Dining areas & multi-capacity tables (couples, families with kids)
--   - Customers & Families (including children, dietary restrictions, allergies)
--   - Active dining sessions with Orders & "Note to Chef" slots
--   - Kitchen tickets with statuses
--   - Completed dining sessions with itemized Bills, Discounts, and Payments
-- ============================================================================

BEGIN;

-- 1. Branch
INSERT INTO branch (id, name, address, phone)
VALUES (
    'a0000000-0000-0000-0000-000000000001',
    'DineDesk Hyderabad',
    'Road No. 36, Jubilee Hills, Hyderabad, Telangana 500033',
    '+91 91545 07776'
) ON CONFLICT (id) DO NOTHING;

-- 2. Dining Areas
INSERT INTO dining_area (id, branch_id, name) VALUES
('a1000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000001', 'Main Dining Hall'),
('a1000000-0000-0000-0000-000000000002', 'a0000000-0000-0000-0000-000000000001', 'Family & Kids Lounge'),
('a1000000-0000-0000-0000-000000000003', 'a0000000-0000-0000-0000-000000000001', 'Rooftop Garden'),
('a1000000-0000-0000-0000-000000000004', 'a0000000-0000-0000-0000-000000000001', 'Chef''s Private Dining')
ON CONFLICT (id) DO NOTHING;

-- 3. Tables (Including Family Tables with High Chairs & Large Group Booths)
INSERT INTO table_entity (id, area_id, table_number, capacity, is_active) VALUES
('t0000000-0000-0000-0000-000000000001', 'a1000000-0000-0000-0000-000000000001', 'T01', 2, TRUE),
('t0000000-0000-0000-0000-000000000002', 'a1000000-0000-0000-0000-000000000001', 'T02', 4, TRUE),
('t0000000-0000-0000-0000-000000000003', 'a1000000-0000-0000-0000-000000000001', 'T03', 6, TRUE),
('t0000000-0000-0000-0000-000000000004', 'a1000000-0000-0000-0000-000000000001', 'T04', 4, TRUE),
('t0000000-0000-0000-0000-000000000005', 'a1000000-0000-0000-0000-000000000001', 'T05', 2, TRUE),
('t0000000-0000-0000-0000-000000000006', 'a1000000-0000-0000-0000-000000000002', 'F01', 4, TRUE),
('t0000000-0000-0000-0000-000000000007', 'a1000000-0000-0000-0000-000000000002', 'F02', 6, TRUE),
('t0000000-0000-0000-0000-000000000008', 'a1000000-0000-0000-0000-000000000002', 'F03', 8, TRUE),
('t0000000-0000-0000-0000-000000000009', 'a1000000-0000-0000-0000-000000000003', 'R01', 4, TRUE),
('t0000000-0000-0000-0000-000000000010', 'a1000000-0000-0000-0000-000000000003', 'R02', 6, TRUE),
('t0000000-0000-0000-0000-000000000011', 'a1000000-0000-0000-0000-000000000003', 'R03', 2, TRUE),
('t0000000-0000-0000-0000-000000000012', 'a1000000-0000-0000-0000-000000000004', 'P01', 8, TRUE)
ON CONFLICT (id) DO NOTHING;

-- 4. Roles
INSERT INTO role (id, name, description) VALUES
(1, 'ADMIN', 'System Administrator with full operational access'),
(2, 'MANAGER', 'Restaurant Floor Manager with override & cashier privileges'),
(3, 'WAITER', 'Waitstaff for guest seating, table assistance & food ordering'),
(4, 'KITCHEN_STAFF', 'Kitchen Chefs, sous-chefs and line cooks')
ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, description = EXCLUDED.description;

-- 5. Staff Accounts (Password: bcrypt hash of admin123, manager123, waiter123, chef123)
INSERT INTO user_account (id, role_id, branch_id, first_name, last_name, email, password_hash) VALUES
('u0000000-0000-0000-0000-000000000001', 1, 'a0000000-0000-0000-0000-000000000001', 'Admin', 'User', 'admin@dinedesk.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW'),
('u0000000-0000-0000-0000-000000000002', 2, 'a0000000-0000-0000-0000-000000000001', 'Rohan', 'Mehta', 'manager@dinedesk.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW'),
('u0000000-0000-0000-0000-000000000003', 3, 'a0000000-0000-0000-0000-000000000001', 'Priya', 'Sharma', 'waiter@dinedesk.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW'),
('u0000000-0000-0000-0000-000000000004', 3, 'a0000000-0000-0000-0000-000000000001', 'Arjun', 'Reddy', 'waiter2@dinedesk.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW'),
('u0000000-0000-0000-0000-000000000005', 4, 'a0000000-0000-0000-0000-000000000001', 'Vikram', 'Malhotra', 'chef@dinedesk.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW')
ON CONFLICT (email) DO NOTHING;

-- 6. Customers & Families (Rich variety including children and dietary restrictions)
INSERT INTO customer (id, first_name, last_name, phone, email) VALUES
('c0000000-0000-0000-0000-000000000001', 'Rajesh & Priya', 'Sharma (Family: 2 Adults + 2 Kids [Aarav 6y, Diya 9y])', '9876543210', 'rajesh.sharma@gmail.com'),
('c0000000-0000-0000-0000-000000000002', 'Vikramaditya & Sunita', 'Rao (Family: 2 Adults + 1 Toddler [Kabir 3y])', '9123456780', 'vikram.rao@gmail.com'),
('c0000000-0000-0000-0000-000000000003', 'Rohan & Tanya', 'Mehra (Family with Infant [Baby Maya 1y] - Jain Diet)', '9811223344', 'rohan.mehra@gmail.com'),
('c0000000-0000-0000-0000-000000000004', 'Amit & Neha', 'Verma (Family: 2 Adults + 1 Child [Rohan 8y])', '9845012345', 'amit.verma@gmail.com'),
('c0000000-0000-0000-0000-000000000005', 'Meera & Siddharth', 'Joshi (Family: 2 Adults + Twins [Neil & Rhea 5y])', '9533445566', 'meera.joshi@gmail.com'),
('c0000000-0000-0000-0000-000000000006', 'Sunil & Kavita', 'Reddy (Family: 3 Adults + 2 Kids [Ananya 7y, Ishaan 11y])', '9844332211', 'sunil.reddy@gmail.com'),
('c0000000-0000-0000-0000-000000000007', 'Deepak & Shweta', 'Agarwal (Family: 2 Adults + 1 Child [Advait 4y - Lactose Intolerant])', '9766554433', 'deepak.agarwal@gmail.com'),
('c0000000-0000-0000-0000-000000000008', 'Sneha', 'Kapadia (Strict Vegan & Severe Peanut Allergy)', '9988776655', 'sneha.kapadia@gmail.com'),
('c0000000-0000-0000-0000-000000000009', 'Dr. Arvind', 'Swaminathan (Senior Citizen - Diabetic & Low Sodium Diet)', '9744556677', 'arvind.swami@gmail.com'),
('c0000000-0000-0000-0000-000000000010', 'Natasha', 'Cooper (Gluten-Free & Celiac Diet)', '9899001122', 'natasha.cooper@gmail.com'),
('c0000000-0000-0000-0000-000000000011', 'Karthik', 'Subramanian (High Protein Diet)', '9731234567', 'karthik.sub@gmail.com'),
('c0000000-0000-0000-0000-000000000012', 'Aditi', 'Sengupta (Pure Vegetarian / Strict Jain Food)', '9611224466', 'aditi.sen@gmail.com'),
('c0000000-0000-0000-0000-000000000013', 'Marcus', 'Aurelius Vance (Food Critic & Solo Gourmet)', '9822334455', 'marcus.vance@gmail.com'),
('c0000000-0000-0000-0000-000000000014', 'Ananya', 'Sen (University Student Diner)', '9422331100', 'ananya.sen@gmail.com'),
('c0000000-0000-0000-0000-000000000015', 'Capt. Raghuveer', 'Singh (Senior Veteran & Large Family - 6 Guests)', '9810998877', 'raghuveer.singh@gmail.com')
ON CONFLICT (id) DO NOTHING;

-- 7. All 8 Menu Categories
INSERT INTO menu_category (id, name, description) VALUES
(1, 'Appetizers', 'Crispy starters, artisanal dips, and flavorful small plates'),
(2, 'Soups & Salads', 'Farm-fresh greens, wholesome bowls, and slow-simmered broths'),
(3, 'Main Course', 'Signature hearty entrees and gourmet culinary masterpieces'),
(4, 'Indian Specialties', 'Royal tandoori delights, aromatic curries, and freshly baked breads'),
(5, 'Italian/Continental', 'Handmade pasta, stone-baked pizzas, and continental classics'),
(6, 'Desserts', 'Decadent handcrafted sweet endings and artisanal pastries'),
(7, 'Beverages', 'Refreshing mocktails, craft coolers, fresh juices, and artisanal brews'),
(8, 'Chef’s Specials', 'Exclusive seasonal tasting creations by Executive Chef Vikram')
ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, description = EXCLUDED.description;

-- 8. Menu Items (with rich dietary tags, kid-friendly indicators, and pricing)
INSERT INTO menu_item (id, category_id, name, description, current_price, is_active) VALUES
-- Appetizers
('m1000000-0000-0000-0000-000000000001', 1, 'Garlic Cheese Baguette', '[VEG] [KID-FRIENDLY] Crispy toasted French baguette brushed with roasted garlic herb butter and loaded with melted mozzarella.', 190.00, TRUE),
('m1000000-0000-0000-0000-000000000002', 1, 'Crispy Paneer Tikka Pops', '[VEG] [GLUTEN-FREE] [JAIN-AVAILABLE] Charred cottage cheese cubes marinated in smoked tandoori spices and mint glaze.', 230.00, TRUE),
('m1000000-0000-0000-0000-000000000003', 1, 'Crispy Corn & Jalapeño Croquettes', '[VEG] [KID-FRIENDLY] Golden fried croquettes with sweet corn kernels, melted cheddar, and smoked paprika mayo.', 210.00, TRUE),
('m1000000-0000-0000-0000-000000000004', 1, 'Smoked Truffle Potato Wedges', '[VEGAN] [GLUTEN-FREE] Hand-cut russet potato wedges dusted with black truffle sea salt and rosemary.', 180.00, TRUE),
('m1000000-0000-0000-0000-000000000005', 1, 'Zesty Herb Chicken Strips', '[NON-VEG] [KID-FRIENDLY] Tender panko-crusted chicken tenders served with honey mustard and garlic dip.', 260.00, TRUE),
('m1000000-0000-0000-0000-000000000006', 1, 'Dynamite Crispy Prawns', '[NON-VEG] Crispy battered tiger prawns tossed in signature sriracha togarashi aioli.', 340.00, TRUE),
('m1000000-0000-0000-0000-000000000007', 1, 'Crispy Veg Spring Rolls', '[VEGAN] [KID-FRIENDLY] Thin golden rolls stuffed with shredded vegetables and served with sweet chili dip.', 180.00, TRUE),

-- Soups & Salads
('m2000000-0000-0000-0000-000000000001', 2, 'Roasted Plum Tomato Basil Soup', '[VEGAN] [GLUTEN-FREE] [JAIN-AVAILABLE] Slow-roasted vine tomato soup infused with sweet basil, served with herbed croutons.', 180.00, TRUE),
('m2000000-0000-0000-0000-000000000002', 2, 'Cream of Wild Forest Mushroom', '[VEG] [GLUTEN-FREE] Velvety blend of button, shiitake, and porcini mushrooms with a swirl of fresh cream.', 210.00, TRUE),
('m2000000-0000-0000-0000-000000000003', 2, 'Mediterranean Greek Feta Salad', '[VEG] [GLUTEN-FREE] Crisp romaine lettuce, Kalamata olives, English cucumber, cherry tomatoes, and creamy feta cheese in lemon vinaigrette.', 240.00, TRUE),
('m2000000-0000-0000-0000-000000000004', 2, 'Classic Caesar Salad with Grilled Chicken', '[NON-VEG] Crisp iceberg leaves, parmesan ribbons, garlic croutons, and grilled chicken breast tossed in house Caesar dressing.', 280.00, TRUE),
('m2000000-0000-0000-0000-000000000005', 2, 'Sweet Corn & Vegetable Velouté', '[VEGAN] [KID-FRIENDLY] Silky sweet corn soup with baby spinach and toasted sesame oil.', 170.00, TRUE),
('m2000000-0000-0000-0000-000000000006', 2, 'Quinoa & Roasted Beetroot Power Bowl', '[VEGAN] [GLUTEN-FREE] Organic tri-color quinoa, baby spinach, avocado, candied walnuts, and citrus vinaigrette.', 260.00, TRUE),

-- Main Course
('m3000000-0000-0000-0000-000000000001', 3, 'Wild Mushroom & Truffle Risotto', '[VEG] [GLUTEN-FREE] Creamy Arborio rice slow-cooked with white wine, wild porcini, parmesan reggiano, and thyme.', 320.00, TRUE),
('m3000000-0000-0000-0000-000000000002', 3, 'Grilled Cottage Cheese Steak', '[GLUTEN-FREE] Charred herb-marinated cottage cheese steak served with ratatouille vegetables, mashed potatoes, and pepper jus.', 310.00, TRUE),
('m3000000-0000-0000-0000-000000000003', 3, 'Pan-Seared Norwegian Salmon', '[NON-VEG] [GLUTEN-FREE] Atlantic salmon fillet served with lemon dill butter sauce, grilled asparagus, and saffron mash.', 480.00, TRUE),
('m3000000-0000-0000-0000-000000000004', 3, 'Herb-Crusted Grilled Chicken Breast', '[NON-VEG] Tender breast fillet served with sautéed greens, roasted baby potatoes, and mushroom demi-glace.', 360.00, TRUE),
('m3000000-0000-0000-0000-000000000005', 3, 'Slow-Braised Moroccan Lamb Tagine', '[NON-VEG] Tender boneless lamb braised with apricots, toasted almonds, and aromatic couscous.', 440.00, TRUE),
('m3000000-0000-0000-0000-000000000006', 3, 'Mediterranean Roasted Veggie Platter', '[VEGAN] [GLUTEN-FREE] Charred zucchini, bell peppers, asparagus, and portobello mushrooms over herb hummus.', 290.00, TRUE),

-- Indian Specialties
('m4000000-0000-0000-0000-000000000001', 4, 'Paneer Butter Masala Royale', '[VEG] [GLUTEN-FREE] [JAIN-AVAILABLE] Tender cottage cheese cubes in rich tomato, cultured butter, and cashew gravy.', 290.00, TRUE),
('m4000000-0000-0000-0000-000000000002', 4, 'Dal Makhani Bukhara', '[VEG] [GLUTEN-FREE] Slow-cooked black lentils simmered overnight for 24 hours with butter and country cream.', 260.00, TRUE),
('m4000000-0000-0000-0000-000000000003', 4, 'Butter Chicken Delhi Style', '[NON-VEG] Tandoor-roasted chicken pieces in a silky, sweet and mildly spiced makhani sauce.', 350.00, TRUE),
('m4000000-0000-0000-0000-000000000004', 4, 'Dum Murgh Awadhi Biryani', '[NON-VEG] Fragrant long-grain basmati rice layered with spiced chicken, caramelized onions, saffron, and fresh mint.', 360.00, TRUE),
('m4000000-0000-0000-0000-000000000005', 4, 'Nizami Veg Dum Biryani', '[VEG] [GLUTEN-FREE] [JAIN-AVAILABLE] Garden vegetables and basmati rice slow cooked under sealed pot with kewra and rose water.', 280.00, TRUE),
('m4000000-0000-0000-0000-000000000006', 4, 'Butter Garlic Naan', '[VEG] Fresh tandoor-baked leavened bread brushed with garlic flakes and cultured butter.', 60.00, TRUE),
('m4000000-0000-0000-0000-000000000007', 4, 'Kadhai Paneer Special', '[VEG] [GLUTEN-FREE] Paneer batons tossed with bell peppers, crushed coriander seeds, and whole dried red chilies.', 280.00, TRUE),

-- Italian/Continental
('m5000000-0000-0000-0000-000000000001', 5, 'Classic Margherita Pizza', '[VEG] [KID-FRIENDLY] [JAIN-AVAILABLE] Hand-stretched sourdough crust topped with San Marzano tomato sauce, fresh basil, and fior di latte mozzarella.', 320.00, TRUE),
('m5000000-0000-0000-0000-000000000002', 5, 'Chicken Alfredo Fettuccine', '[NON-VEG] [KID-FRIENDLY] Handmade flat ribbon pasta tossed in rich parmesan garlic cream sauce with grilled chicken breast pieces.', 290.00, TRUE),
('m5000000-0000-0000-0000-000000000003', 5, 'Steak Spaghetti Pomodoro e Basilico', '[NON-VEG] Artisanal spaghetti with grilled steak slices in sweet cherry tomato sauce, extra virgin olive oil, and fresh garden basil.', 270.00, TRUE),
('m5000000-0000-0000-0000-000000000004', 5, 'Smoked Chicken & Pesto Pizza', '[NON-VEG] Thin crust pizza with basil pesto base, shredded smoked chicken, sun-dried tomatoes, and mozzarella.', 380.00, TRUE),
('m5000000-0000-0000-0000-000000000005', 5, 'Four-Cheese Quattro Formaggi Pizza', '[VEG] [KID-FRIENDLY] Mozzarella, gorgonzola, fontina, and parmigiano on a crisp hand-tossed base.', 360.00, TRUE),
('m5000000-0000-0000-0000-000000000006', 5, 'Truffle Porcini Ravioli', '[VEG] Handmade pasta pockets stuffed with wild mushrooms in sage and brown butter emulsion.', 340.00, TRUE),

-- Desserts
('m6000000-0000-0000-0000-000000000001', 6, 'Sizzling Chocolate Walnut Brownie', '[VEG] [KID-FRIENDLY] Warm decadent fudge brownie on hot cast iron, topped with Madagascar vanilla gelato and dark chocolate ganache.', 170.00, TRUE),
('m6000000-0000-0000-0000-000000000002', 6, 'Classic Venetian Tiramisu', '[VEG] Espresso-soaked savoiardi ladyfingers layered with velvety mascarpone cheese and dusted with Belgian cocoa.', 240.00, TRUE),
('m6000000-0000-0000-0000-000000000003', 6, 'Baked New York Raspberry Cheesecake', '[VEG] Rich and dense cream cheese cake on a graham cracker crust, drizzled with tart raspberry coulis.', 220.00, TRUE),
('m6000000-0000-0000-0000-000000000004', 6, 'Warm Gulab Jamun with Kesari Rabdi', '[VEG] [JAIN-AVAILABLE] Traditional khoya dumplings soaked in saffron syrup, served warm over creamy chilled saffron rabdi.', 150.00, TRUE),
('m6000000-0000-0000-0000-000000000005', 6, 'Belgian Dark Chocolate Lava Cake', '[VEG] [KID-FRIENDLY] Molten centered warm chocolate cake served with fresh berries and vanilla ice cream.', 200.00, TRUE),
('m6000000-0000-0000-0000-000000000006', 6, 'Mango Kulfi Falooda Sundae', '[VEG] [GLUTEN-FREE] Rich frozen mango kulfi slices with basil seeds, rose syrup, and vermicelli.', 160.00, TRUE),

-- Beverages
('m7000000-0000-0000-0000-000000000001', 7, 'Signature Wild Berry Spritzer', '[VEGAN] [KID-FRIENDLY] Refreshing blend of crushed forest berries, mint leaves, fresh lime, and sparkling soda.', 130.00, TRUE),
('m7000000-0000-0000-0000-000000000002', 7, 'Tropical Mango Passion Sparkler', '[VEGAN] [KID-FRIENDLY] Sweet Alphonso mango purée infused with passion fruit and crushed ice.', 140.00, TRUE),
('m7000000-0000-0000-0000-000000000003', 7, 'Cold Brew Iced Vanilla Latte', '[VEG] [GLUTEN-FREE] 16-hour steeped single-origin Arabica cold brew poured over chilled milk and vanilla syrup.', 150.00, TRUE),
('m7000000-0000-0000-0000-000000000004', 7, 'Virgin Mojito Royale', '[VEGAN] Fresh garden mint muddled with Persian lime wedges, cane sugar, and chilled club soda.', 120.00, TRUE),
('m7000000-0000-0000-0000-000000000005', 7, 'Masala Cutting Chai', '[VEG] Royal slow-brewed black tea with crushed green cardamom, ginger, and cinnamon.', 60.00, TRUE),
('m7000000-0000-0000-0000-000000000006', 7, 'Fresh Alphonso Mango Smoothie', '[VEG] [KID-FRIENDLY] Creamy blended Greek yogurt with fresh ripe mango puree and honey.', 150.00, TRUE),
('m7000000-0000-0000-0000-000000000007', 7, 'Artisan Blue Pea Flower Lemonade', '[VEGAN] Natural butterfly pea floral tea infused with freshly squeezed lime and sparkling water.', 135.00, TRUE),

-- Chef’s Specials
('m8000000-0000-0000-0000-000000000001', 8, 'Chef Vikram''s Truffle Infused Risotto', '[CHEF-SPECIAL] [VEG] [GLUTEN-FREE] Carnaroli rice cooked with shaved black winter truffles, aged 24-month Parmigiano, and white truffle oil.', 450.00, TRUE),
('m8000000-0000-0000-0000-000000000002', 8, 'Smoked Kashmiri Lamb Shank', '[CHEF-SPECIAL] [NON-VEG] [GLUTEN-FREE] 6-hour braised lamb shank in rich Kashmiri saffron chili reduction, served with warqi paratha.', 540.00, TRUE),
('m8000000-0000-0000-0000-000000000003', 8, 'Lobster Thermidor Continental', '[CHEF-SPECIAL] [NON-VEG] Succulent lobster meat baked with egg yolk, gruyère cheese, and dijon mustard cream sauce.', 650.00, TRUE),
('m8000000-0000-0000-0000-000000000004', 8, 'Avocado & Edamame Tartare', '[CHEF-SPECIAL] [VEGAN] [GLUTEN-FREE] Ripe Hass avocado stacked with young edamame, ponzu pearls, and lotus root crisps.', 340.00, TRUE),
('m8000000-0000-0000-0000-000000000005', 8, 'Gold Leaf Royal Shahi Tukda', '[CHEF-SPECIAL] [VEG] Crispy ghee-fried brioche steeped in cardamom saffron syrup, covered in 24k edible gold leaf and pistachio rabdi.', 280.00, TRUE),
('m8000000-0000-0000-0000-000000000006', 8, 'Chilean Sea Bass in Saffron Beurre Blanc', '[CHEF-SPECIAL] [NON-VEG] [GLUTEN-FREE] Pan-roasted sea bass fillet on a bed of braised leeks with Kashmiri saffron butter sauce.', 580.00, TRUE)
ON CONFLICT (id) DO UPDATE SET 
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    current_price = EXCLUDED.current_price;

-- 9. Discounts
INSERT INTO discount (id, name, description, discount_type, value, max_discount_amount, is_active) VALUES
('d0000000-0000-0000-0000-000000000001', 'WELCOME10', '10% off for first-time dining guests', 'PERCENTAGE', 10.00, 200.00, TRUE),
('d0000000-0000-0000-0000-000000000002', 'FAMILY20', '20% off for Family Tables with Children on Weekends', 'PERCENTAGE', 20.00, 400.00, TRUE),
('d0000000-0000-0000-0000-000000000003', 'KIDSDAY', 'Flat ₹100 discount on family dining with kids', 'FIXED', 100.00, NULL, TRUE),
('d0000000-0000-0000-0000-000000000004', 'CHEFVIP', '25% Exclusive Chef Special Dining Pass', 'PERCENTAGE', 25.00, 600.00, TRUE)
ON CONFLICT (id) DO NOTHING;

-- 10. Advance Reservations (Families with kids & dietary notices)
INSERT INTO reservation (id, table_id, customer_id, start_time, end_time, guest_count, status) VALUES
('r0000000-0000-0000-0000-000000000001', 't0000000-0000-0000-0000-000000000006', 'c0000000-0000-0000-0000-000000000001', NOW() + INTERVAL '2 hour', NOW() + INTERVAL '4 hour', 4, 'CONFIRMED'),
('r0000000-0000-0000-0000-000000000002', 't0000000-0000-0000-0000-000000000001', 'c0000000-0000-0000-0000-000000000008', NOW() + INTERVAL '3 hour', NOW() + INTERVAL '5 hour', 2, 'CONFIRMED'),
('r0000000-0000-0000-0000-000000000003', 't0000000-0000-0000-0000-000000000007', 'c0000000-0000-0000-0000-000000000003', NOW() + INTERVAL '1 day 1 hour', NOW() + INTERVAL '1 day 3 hour', 6, 'CONFIRMED'),
('r0000000-0000-0000-0000-000000000004', 't0000000-0000-0000-0000-000000000012', 'c0000000-0000-0000-0000-000000000013', NOW() + INTERVAL '2 day', NOW() + INTERVAL '2 day 3 hour', 4, 'CONFIRMED')
ON CONFLICT (id) DO NOTHING;

-- 11. Active Dining Session on Table F01 (Family with child Rohan)
INSERT INTO dining_session (id, table_id, customer_id, guest_count, status, start_time) VALUES
('s0000000-0000-0000-0000-000000000001', 't0000000-0000-0000-0000-000000000006', 'c0000000-0000-0000-0000-000000000004', 3, 'ACTIVE', NOW() - INTERVAL '45 minute')
ON CONFLICT (id) DO NOTHING;

-- Order with "Note to Chef" slots
INSERT INTO customer_order (id, session_id, user_id, status, created_at) VALUES
('o0000000-0000-0000-0000-000000000001', 's0000000-0000-0000-0000-000000000001', 'u0000000-0000-0000-0000-000000000003', 'PREPARING', NOW() - INTERVAL '40 minute')
ON CONFLICT (id) DO NOTHING;

-- Order Items with detailed Special Requests / Note to Chef
INSERT INTO order_item (id, order_id, item_id, quantity, unit_price, special_requests) VALUES
('oi000000-0000-0000-0000-000000000001', 'o0000000-0000-0000-0000-000000000001', 'm5000000-0000-0000-0000-000000000001', 1, 320.00, 'Note to Chef: Extra mild sauce & sliced into 8 small triangles for the 8-year-old child'),
('oi000000-0000-0000-0000-000000000002', 'o0000000-0000-0000-0000-000000000001', 'm5000000-0000-0000-0000-000000000002', 1, 290.00, 'Note to Chef: Mild garlic, extra grated parmesan on top'),
('oi000000-0000-0000-0000-000000000003', 'o0000000-0000-0000-0000-000000000001', 'm4000000-0000-0000-0000-000000000001', 1, 290.00, 'Note to Chef: Medium spice, soft paneer'),
('oi000000-0000-0000-0000-000000000004', 'o0000000-0000-0000-0000-000000000001', 'm4000000-0000-0000-0000-000000000006', 3, 60.00, 'Note to Chef: Well done, crispy edges'),
('oi000000-0000-0000-0000-000000000005', 'o0000000-0000-0000-0000-000000000001', 'm7000000-0000-0000-0000-000000000001', 2, 130.00, 'Note to Chef: Less ice for the kid''s drink')
ON CONFLICT (id) DO NOTHING;

-- Kitchen Ticket
INSERT INTO kitchen_ticket (id, order_id, status, prep_start_time) VALUES
('kt000000-0000-0000-0000-000000000001', 'o0000000-0000-0000-0000-000000000001', 'IN_PROGRESS', NOW() - INTERVAL '25 minute')
ON CONFLICT (id) DO NOTHING;

-- 12. Completed Historical Dining Session on Table T03 (Sharma Family with 2 Kids)
INSERT INTO dining_session (id, table_id, customer_id, guest_count, status, start_time, end_time) VALUES
('s0000000-0000-0000-0000-000000000002', 't0000000-0000-0000-0000-000000000003', 'c0000000-0000-0000-0000-000000000001', 4, 'COMPLETED', NOW() - INTERVAL '3 hour', NOW() - INTERVAL '1 hour 30 minute')
ON CONFLICT (id) DO NOTHING;

INSERT INTO customer_order (id, session_id, user_id, status, created_at) VALUES
('o0000000-0000-0000-0000-000000000002', 's0000000-0000-0000-0000-000000000002', 'u0000000-0000-0000-0000-000000000003', 'SERVED', NOW() - INTERVAL '2 hour 50 minute')
ON CONFLICT (id) DO NOTHING;

INSERT INTO order_item (id, order_id, item_id, quantity, unit_price, special_requests) VALUES
('oi000000-0000-0000-0000-000000000006', 'o0000000-0000-0000-0000-000000000002', 'm1000000-0000-0000-0000-000000000005', 2, 260.00, 'Note to Chef: Kid''s portion, no chili flakes, honey mustard dip on side'),
('oi000000-0000-0000-0000-000000000007', 'o0000000-0000-0000-0000-000000000002', 'm4000000-0000-0000-0000-000000000004', 2, 360.00, 'Note to Chef: Authentic Dum preparation with raita'),
('oi000000-0000-0000-0000-000000000008', 'o0000000-0000-0000-0000-000000000002', 'm6000000-0000-0000-0000-000000000001', 2, 170.00, 'Note to Chef: Extra vanilla scoop for the kids'),
('oi000000-0000-0000-0000-000000000009', 'o0000000-0000-0000-0000-000000000002', 'm7000000-0000-0000-0000-000000000002', 2, 140.00, 'Note to Chef: Served chilled in tall glasses with fun straws')
ON CONFLICT (id) DO NOTHING;

INSERT INTO kitchen_ticket (id, order_id, status, prep_start_time, ready_time) VALUES
('kt000000-0000-0000-0000-000000000002', 'o0000000-0000-0000-0000-000000000002', 'READY', NOW() - INTERVAL '2 hour 50 minute', NOW() - INTERVAL '2 hour 20 minute')
ON CONFLICT (id) DO NOTHING;

-- Bill (Subtotal: 1860.00, Tax: 93.00, Total: 1953.00)
INSERT INTO bill (id, session_id, subtotal, tax_amount, total_amount, status) VALUES
('b0000000-0000-0000-0000-000000000001', 's0000000-0000-0000-0000-000000000002', 1860.00, 93.00, 1953.00, 'PAID')
ON CONFLICT (id) DO NOTHING;

INSERT INTO bill_item (id, bill_id, order_item_id, item_name_snapshot, quantity, unit_price) VALUES
('bi000000-0000-0000-0000-000000000001', 'b0000000-0000-0000-0000-000000000001', 'oi000000-0000-0000-0000-000000000006', 'Zesty Herb Chicken Strips', 2, 260.00),
('bi000000-0000-0000-0000-000000000002', 'b0000000-0000-0000-0000-000000000001', 'oi000000-0000-0000-0000-000000000007', 'Dum Murgh Awadhi Biryani', 2, 360.00),
('bi000000-0000-0000-0000-000000000003', 'b0000000-0000-0000-0000-000000000001', 'oi000000-0000-0000-0000-000000000008', 'Sizzling Chocolate Walnut Brownie', 2, 170.00),
('bi000000-0000-0000-0000-000000000004', 'b0000000-0000-0000-0000-000000000001', 'oi000000-0000-0000-0000-000000000009', 'Tropical Mango Passion Sparkler', 2, 140.00)
ON CONFLICT (id) DO NOTHING;

-- Completed Payment
INSERT INTO payment (id, bill_id, amount, payment_method, status, transaction_ref) VALUES
('p0000000-0000-0000-0000-000000000001', 'b0000000-0000-0000-0000-000000000001', 1953.00, 'CARD', 'COMPLETED', 'TXN-CARD-F9821A4B')
ON CONFLICT (id) DO NOTHING;

COMMIT;
