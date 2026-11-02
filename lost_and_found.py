#Lost and found
#streamlit run "lost_and_found.py"
 
import streamlit as st
from datetime import date
from object import Item
import sqlite3
 
#Connect to the database
 
connect = sqlite3.connect("sqlite.db", check_same_thread = False)
cursor = connect.cursor()
 
 
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
            except Exception:
                st.write("Another error occured")
 
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
            st.session_state.show_form = True # Creates an empty lsit only if it doesnt exsist.
 
    with col2:
        if st.button("View Claim Requests"):
            st.session_state.show_claims = not st.session_state.show_claims # when i put True, claims appeared, but wouldn't go away
 
   # View all requests to claim an item
    if st.session_state.show_claims:
        st.subheader("Claim Requests")
 
        # Display success messages after the page reruns
        # (moved out of the loop so it only appears once)
        if "claim_message" in st.session_state:
            st.success(st.session_state["claim_message"])
            del st.session_state["claim_message"]
 
        cursor.execute("SELECT * FROM claims")
        claims = cursor.fetchall()
 
        if len(claims) == 0:
            st.write("No claim requests.")
 
        else:
            for claim in claims:
                # claim = (id, item_id, student_name, claim_date, status, delivery, bus_number)
                claim_id = claim[0]
                item_id = claim[1]
                status = claim[4]
                delivery = claim[5]
 
                st.write(f"Item ID: {item_id}, Student: {claim[2]}, "f"Claim Date: {claim[3]}, Status: {status}, "f"Delivery: {delivery}, Bus Number: {claim[6]}")
 
                col1, col2, col3 = st.columns(3)
 
                # STEP 1: a new claim -> the admin accepts or rejects it
                if status == "Pending":
                    with col1:
                        if st.button("Accept", key=f"accept_{claim_id}"):
                            cursor.execute("UPDATE claims SET status = ? WHERE id = ?", ("Approved", claim_id))
                            connect.commit()
                            st.session_state["claim_message"] = "Claim approved! The student can now see it."
                            st.rerun()
 
                    with col2:
                        if st.button("Reject", key=f"reject_{claim_id}"):
                            cursor.execute("UPDATE claims SET status = ? WHERE id = ?", ("Rejected", claim_id))
                            connect.commit()
                            st.session_state["claim_message"] = "Claim rejected! The student can now see it."
                            st.rerun()
 
                # STEP 2: approved -> the ADMIN closes it once the item is picked up or sent on the bus.
                # The student does not need to press anything, so claims never get stuck.
                # ("Collected" is included for old claims where a student pressed the old "Got it!" button)
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
                                cursor.execute("DELETE FROM claims WHERE id = ?", (claim_id,))
                                cursor.execute("DELETE FROM lost_items WHERE id = ?", (item_id,))
                                connect.commit()
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
                            cursor.execute("DELETE FROM claims WHERE id = ?", (claim_id,))
                            connect.commit()
                            st.session_state["claim_message"] = "Rejected claim deleted! The item can be claimed again."
                            st.rerun()
 
                st.divider()
 
 
    # Form required to add a new item
 
    if st.session_state.show_form == True:
 
        with st.form("add_item"):
            item_name = st.selectbox("Item Name",["Sweater", "Lunchbox"," Water Bottle", "Pencil Case", "Shirt", "Headphones", "Other"])
 
            category = st.selectbox("Category",["Clothing", "Electronics", "School Supplies", "Food and Drink", "Personal Items", "Other"])
            brand = st.text_input("Brand")
            color = st.selectbox("Color",["Red", "Orange", "Yellow", "Green", "Blue", "Purple", "Brown", "Black", "White", "Gray"])
 
            location_found = st.selectbox("Location",["Cafeteria","Central Plaza", "Buses", "Gym", "High School Building", "Middle School Building", "Elementary Building", "Preschool Building"])
            date_found = st.date_input("Date found")
            image = st.file_uploader("Image")
 
            submitted = st.form_submit_button("Add Item")
 
        if submitted:
 
            # Check whether an image was uploaded
            if image is None:
                st.error(
                    "Error: Please upload an image before adding the item.")
 
            else:
                new_item = Item( item_name, category, brand, color, location_found, date_found, image)
 
                # Get the uploaded image data
                image_data = image.getvalue()
 
                # Save the item in the database
                cursor.execute(
                    """
                    INSERT INTO lost_items (item_name, category, brand, color, location_found, date_found, image) VALUES (?, ?, ?, ?, ?, ?, ?) """, (new_item.item_name, new_item.category, new_item.brand, new_item.color, new_item.location_found, str(new_item.date_found), image_data))
 
                connect.commit()
 
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
            cursor.execute(
                "SELECT * FROM lost_items WHERE id = ?",
                (int(search_id),)
            )
            lost_items = cursor.fetchall()
 
            if not lost_items:
                st.warning("No item found with that ID.")
        else:
            st.warning("Please enter a valid numeric Item ID.")
            lost_items = []
    else:
        cursor.execute("SELECT * FROM lost_items")
        lost_items = cursor.fetchall()
 
    # Display the matching items
    if not lost_items:
        if not search_id:
            st.write("No items are uploaded yet.")
    else:
        for item in lost_items:
            st.write(f"ID: {item[0]}, "f"Name: {item[1]}, "f"Category: {item[2]}, "f"Brand: {item[3]}, "f"Color: {item[4]}, "f"Location: {item[5]}, "f"Date: {item[6]}")
 
            # Delete item if it has no claim requests
            if st.button("Delete", key=f"delete_item_{item[0]}"):
                cursor.execute(
                    "SELECT * FROM claims WHERE item_id = ?",
                    (item[0],))
 
                existing_claim = cursor.fetchone()
 
                if existing_claim:
                    st.warning("This item cannot be deleted because ""it has claim requests.")
                else:
                    cursor.execute("DELETE FROM lost_items WHERE id = ?",(item[0],))
                    connect.commit()
 
                    st.success("Item deleted!")
                    st.rerun()
 
 
def student_page():
 
    cursor.execute("SELECT * FROM lost_items")
    lost_items = cursor.fetchall()
 
# Students' lost items take up more space so, for convencience, I will put their claims at the top
    if "show_my_claims" not in st.session_state:
        st.session_state.show_my_claims = False
 
    if st.button("View My Claims"):
        st.session_state.show_my_claims = not st.session_state.show_my_claims # True does not work form some reason
 
    if st.session_state.show_my_claims:
        st.subheader("My Claim Requests")
 
        # (moved inside the "if" so it only shows after pressing "View My Claims")
        student_name_search = st.text_input("Enter your name to view your claims:")
 
        if student_name_search.strip():
            # LOWER and TRIM ignore capitals and extra spaces, so "Ana" and "ana " both match
            cursor.execute(
                "SELECT * FROM claims WHERE LOWER(TRIM(student_name)) = LOWER(TRIM(?))", (student_name_search,))
            claims = cursor.fetchall()
 
            # Display the approved or denired claim
            if len(claims) == 0:
                st.write("No active claims found for that name. Items that were already picked up or sent home no longer appear here.")
 
            else:
                for claim in claims:
                    # claim = (id, item_id, student_name, claim_date, status, delivery, bus_number)
                    cursor.execute("SELECT item_name FROM lost_items WHERE id = ?", (claim[1],))
                    item = cursor.fetchone()
 
                    if item:
                        item_name = item[0]
                    else:
                        item_name = "Deleted item"
 
                    if claim[4] == "Approved":
                        # The message depends on how the student chose to receive the item.
                        # No "Got it!" button anymore: the admin closes the claim instead.
                        if claim[5] == "Deliver home":
                            st.success(f"Your claim for {item_name} has been approved! It will be sent home on bus {claim[6]}.")
                        else:
                            st.success(f"Your claim for {item_name} has been approved! Please collect it from the Lost and Found at 2:30pm.")
                    elif claim[4] == "Rejected":
                        st.error(f"Your claim for {item_name} has been rejected. Please contact security for more information")
                    elif claim[4] == "Collected":
                        st.success("You have collected your item")
                    else:
                        st.info(f"Your request for {item_name} is still pending") #it is nither an error not success, but i want it to have a condition. im not sure if this makes sense
 
 
 
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
                value = item[1]
            elif search_field == "Category":
                value = item[2]
            elif search_field == "Brand":
                value = item[3]
            elif search_field == "Color":
                value = item[4]
            else:
                value = item[5]
 
            if value and search_text.lower() in value.lower():
                filtered_items.append(item)
 
 
# View the lost items
 
    if len(filtered_items) == 0:
        st.write("No lost items have been uploaded yet.")
 
    for item in filtered_items:
        col1, col2 = st.columns(2)
 
        with col1:
            if item[7]:
                st.image(item[7], width = 300)
 
        with col2:
            st.write(f"{item[1]}")
            st.write(f"Category: {item[2]}")
            st.write(f"Brand: {item[3]}")
            st.write(f" Color: {item[4]}")
            st.write(f" Location found: {item [5]}")
            st.write(f" Date found: {item[6]}")
 
       #Claim button
 
        if st.button("Claim", key = item[0]): #the key will prevent issues if there are duplicates
 
            cursor.execute("SELECT * FROM claims WHERE item_id = ?", (item[0],))
            existing_claim = cursor.fetchone() # unlike fetchall that retrieves everything, fetchone retries one row
 
            if existing_claim:
                st.warning("this item has already been claimed.")
 
            else:
                st.session_state.claiming_item = item[0]
 
        if st.session_state.get("claiming_item") == item[0]:
            student_name = st.text_input("Write your name:",  key=f"name_{item[0]}")
            delivery = st.selectbox("how would you like to reciebe the item?", ["Collect at the Lost and Found", "Deliver home"],key=f"delivery_{item[0]}")
 
            bus_number = ""
 
            if delivery == "Deliver home":
                bus_number = st.text_input("Bus number", key=f"bus_{item[0]}")
 
            if st.button("Submit Claim", key=f"submit_{item[0]}"):
 
                if student_name.strip() == "":
                    st.error("Please enter your name") # st.error does not accept a key, it caused a crash
 
                elif delivery == "Deliver home" and bus_number.strip() == "":
                    st.error("Please enter your bus number.")
 
                else:
                    cursor.execute("""INSERT INTO CLAIMS (item_id, student_name, claim_date, status, delivery, bus_number) VALUES (?, ?, ?, ?, ?, ?) """, ( item[0], student_name.strip(), str(date.today()), "Pending", delivery, bus_number.strip() if delivery == "Deliver home" else None ))
 
                    connect.commit()
                    st.success("Claim submitted!")
                    st.session_state.claiming_item = None
                    st.rerun()
 
 
    st.divider() # Draw a horizontal line across the page, separate the objects
 
 
 
if st.session_state.page == "login":
    home_page()
 
elif st.session_state.page == "admin":
    st.write("Going to admin page")
    admin_page()
 
elif st.session_state.page == "student":
    student_page()
