#Lost and found
#streamlit run "lost_and_found.py"
 
import streamlit as st
from datetime import date
from object import Item
import database as db # all the Supabase code is in database.py
 
# The data lives in Supabase, not in a local sqlite.db file,
# so it is not deleted when Streamlit Community Cloud reboots.
# Every row is a dictionary, so columns are read BY NAME (item["item_name"]),
# not by position (item[1]).
 
 
if "page" not in st.session_state:
    st.session_state.page = "login" # remembers which screen user should see
 
if "role" not in st.session_state: # Remembers the role
    st.session_state.role = ""
 
if "username" not in st.session_state:
    st.session_state.username = ""
 
def home_page():
 
    st.title("Welcome to Lincoln School's Lost and Found!")
 
    st.write("Select your role:")
 
    col1, col2, col3, col4, col5, col6 = st.columns(6)
 
# Select a role feature
 
    with col1:
        if st.button("Admin"):
            st.session_state.role = "Admin"
            st.write("Admin login selected")
 
    with col2:
        if st.button("Student"):
            st.session_state.role = "Student"
            st.write("Student login selected")
 
 
    if st.session_state.role == "":
        st.error("You must choose a role before logging in")
 
# Text inputs that allow you to write the username and password in
    elif st.session_state.role == "Admin":
        username = st.text_input("Username").strip()
        password = st.text_input("Password", type="password").strip()
 
# Login button
        if st.button("Login"):
            admin = []
            found = False
 
            try:
                with open("admin.txt", "r") as myfile:
 
                    for line in myfile:
                        admin.append(line.strip())
 
                    if f"{username},{password}" in admin: #The f lets you put variables inside of a string
                        found = True
                        st.success("Welcome Admin!")
                        st.session_state.page = "admin"
                        st.rerun() # refresh the app and use a new page
 
                if not found:
                    st.error("The username or password is incorrect")
 
            except FileNotFoundError:
                st.write ("I could not find that file")
 
    elif st.session_state.role == "Student":
 
        if st.button("Login"):
            st.success("Welcome Student!")
            st.session_state.page = "student"
            st.rerun()
 
 
def admin_page():
 
    if "show_form" not in st.session_state:
        st.session_state.show_form = False
 
    if "show_claims" not in st.session_state:
        st.session_state.show_claims = False
 
    if "confirm_close" not in st.session_state:
        st.session_state.confirm_close = None # id of the claim the admin is about to close
 
    st.header("Admin Dashbord")
 
    col1, col2 = st.columns(2)
 
    with col1:
        if st.button("Add lost item"):
            st.session_state.show_form = True
 
    with col2:
        if st.button("View Claim Requests"):
            st.session_state.show_claims = not st.session_state.show_claims # when i put True, claims appeared, but wouldn't go away
 
   # View all requests to claim an item
    if st.session_state.show_claims:
        st.subheader("Claim Requests")
 
        # Display success messages after the page reruns
        if "claim_message" in st.session_state:
            st.success(st.session_state["claim_message"])
            del st.session_state["claim_message"]
 
        claims = db.get_all_claims()
 
        if len(claims) == 0:
            st.write("No claim requests.")
 
        else:
            for claim in claims:
                claim_id = claim["id"]
                status = claim["status"]
                delivery = claim["delivery"]
 
                st.write(f"Item ID: {claim['item_id']}, Student: {claim['student_name']}, Claim Date: {claim['claim_date']}, Status: {status}, Delivery: {delivery}, Bus Number: {claim['bus_number']}")
 
                col1, col2, col3 = st.columns(3)
 
                # STEP 1: a new claim -> the admin accepts or rejects it
                if status == "Pending":
                    with col1:
                        if st.button("Accept", key=f"accept_{claim_id}"):
                            db.set_claim_status(claim_id, "Approved")
                            st.session_state["claim_message"] = "Claim approved! The student can now see it."
                            st.rerun()
 
                    with col2:
                        if st.button("Reject", key=f"reject_{claim_id}"):
                            db.set_claim_status(claim_id, "Rejected")
                            st.session_state["claim_message"] = "Claim rejected! The student can now see it."
                            st.rerun()
 
                # STEP 2: approved -> the ADMIN closes it once the item is picked up or sent on the bus.
                # The student does not need to press anything, so claims never get stuck.
                elif status in ("Approved", "Collected"):
                    if delivery == "Deliver home":
                        close_label = "Sent on bus"
                    else:
                        close_label = "Picked up"
 
                    with col1:
                        if st.button(close_label, key=f"close_{claim_id}"):
                            st.session_state.confirm_close = claim_id # ask for confirmation first
 
                    # Deleting can't be undone, so the admin has to confirm
                    if st.session_state.confirm_close == claim_id:
                        st.warning("This will delete the claim AND the item. Are you sure?")
                        yes_col, no_col = st.columns(2)
 
                        with yes_col:
                            if st.button("Yes, delete", key=f"yes_{claim_id}"):
                                db.close_claim(claim) # deletes the claim, the item and its photo
                                st.session_state.confirm_close = None
                                st.session_state["claim_message"] = "Item handed over. Claim and item deleted!"
                                st.rerun()
 
                        with no_col:
                            if st.button("Cancel", key=f"cancel_{claim_id}"):
                                st.session_state.confirm_close = None
                                st.rerun()
 
                # STEP 2 (rejected): delete the claim so other students can claim the item again
                elif status == "Rejected":
                    with col1:
                        if st.button("Delete Claim", key=f"delete_{claim_id}"):
                            db.delete_claim(claim_id)
                            st.session_state["claim_message"] = "Rejected claim deleted! The item can be claimed again."
                            st.rerun()
 
                st.divider()
 
 
    # Form required to add a new item
 
    if st.session_state.show_form == True:
 
        with st.form("add_item"):
            item_name = st.selectbox("Item Name",["Sweater", "Lunchbox", "Water Bottle", "Pencil Case", "Shirt", "Headphones", "Other"])
 
            category = st.selectbox("Category",["Clothing", "Electronics", "School Supplies", "Food and Drink", "Personal Items", "Other"])
            brand = st.text_input("Brand")
            color = st.selectbox("Color",["Red", "Orange", "Yellow", "Green", "Blue", "Purple", "Brown", "Black", "White", "Gray"])
 
            location_found = st.selectbox("Location",["Cafeteria","Central Plaza", "Buses", "Gym", "High School Building", "Middle School Building", "Elementary Building", "Preschool Building"])
            date_found = st.date_input("Date found")
            image = st.file_uploader("Image", type=["png", "jpg", "jpeg"])
 
            submitted = st.form_submit_button("Add Item")
 
        if submitted:
 
            # Check whether an image was uploaded
            if image is None:
                st.error(
                    "Error: Please upload an image before adding the item.")
 
            else:
                new_item = Item( item_name, category, brand.strip(), color, location_found, date_found, image)
 
                # Save the photo in Supabase Storage, then the item (with the photo's file name) in the database
                try:
                    image_path = db.upload_image(image)
                except Exception as error:
                    st.error(f"The photo could not be uploaded: {error}")
                    st.stop()
 
                db.add_item(new_item, image_path)
 
                st.session_state.show_form = False
                st.success("Item added successfully!")
                st.rerun()
 
 
 
    # Search and display uploaded lost items
    st.subheader("Uploaded Lost Items")
 
    # Search by Item ID
    search_id = st.text_input(
        "Search by Item ID",
        placeholder="Enter the Item ID..."
    )
 
    if search_id:
        if search_id.isdigit():
            found_item = db.get_item(int(search_id))
 
            if found_item:
                lost_items = [found_item]
            else:
                lost_items = []
                st.warning("No item found with that ID.")
        else:
            st.warning("Please enter a valid numeric Item ID.")
            lost_items = []
    else:
        lost_items = db.get_all_items()
 
    # Display the matching items
    if not lost_items:
        if not search_id:
            st.write("No items are uploaded yet.")
    else:
        for item in lost_items:
            st.write(f"ID: {item['id']}, Name: {item['item_name']}, Category: {item['category']}, Brand: {item['brand']}, Color: {item['color']}, Location: {item['location_found']}, Date: {item['date_found']}")
 
            # Delete item if it has no claim requests
            if st.button("Delete", key=f"delete_item_{item['id']}"):
 
                if db.get_claim_for_item(item["id"]):
                    st.warning("This item cannot be deleted because it has claim requests.")
                else:
                    db.delete_item(item) # deletes the item and its photo
 
                    st.success("Item deleted!")
                    st.rerun()
 
 
def student_page():
 
    lost_items = db.get_all_items()
 
    # Look up item names by id (used in "My Claim Requests")
    item_names = {}
    for item in lost_items:
        item_names[item["id"]] = item["item_name"]
 
# Students' lost items take up more space so, for convencience, I will put their claims at the top
    if "show_my_claims" not in st.session_state:
        st.session_state.show_my_claims = False
 
    if st.button("View My Claims"):
        st.session_state.show_my_claims = not st.session_state.show_my_claims # True does not work form some reason
 
    if st.session_state.show_my_claims:
        st.subheader("My Claim Requests")
 
        student_name_search = st.text_input("Enter your name to view your claims:")
 
        if student_name_search.strip():
            # ignores capitals and extra spaces, so "Ana" and "ana " both match
            claims = db.get_claims_for_student(student_name_search)
 
            # Display the approved or denied claim
            if len(claims) == 0:
                st.write("No active claims found for that name. Items that were already picked up or sent home no longer appear here.")
 
            else:
                for claim in claims:
                    item_name = item_names.get(claim["item_id"], "Deleted item")
 
                    if claim["status"] == "Approved":
                        # The message depends on how the student chose to receive the item
                        if claim["delivery"] == "Deliver home":
                            st.success(f"Your claim for {item_name} has been approved! It will be sent home on bus {claim['bus_number']}.")
                        else:
                            st.success(f"Your claim for {item_name} has been approved! Please collect it from the Lost and Found at 2:30pm.")
                    elif claim["status"] == "Rejected":
                        st.error(f"Your claim for {item_name} has been rejected. Please contact security for more information")
                    elif claim["status"] == "Collected":
                        st.success("You have collected your item")
                    else:
                        st.info(f"Your request for {item_name} is still pending")
 
        st.divider()
# Add a filter. Make it easier for people to find the lost items
 
    st.subheader("Search")
    # linear search algorithm
    search_field = st.selectbox("Search by", ["Name","Category", "Brand", "Color", "Location"])
 
    st.divider()
    st.text("Item names available: Sweater, Lunchbox, Water Bottle, Pencil Case, Shirt, Headphones, Other")
    st.text("Categories available: Clothing, Electronics, School Supplies, Food and Drink, Personal Items, Other")
    st.text("Colors available: Red, Orange, Yellow, Green, Blue, Purple, Brown, Black, White, Gray")
    st.text("Locations availables: Cafeteria,Central Plaza, Buses, Gym, High School Building, Middle School Building, Elementary Building, Preschool Building")
    st.divider()
 
    search_text = st.text_input("Enter what you are looking for (e.g. red):")
 
 
    filtered_items = []
    if search_text == "":
        filtered_items = lost_items
    else:
        for item in lost_items:
            if search_field == "Name":
                value = item["item_name"]
            elif search_field == "Category":
                value = item["category"]
            elif search_field == "Brand":
                value = item["brand"]
            elif search_field == "Color":
                value = item["color"]
            else:
                value = item["location_found"]
 
            if value and search_text.lower() in value.lower():
                filtered_items.append(item)
 
 
# View the lost items
 
    if len(lost_items) == 0:
        st.write("No lost items have been uploaded yet.")
    elif len(filtered_items) == 0:
        st.write("No items match your search.")
 
    for item in filtered_items:
        item_id = item["id"]
        col1, col2 = st.columns(2)
 
        with col1:
            if item["image_path"]:
                image_bytes = db.get_image(item["image_path"])
                try:
                    st.image(image_bytes, width = 300)
                except Exception:
                    # a missing or broken photo should not crash the whole page
                    st.caption("Photo could not be loaded")
 
        with col2:
            st.write(f"{item['item_name']}")
            st.write(f"Category: {item['category']}")
            st.write(f"Brand: {item['brand']}")
            st.write(f"Color: {item['color']}")
            st.write(f"Location found: {item['location_found']}")
            st.write(f"Date found: {item['date_found']}")
 
       #Claim button
 
        if st.button("Claim", key = f"claim_{item_id}"): #the key will prevent issues if there are duplicates
 
            if db.get_claim_for_item(item_id):
                st.warning("this item has already been claimed.")
 
            else:
                st.session_state.claiming_item = item_id
 
        if st.session_state.get("claiming_item") == item_id:
            student_name = st.text_input("Write your name:", key=f"name_{item_id}")
            delivery = st.selectbox("how would you like to reciebe the item?", ["Collect at the Lost and Found", "Deliver home"], key=f"delivery_{item_id}")
 
            bus_number = ""
 
            if delivery == "Deliver home":
                bus_number = st.text_input("Bus number", key=f"bus_{item_id}")
 
            if st.button("Submit Claim", key=f"submit_{item_id}"):
 
                if student_name.strip() == "":
                    st.error("Please enter your name")
 
                elif delivery == "Deliver home" and bus_number.strip() == "":
                    st.error("Please enter your bus number.")
 
                else:
                    if delivery == "Deliver home":
                        bus = bus_number.strip()
                    else:
                        bus = None
 
                    db.add_claim(item_id, student_name.strip(), str(date.today()), delivery, bus)
 
                    st.success("Claim submitted!")
                    st.session_state.claiming_item = None
                    st.rerun()
 
 
        st.divider() # Draw a horizontal line across the page, separate the objects
 
 
 
if st.session_state.page == "login":
    home_page()
 
elif st.session_state.page == "admin":
    admin_page()
 
elif st.session_state.page == "student":
    student_page()
