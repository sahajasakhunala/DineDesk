import sys
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.core.security import get_password_hash
from app.models.base import Base
from app.models.restaurant import Branch, DiningArea, TableEntity
from app.models.users import Role, UserAccount, Customer
from app.models.menu import MenuCategory, MenuItem
from app.models.billing import Discount, Bill, BillItem, Payment, DiscountApplication
from app.models.dining import Reservation, DiningSession
from app.models.orders import CustomerOrder, OrderItem, OrderStatusHistory
from app.models.kitchen import KitchenTicket, KitchenTicketItem

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def seed():
    # Drop and recreate all tables for a fresh, clean database state
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    try:
        print("[INFO] Starting DineDesk Database Seeding with Realistic Staggered Timestamps...")
        # Base anchor time without microseconds
        now = datetime.now(timezone.utc).replace(microsecond=0)

        # 1. Branch (Created 180 days ago at 09:15:00)
        branch_created = (now - timedelta(days=180)).replace(hour=9, minute=15, second=0)
        branch = Branch(
            name="DineDesk Hyderabad",
            address="Road No. 36, Jubilee Hills, Hyderabad, Telangana 500033",
            phone="+91 91545 07776",
            created_at=branch_created,
            updated_at=branch_created
        )
        db.add(branch)
        db.flush()

        # 2. Dining Areas (Created 180 days ago, staggered by 15 mins)
        area_names = ["Main Dining Hall", "Family & Kids Lounge", "Romantic Terrace (Rooftop)", "Chef's Private Dining"]
        areas = {}
        for idx, aname in enumerate(area_names):
            a_time = branch_created + timedelta(minutes=idx * 15)
            area = DiningArea(
                branch_id=branch.id, 
                name=aname,
                created_at=a_time,
                updated_at=a_time
            )
            db.add(area)
            db.flush()
            areas[aname] = area

        # 3. Tables (Created 175 days ago, staggered hours & minutes)
        tables_def = [
            ("T01", 2, "Main Dining Hall"), ("T02", 4, "Main Dining Hall"),
            ("T03", 6, "Main Dining Hall"), ("T04", 4, "Main Dining Hall"),
            ("T05", 2, "Main Dining Hall"), ("F01", 4, "Family & Kids Lounge"),
            ("F02", 6, "Family & Kids Lounge"), ("F03", 8, "Family & Kids Lounge"),
            ("R01", 4, "Romantic Terrace (Rooftop)"), ("R02", 6, "Romantic Terrace (Rooftop)"),
            ("R03", 2, "Romantic Terrace (Rooftop)"), ("P01", 8, "Chef's Private Dining"),
        ]
        tables_map = {}
        for idx, (tnum, cap, aname) in enumerate(tables_def):
            t_time = (branch_created + timedelta(days=5, hours=10)).replace(minute=idx*4, second=idx*3)
            table = TableEntity(
                area_id=areas[aname].id,
                table_number=tnum,
                capacity=cap,
                is_active=True,
                created_at=t_time,
                updated_at=t_time
            )
            db.add(table)
            db.flush()
            tables_map[tnum] = table

        # 4. Roles
        roles_def = [
            ("ADMIN", "System Administrator with full operational access"),
            ("MANAGER", "Restaurant Floor Manager with override & cashier privileges"),
            ("WAITER", "Waitstaff for guest seating, table assistance & food ordering"),
            ("KITCHEN_STAFF", "Kitchen Chefs, sous-chefs and line cooks")
        ]
        roles = {}
        for rname, rdesc in roles_def:
            role = Role(name=rname, description=rdesc)
            db.add(role)
            db.flush()
            roles[rname] = role

        # 5. Staff Accounts (Onboarded at distinct hours/minutes/seconds)
        users_def = [
            ("admin@dinedesk.com", "Admin", "User", "admin123", "ADMIN", 150, 9, 30, 15),
            ("manager@dinedesk.com", "Rohan", "Mehta", "manager123", "MANAGER", 120, 10, 45, 20),
            ("waiter@dinedesk.com", "Priya", "Sharma", "waiter123", "WAITER", 90, 11, 15, 45),
            ("waiter2@dinedesk.com", "Arjun", "Reddy", "waiter123", "WAITER", 60, 14, 20, 10),
            ("chef@dinedesk.com", "Vikram", "Malhotra", "chef123", "KITCHEN_STAFF", 30, 16, 0, 5),
        ]
        users_map = {}
        for email, fn, ln, pw, rname, days_ago, hr, mn, sc in users_def:
            u_time = (now - timedelta(days=days_ago)).replace(hour=hr, minute=mn, second=sc)
            user = UserAccount(
                branch_id=branch.id,
                role_id=roles[rname].id,
                first_name=fn,
                last_name=ln,
                email=email,
                password_hash=get_password_hash(pw),
                created_at=u_time,
                updated_at=u_time
            )
            db.add(user)
            db.flush()
            users_map[email] = user

        # 6. Customers (Registered at realistic, unique times of day)
        customers_def = [
            ("Rajesh & Priya", "Sharma (Family: 2 Adults + 2 Kids [Aarav 6y, Diya 9y])", "9876543210", "rajesh.sharma@gmail.com", 120, 10, 15, 22),
            ("Vikramaditya & Sunita", "Rao (Family: 2 Adults + 1 Toddler [Kabir 3y])", "9123456780", "vikram.rao@gmail.com", 110, 11, 42, 18),
            ("Rohan & Tanya", "Mehra (Family with Infant [Baby Maya 1y] - Jain Diet)", "9811223344", "rohan.mehra@gmail.com", 95, 14, 5, 50),
            ("Amit & Neha", "Verma (Family: 2 Adults + 1 Child [Rohan 8y])", "9845012345", "amit.verma@gmail.com", 85, 15, 22, 10),
            ("Meera & Siddharth", "Joshi (Family: 2 Adults + Twins [Neil & Rhea 5y])", "9533445566", "meera.joshi@gmail.com", 70, 16, 35, 44),
            ("Sunil & Kavita", "Reddy (Family: 3 Adults + 2 Kids [Ananya 7y, Ishaan 11y])", "9844332211", "sunil.reddy@gmail.com", 60, 17, 10, 5),
            ("Deepak & Shweta", "Agarwal (Family: 2 Adults + 1 Child [Advait 4y - Lactose Intolerant])", "9766554433", "deepak.agarwal@gmail.com", 50, 18, 42, 30),
            ("Sneha", "Kapadia (Strict Vegan & Severe Peanut Allergy)", "9988776655", "sneha.kapadia@gmail.com", 45, 9, 15, 12),
            ("Dr. Arvind", "Swaminathan (Senior Citizen - Diabetic & Low Sodium Diet)", "9744556677", "arvind.swami@gmail.com", 40, 12, 28, 40),
            ("Natasha", "Cooper (Gluten-Free & Celiac Diet)", "9899001122", "natasha.cooper@gmail.com", 30, 13, 50, 15),
            ("Karthik", "Subramanian (High Protein Diet)", "9731234567", "karthik.sub@gmail.com", 20, 19, 5, 35),
            ("Aditi", "Sengupta (Pure Vegetarian / Strict Jain Food)", "9611224466", "aditi.sen@gmail.com", 15, 20, 33, 12),
            ("Marcus", "Aurelius Vance (Food Critic & Solo Gourmet)", "9822334455", "marcus.vance@gmail.com", 10, 14, 12, 40),
            ("Ananya", "Sen (University Student Diner)", "9422331100", "ananya.sen@gmail.com", 5, 17, 55, 8),
            ("Capt. Raghuveer", "Singh (Senior Veteran & Large Family - 6 Guests)", "9810998877", "raghuveer.singh@gmail.com", 2, 11, 22, 45)
        ]
        customers_map = {}
        for fn, ln, ph, em, days_ago, hr, mn, sc in customers_def:
            c_time = (now - timedelta(days=days_ago)).replace(hour=hr, minute=mn, second=sc)
            cust = Customer(
                first_name=fn,
                last_name=ln,
                phone=ph,
                email=em,
                created_at=c_time,
                updated_at=c_time
            )
            db.add(cust)
            db.flush()
            customers_map[em] = cust

        # 7. Menu Categories (Created 180 days ago at 10:00:00)
        categories_def = [
            ("Appetizers", "Crispy starters, artisanal dips, and flavorful small plates"),
            ("Soups & Salads", "Farm-fresh greens, wholesome bowls, and slow-simmered broths"),
            ("Main Course", "Signature hearty entrees and gourmet culinary masterpieces"),
            ("Indian Specialties", "Royal tandoori delights, aromatic curries, and freshly baked breads"),
            ("Italian/Continental", "Handmade pasta, stone-baked pizzas, and continental classics"),
            ("Desserts", "Decadent handcrafted sweet endings and artisanal pastries"),
            ("Beverages", "Refreshing mocktails, craft coolers, fresh juices, and artisanal brews"),
            ("Chef’s Specials", "Exclusive seasonal tasting creations by Executive Chef Vikram")
        ]
        categories = {}
        for idx, (cname, cdesc) in enumerate(categories_def):
            cat_time = (branch_created + timedelta(days=1)).replace(hour=10, minute=idx*5, second=0)
            cat = MenuCategory(name=cname, description=cdesc)
            db.add(cat)
            db.flush()
            categories[cname] = cat

        # 8. Menu Items (Created 175 days ago, updated 10 days ago at varied times)
        menu_items_def = [
            ("Garlic Cheese Baguette", "[VEG] [KID-FRIENDLY] Crispy toasted French baguette brushed with roasted garlic herb butter and loaded with melted mozzarella.", Decimal("190.00"), "Appetizers", "https://images.unsplash.com/photo-1619535860434-ba1d8fa12536?auto=format&fit=crop&w=800&q=80"),
            ("Crispy Paneer Tikka Pops", "[VEG] [GLUTEN-FREE] [JAIN-AVAILABLE] Charred cottage cheese cubes marinated in smoked tandoori spices and mint glaze.", Decimal("230.00"), "Appetizers", "https://images.unsplash.com/photo-1567188040759-fb8a883dc6d8?auto=format&fit=crop&w=800&q=80"),
            ("Crispy Corn & Jalapeño Croquettes", "[VEG] [KID-FRIENDLY] Golden fried croquettes with sweet corn kernels, melted cheddar, and smoked paprika mayo.", Decimal("210.00"), "Appetizers", "https://images.unsplash.com/photo-1541529086526-db283c563270?auto=format&fit=crop&w=800&q=80"),
            ("Smoked Truffle Potato Wedges", "[VEGAN] [GLUTEN-FREE] Hand-cut russet potato wedges dusted with black truffle sea salt and rosemary.", Decimal("180.00"), "Appetizers", "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?auto=format&fit=crop&w=800&q=80"),
            ("Zesty Herb Chicken Strips", "[NON-VEG] [KID-FRIENDLY] Tender panko-crusted chicken tenders served with honey mustard and garlic dip.", Decimal("260.00"), "Appetizers", "https://images.unsplash.com/photo-1562967914-608f82629710?auto=format&fit=crop&w=800&q=80"),
            ("Dynamite Crispy Prawns", "[NON-VEG] Crispy battered tiger prawns tossed in signature sriracha togarashi aioli.", Decimal("340.00"), "Appetizers", "https://images.unsplash.com/photo-1565680018434-b513d5e5fd47?auto=format&fit=crop&w=800&q=80"),
            ("Roasted Plum Tomato Basil Soup", "[VEGAN] [GLUTEN-FREE] [JAIN-AVAILABLE] Slow-roasted vine tomato soup infused with sweet basil, served with herbed croutons.", Decimal("180.00"), "Soups & Salads", "https://images.unsplash.com/photo-1547592166-23ac45744acd?auto=format&fit=crop&w=800&q=80"),
            ("Cream of Wild Forest Mushroom", "[VEG] [GLUTEN-FREE] Velvety blend of button, shiitake, and porcini mushrooms with a swirl of fresh cream.", Decimal("210.00"), "Soups & Salads", "https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=800&q=80"),
            ("Mediterranean Greek Feta Salad", "[VEG] [GLUTEN-FREE] Crisp romaine lettuce, Kalamata olives, English cucumber, cherry tomatoes, and creamy feta cheese in lemon vinaigrette.", Decimal("240.00"), "Soups & Salads", "https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=800&q=80"),
            ("Classic Caesar Salad with Grilled Chicken", "[NON-VEG] Crisp iceberg leaves, parmesan ribbons, garlic croutons, and grilled chicken breast tossed in house Caesar dressing.", Decimal("280.00"), "Soups & Salads", "https://images.unsplash.com/photo-1550304943-4f24f54ddde9?auto=format&fit=crop&w=800&q=80"),
            ("Wild Mushroom & Truffle Risotto", "[VEG] [GLUTEN-FREE] Creamy Arborio rice slow-cooked with white wine, wild porcini, parmesan reggiano, and thyme.", Decimal("320.00"), "Main Course", "https://images.unsplash.com/photo-1633964913295-ceb43826e7c9?auto=format&fit=crop&w=800&q=80"),
            ("Grilled Cottage Cheese Steak", "[GLUTEN-FREE] Charred herb-marinated cottage cheese steak served with roasted ratatouille vegetables, mashed potatoes, and pepper jus.", Decimal("310.00"), "Main Course", "https://images.unsplash.com/photo-1567188040759-fb8a883dc6d8?auto=format&fit=crop&w=800&q=80"),
            ("Pan-Seared Norwegian Salmon", "[NON-VEG] [GLUTEN-FREE] Atlantic salmon fillet served with lemon dill butter sauce, grilled asparagus, and saffron mash.", Decimal("480.00"), "Main Course", "https://images.unsplash.com/photo-1467003909585-2f8a72700288?auto=format&fit=crop&w=800&q=80"),
            ("Herb-Crusted Grilled Chicken Breast", "[NON-VEG] Tender breast fillet served with sautéed greens, roasted baby potatoes, and mushroom demi-glace.", Decimal("360.00"), "Main Course", "https://images.unsplash.com/photo-1532550907401-a500c9a57435?auto=format&fit=crop&w=800&q=80"),
            ("Paneer Butter Masala Royale", "[VEG] [GLUTEN-FREE] [JAIN-AVAILABLE] Tender cottage cheese cubes in rich tomato, cultured butter, and cashew gravy.", Decimal("290.00"), "Indian Specialties", "https://images.unsplash.com/photo-1631452180519-c014fe946bc7?auto=format&fit=crop&w=800&q=80"),
            ("Dal Makhani Bukhara", "[VEG] [GLUTEN-FREE] Slow-cooked black lentils simmered overnight for 24 hours with butter and country cream.", Decimal("260.00"), "Indian Specialties", "https://images.unsplash.com/photo-1546833999-b9f581a1996d?auto=format&fit=crop&w=800&q=80"),
            ("Butter Chicken Delhi Style", "[NON-VEG] Tandoor-roasted chicken pieces in a silky, sweet and mildly spiced makhani sauce.", Decimal("350.00"), "Indian Specialties", "https://images.unsplash.com/photo-1603894584373-5ac82b2ae398?auto=format&fit=crop&w=800&q=80"),
            ("Dum Murgh Awadhi Biryani", "[NON-VEG] Fragrant long-grain basmati rice layered with spiced chicken, caramelized onions, saffron, and fresh mint.", Decimal("360.00"), "Indian Specialties", "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?auto=format&fit=crop&w=800&q=80"),
            ("Butter Garlic Naan", "[VEG] Fresh tandoor-baked leavened bread brushed with garlic flakes and cultured butter.", Decimal("60.00"), "Indian Specialties", "https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?auto=format&fit=crop&w=800&q=80"),
            ("Classic Margherita Pizza", "[VEG] [KID-FRIENDLY] [JAIN-AVAILABLE] Hand-stretched sourdough crust topped with San Marzano tomato sauce, fresh basil, and fior di latte mozzarella.", Decimal("320.00"), "Italian/Continental", "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?auto=format&fit=crop&w=800&q=80"),
            ("Chicken Alfredo Fettuccine", "[NON-VEG] [KID-FRIENDLY] Handmade flat ribbon pasta tossed in rich parmesan garlic cream sauce with grilled chicken breast pieces.", Decimal("290.00"), "Italian/Continental", "https://images.unsplash.com/photo-1645112411341-6c4fd023714a?auto=format&fit=crop&w=800&q=80"),
            ("Steak Spaghetti Pomodoro e Basilico", "[NON-VEG] Artisanal spaghetti with grilled steak slices in sweet cherry tomato pomodoro sauce, extra virgin olive oil, and fresh garden basil.", Decimal("270.00"), "Italian/Continental", "https://images.unsplash.com/photo-1551183053-bf91a1d81141?auto=format&fit=crop&w=800&q=80"),
            ("Smoked Chicken & Pesto Pizza", "[NON-VEG] Thin crust pizza with basil pesto base, shredded smoked chicken, sun-dried tomatoes, and mozzarella.", Decimal("380.00"), "Italian/Continental", "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=800&q=80"),
            ("Sizzling Chocolate Walnut Brownie", "[VEG] [KID-FRIENDLY] Warm decadent fudge brownie on hot cast iron, topped with Madagascar vanilla gelato and dark chocolate ganache.", Decimal("170.00"), "Desserts", "https://images.unsplash.com/photo-1606313564200-e75d5e30476c?auto=format&fit=crop&w=800&q=80"),
            ("Classic Venetian Tiramisu", "[VEG] Espresso-soaked savoiardi ladyfingers layered with velvety mascarpone cheese and dusted with Belgian cocoa.", Decimal("240.00"), "Desserts", "https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?auto=format&fit=crop&w=800&q=80"),
            ("Baked New York Raspberry Cheesecake", "[VEG] Rich and dense cream cheese cake on a graham cracker crust, drizzled with tart raspberry coulis.", Decimal("220.00"), "Desserts", "https://images.unsplash.com/photo-1533134242443-d4fd215305ad?auto=format&fit=crop&w=800&q=80"),
            ("Warm Gulab Jamun with Kesari Rabdi", "[VEG] [JAIN-AVAILABLE] Traditional khoya dumplings soaked in saffron syrup, served warm over creamy chilled saffron rabdi.", Decimal("150.00"), "Desserts", "https://images.unsplash.com/photo-1599488615731-7e5c2823ff28?auto=format&fit=crop&w=800&q=80"),
            ("Signature Wild Berry Spritzer", "[VEGAN] [KID-FRIENDLY] Refreshing blend of crushed forest berries, mint leaves, fresh lime, and sparkling soda.", Decimal("130.00"), "Beverages", "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?auto=format&fit=crop&w=800&q=80"),
            ("Tropical Mango Passion Sparkler", "[VEGAN] [KID-FRIENDLY] Sweet Alphonso mango purée infused with passion fruit and crushed ice.", Decimal("140.00"), "Beverages", "https://images.unsplash.com/photo-1546171753-97d7676e4602?auto=format&fit=crop&w=800&q=80"),
            ("Cold Brew Iced Vanilla Latte", "[VEG] [GLUTEN-FREE] 16-hour steeped single-origin Arabica cold brew poured over chilled milk and vanilla syrup.", Decimal("150.00"), "Beverages", "https://images.unsplash.com/photo-1517701550927-30cf4ba1dba5?auto=format&fit=crop&w=800&q=80"),
            ("Virgin Mojito Royale", "[VEGAN] Fresh garden mint muddled with Persian lime wedges, cane sugar, and chilled club soda.", Decimal("120.00"), "Beverages", "https://images.unsplash.com/photo-1551024709-8f23befc6f87?auto=format&fit=crop&w=800&q=80"),
            ("Chef Vikram's Truffle Infused Risotto", "[CHEF-SPECIAL] [VEG] [GLUTEN-FREE] Carnaroli rice cooked with shaved black winter truffles, aged 24-month Parmigiano, and white truffle oil.", Decimal("450.00"), "Chef’s Specials", "https://images.unsplash.com/photo-1633964913295-ceb43826e7c9?auto=format&fit=crop&w=800&q=80"),
            ("Smoked Kashmiri Lamb Shank", "[CHEF-SPECIAL] [NON-VEG] [GLUTEN-FREE] 6-hour braised lamb shank in rich Kashmiri saffron chili reduction, served with warqi paratha.", Decimal("540.00"), "Chef’s Specials", "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=800&q=80"),
            ("Lobster Thermidor Continental", "[CHEF-SPECIAL] [NON-VEG] Succulent lobster meat baked with egg yolk, gruyère cheese, and dijon mustard cream sauce.", Decimal("650.00"), "Chef’s Specials", "https://images.unsplash.com/photo-1553240799-36bbf332a5c3?auto=format&fit=crop&w=800&q=80"),
            ("Avocado & Edamame Tartare", "[CHEF-SPECIAL] [VEGAN] [GLUTEN-FREE] Ripe Hass avocado stacked with young edamame, ponzu pearls, and lotus root crisps.", Decimal("340.00"), "Chef’s Specials", "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=800&q=80")
        ]

        menu_items_map = {}
        for idx, (iname, idesc, iprice, cname, iurl) in enumerate(menu_items_def):
            item_created = (branch_created + timedelta(days=10)).replace(hour=11 + (idx % 8), minute=(idx * 7) % 60, second=(idx * 11) % 60)
            item_updated = (now - timedelta(days=10)).replace(hour=14 + (idx % 6), minute=(idx * 9) % 60, second=(idx * 13) % 60)
            item = MenuItem(
                category_id=categories[cname].id,
                name=iname,
                description=idesc,
                current_price=iprice,
                image_url=iurl,
                is_active=True,
                created_at=item_created,
                updated_at=item_updated
            )
            db.add(item)
            db.flush()
            menu_items_map[iname] = item

        # 9. Discounts (Created 90 days ago at 15:30:00)
        discounts_def = [
            ("WELCOME10", "10% off for first-time dining guests", "PERCENTAGE", Decimal("10.00"), Decimal("200.00")),
            ("FAMILY20", "20% off for Family Tables with Children on Weekends", "PERCENTAGE", Decimal("20.00"), Decimal("400.00")),
            ("KIDSDAY", "Flat ₹100 discount on family dining with kids", "FIXED", Decimal("100.00"), None),
            ("CHEFVIP", "25% Exclusive Chef Special Dining Pass", "PERCENTAGE", Decimal("25.00"), Decimal("600.00")),
        ]
        discounts_map = {}
        for idx, (dname, ddesc, dtype, dval, dmax) in enumerate(discounts_def):
            d_time = (now - timedelta(days=90)).replace(hour=15 + idx, minute=20 + idx*5, second=10)
            disc = Discount(
                name=dname,
                description=ddesc,
                discount_type=dtype,
                value=dval,
                max_discount_amount=dmax,
                is_active=True,
                created_at=d_time,
                updated_at=d_time
            )
            db.add(disc)
            db.flush()
            discounts_map[dname] = disc

        # 10. Advance Reservations (Booked for valid 90-minute webpage slots at least 3 days in advance)
        reservations_def = [
            ("rajesh.sharma@gmail.com", "F01", 3, 18, 30, 4, 4, "CONFIRMED"),   # 06:30 PM – 08:00 PM (4 days ahead)
            ("rohan.mehra@gmail.com", "F02", 5, 19, 0, 4, 6, "CONFIRMED"),     # 07:00 PM – 08:30 PM (4 days ahead)
            ("sunil.reddy@gmail.com", "F03", 4, 19, 30, 5, 5, "CONFIRMED"),    # 07:30 PM – 09:00 PM (5 days ahead)
            ("marcus.vance@gmail.com", "P01", 2, 20, 30, 5, 4, "CONFIRMED"),   # 08:30 PM – 10:00 PM (5 days ahead)
            ("sneha.kapadia@gmail.com", "T01", 1, 19, 30, 6, 2, "CONFIRMED")    # 07:30 PM – 09:00 PM (6 days ahead)
        ]
        for idx, (cemail, tnum, booked_days_ago, res_hour, res_min, day_offset, gcount, status) in enumerate(reservations_def):
            cust = customers_map[cemail]
            tbl = tables_map[tnum]
            res_created = (now - timedelta(days=booked_days_ago)).replace(hour=14 + idx, minute=12 + idx*8, second=25)
            st = (now + timedelta(days=day_offset)).replace(hour=res_hour, minute=res_min, second=0, microsecond=0)
            et = st + timedelta(minutes=90)
            res = Reservation(
                customer_id=cust.id,
                table_id=tbl.id,
                start_time=st,
                end_time=et,
                guest_count=gcount,
                status=status,
                created_at=res_created,
                updated_at=res_created
            )
            db.add(res)

        # 11. Active Dining Session on Table F01 (Started 45 mins ago at 19:15:20, updated 10 mins ago at 19:50:15)
        family_table = tables_map["F01"]
        family_cust = customers_map["amit.verma@gmail.com"]
        waiter_user = users_map["waiter@dinedesk.com"]

        active_created = (now - timedelta(minutes=45)).replace(second=20)
        active_updated = (now - timedelta(minutes=10)).replace(second=15)

        active_session = DiningSession(
            table_id=family_table.id,
            customer_id=family_cust.id,
            guest_count=3,
            status="ACTIVE",
            start_time=active_created,
            created_at=active_created,
            updated_at=active_updated
        )
        db.add(active_session)
        db.flush()

        # Place Active Order (Created 40 mins ago at 19:20:10, status updated 15 mins ago at 19:45:30)
        order_created = (now - timedelta(minutes=40)).replace(second=10)
        order_updated = (now - timedelta(minutes=15)).replace(second=30)

        order = CustomerOrder(
            session_id=active_session.id,
            user_id=waiter_user.id,
            status="PREPARING",
            created_at=order_created,
            updated_at=order_updated
        )
        db.add(order)
        db.flush()

        # Order Items (Staggered minutes/seconds when items were ordered)
        order_items_data = [
            ("Classic Margherita Pizza", 1, Decimal("320.00"), "Note to Chef: Extra mild sauce & sliced into 8 small triangles for the 8-year-old child", 38, 12),
            ("Chicken Alfredo Fettuccine", 1, Decimal("290.00"), "Note to Chef: Mild garlic, extra grated parmesan on top", 37, 45),
            ("Paneer Butter Masala Royale", 1, Decimal("290.00"), "Note to Chef: Medium spice, soft paneer", 35, 20),
            ("Butter Garlic Naan", 3, Decimal("60.00"), "Note to Chef: Well done, crispy edges", 34, 5),
            ("Signature Wild Berry Spritzer", 2, Decimal("130.00"), "Note to Chef: Less ice for the kid's drink", 32, 50)
        ]

        for iname, qty, uprice, req, item_min_ago, sec_val in order_items_data:
            item_obj = menu_items_map[iname]
            item_created_t = (now - timedelta(minutes=item_min_ago)).replace(second=sec_val)
            oi = OrderItem(
                order_id=order.id,
                item_id=item_obj.id,
                quantity=qty,
                unit_price=uprice,
                special_requests=req,
                created_at=item_created_t,
                updated_at=order_updated
            )
            db.add(oi)

        # Kitchen Ticket (Prep started 25 mins ago at 19:35:10)
        tkt_start = (now - timedelta(minutes=25)).replace(second=10)
        kitchen_ticket = KitchenTicket(
            order_id=order.id,
            status="IN_PROGRESS",
            prep_start_time=tkt_start,
            created_at=order_created,
            updated_at=tkt_start
        )
        db.add(kitchen_ticket)

        osh = OrderStatusHistory(
            order_id=order.id,
            status="PREPARING",
            changed_at=order_updated
        )
        db.add(osh)

        # 12. Completed Historical Dining Session on Table T03 (Occurred 3.5 hours ago, ended 1.5 hours ago)
        t03_table = tables_map["T03"]
        sharma_cust = customers_map["rajesh.sharma@gmail.com"]
        manager_user = users_map["manager@dinedesk.com"]

        past_start = (now - timedelta(hours=3, minutes=30)).replace(second=14)
        past_end = (now - timedelta(hours=1, minutes=30)).replace(second=45)

        completed_session = DiningSession(
            table_id=t03_table.id,
            customer_id=sharma_cust.id,
            guest_count=4,
            status="COMPLETED",
            start_time=past_start,
            end_time=past_end,
            created_at=past_start,
            updated_at=past_end
        )
        db.add(completed_session)
        db.flush()

        past_order_time = (past_start + timedelta(minutes=12)).replace(second=30)
        past_order = CustomerOrder(
            session_id=completed_session.id,
            user_id=waiter_user.id,
            status="SERVED",
            created_at=past_order_time,
            updated_at=past_end - timedelta(minutes=20)
        )
        db.add(past_order)
        db.flush()

        past_items = [
            ("Zesty Herb Chicken Strips", 2, Decimal("260.00"), "Note to Chef: Kid's portion, no chili flakes, honey mustard dip on side", 10),
            ("Dum Murgh Awadhi Biryani", 2, Decimal("360.00"), "Note to Chef: Authentic Dum preparation with raita", 15),
            ("Sizzling Chocolate Walnut Brownie", 2, Decimal("170.00"), "Note to Chef: Extra vanilla scoop for the kids", 35),
            ("Tropical Mango Passion Sparkler", 2, Decimal("140.00"), "Note to Chef: Served chilled in tall glasses with fun straws", 40)
        ]

        past_order_items = []
        for iname, qty, uprice, req, item_delay in past_items:
            item_obj = menu_items_map[iname]
            oi_time = past_order_time + timedelta(minutes=item_delay)
            oi = OrderItem(
                order_id=past_order.id,
                item_id=item_obj.id,
                quantity=qty,
                unit_price=uprice,
                special_requests=req,
                created_at=oi_time,
                updated_at=past_end - timedelta(minutes=20)
            )
            db.add(oi)
            db.flush()
            past_order_items.append((oi, iname, qty, uprice, oi_time))

        past_ticket = KitchenTicket(
            order_id=past_order.id,
            status="READY",
            prep_start_time=past_order_time + timedelta(minutes=5),
            ready_time=past_end - timedelta(minutes=25),
            created_at=past_order_time,
            updated_at=past_end - timedelta(minutes=25)
        )
        db.add(past_ticket)

        subtotal = Decimal("1860.00")
        tax = Decimal("93.00")
        total = subtotal + tax

        bill_time = past_end - timedelta(minutes=15)
        past_bill = Bill(
            session_id=completed_session.id,
            subtotal=subtotal,
            tax_amount=tax,
            total_amount=total,
            status="PAID",
            created_at=bill_time,
            updated_at=past_end
        )
        db.add(past_bill)
        db.flush()

        for oi, iname, qty, uprice, oi_time in past_order_items:
            bi = BillItem(
                bill_id=past_bill.id,
                order_item_id=oi.id,
                item_name_snapshot=iname,
                quantity=qty,
                unit_price=uprice,
                created_at=bill_time
            )
            db.add(bi)

        pmt = Payment(
            bill_id=past_bill.id,
            amount=total,
            payment_method="CARD",
            status="COMPLETED",
            transaction_ref=f"TXN-CARD-{uuid.uuid4().hex[:8].upper()}",
            created_at=past_end,
            updated_at=past_end
        )
        db.add(pmt)

        db.commit()
        print("[SUCCESS] Database successfully re-seeded with unique, clean YYYY-MM-DD HH:MM:SS timestamps!")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Seeding error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    seed()
