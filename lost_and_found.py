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
    else:
        username = st.text_input("Username").strip()
        password = st.text_input("Password", type="password").strip() # type = "password" hides the characters that the user types 

# Login button
    if st.button("Login"):

        admin = []
        student = []
        found = False 

# Usernames and passwords will be administered by technology, how lincoln does with Microsoft. Therefore, these can be written in a seperate file the webpage can read from 
        if st.session_state.role == "Admin":
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

        if st.session_state.role == "Student":
            try:
                with open("student.txt", "r") as myfile:

                    for line in myfile:
                        student.append(line.strip())

                    if f"{username},{password}" in student: #The f lets you put variables inside of a string 
                        found = True
                        st.session_state.username = username 
                        st.success("Welcome Student!")
                        st.session_state.page = "student"
                        st.rerun()

                if not found: 
                    st.error("The username or password is incorrect")

            except FileNotFoundError:
                st.write ("I could not find that file") 
            except Exception: 
                st.write("Another error occured")

def admin_page():

    if "show_form" not in st.session_state:
        st.session_state.show_form = False 

    if "show_claims" not in st.session_state:
        st.session_state.show_claims = False

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

        cursor.execute("SELECT * FROM claims")
        claims = cursor.fetchall()

        if len(claims) == 0:
            st.write("No claim requests.")

        else:
            for claim in claims:
                st.write(f"Item ID: {claim[0]}, Student: {claim[1]}, Claim Date: {claim[2]}, Status: {claim[3]}")

                col1, col2,col3 = st.columns(3)

        # Accept or deny a claim 
                with col1:
                    if st.button("Accept", key = "accept" + str(claim[0])): # line 83 "Computer Science IA", THere i got the help to fix this error 
                        cursor.execute("UPDATE claims SET status = 'Approved' WHERE item_id = ?", (claim[0],))
                        connect.commit()
                        st.success("Claim approved!")
                        st.rerun()

                with col2: 
                    if st.button("Reject", key = "reject" + str(claim[0])):
                        cursor.execute("UPDATE claims SET status = 'Rejected' WHERE item_id = ?", (claim[0],))
                        connect.commit()
                        st.success("Claim rejected")
                        st.rerun()

                with col3:
                    if claim[3] == "Collected" or "Rejected":
                        if st.button("Delete Claim", key=f"delete_{claim[0]}"):
                            cursor.execute("DELETE FROM claims WHERE item_id = ?", (claim[0],))
                            connect.commit()
                            st.success("Claim deleated!")
                            st.rerun()

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
            new_item = Item(item_name, category, brand, color, location_found, date_found, image)
            # save the picture in SQLite 
            if image:
                image_data = image.getvalue()
            else:
                image_data = None 
            
            # Conncect to the sqlite.db

            cursor.execute("""INSERT INTO lost_items (item_name, category, brand, color, location_found, date_found, image) VALUES (?, ?, ?, ?, ?, ?, ?) """, (new_item.item_name, new_item.category,new_item.brand,new_item.color, new_item.location_found, str(new_item.date_found),image_data)) #the ? are placeholders 
            connect.commit() #Save 

            st.success("Item added!")
            
            st.session_state.show_form = False # works as long as streamlit is running, if it is not, it wont save the information
            st.rerun() #refresh the webpage.

    st.subheader("Uploaded Lost Items")

    cursor.execute("SELECT * FROM lost_items")
    lost_items = cursor.fetchall() # retrieve all of the objects 
    # This returns a lits of tuples 

    if len(lost_items) == 0:
        st.write("No items are uploaded yet")

    else: 
    # Add the new item and the new item 
        for item in lost_items:
            st.write(f" Id: {item[0]}, Name: {item[1]}, Category: {item[2]}, Brand: {item[3]}, Color: {item[4]}, Location: {item[5]}, Date: {item[6]}")

    # Delete an object if necessary 
            if st.button("Delete", key = item[0]):

                cursor.execute("SELECT * FROM claims WHERE item_id = ?", (item[0],))
    
    # Check if there are any exsisting claim requests

                exsisting_claim = cursor.fetchone() 
                if exsisting_claim:
                    st.warning("This item cannot be deleted because it has claim requests")

                else: 
                    cursor.execute("DELETE FROM lost_items WHERE id = ?", (item[0],))
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

        cursor.execute( "SELECT * FROM claims WHERE student_username = ?", (st.session_state.username,))
        claims = cursor.fetchall()  

        # Display the approved or denired claim
        if len(claims) == 0:
            st.write("You have not submitted any claims")

        else:
            for claim in claims:
                cursor.execute("SELECT item_name FROM lost_items WHERE id = ?", (claim[0],))
                item = cursor.fetchone()

                if item:
                    item_name = item[0] 
                else: 
                    item_name = "Deleted item"

                if claim[3] == "Approved":
                    st.success(f" Your claim for {item_name} has been approved! Please collect it form the Lost and Found at 2:30pm")
                    if st.button("Got it!", key=f"got_it_{claim[0]}"):
                        cursor.execute("UPDATE claims SET status = 'Collected' WHERE item_id = ?", (claim[0],) )
                        connect.commit()
                        st.success("Item was collected")
                        st.rerun()
                elif claim[3] == "Rejected":
                    st.error(f"Your claim for {item_name} has been rejected. Please contact security for more information")
                elif claim[3] == "Collected":
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
                cursor.execute("""INSERT INTO claims(item_id, student_username, claim_date, status) VALUES (?, ?, ?, ?)""", (item[0], st.session_state.username, str(date.today()), "Pending"))
                connect.commit()
                st.success("Claim submitted!")

    st.divider() # Draw a horizontal line across the page, separate the objects
 


if st.session_state.page == "login":
    home_page()

elif st.session_state.page == "admin":
    st.write("Going to admin page")
    admin_page()

elif st.session_state.page == "student":
    student_page()

# My internet is slow 
#Next time you open this, delete the object you already created and add a new one 
# see if this fixes the bug, it is not creating the id. 
# I assume it is because the object was created before I implemented that feature


# My head hurts.
# Next time you open this, attempt to debug the student's claim button, for some reason this isnt appearing on the screen 
# I suspect the admin's acceptance or denial isnt being saved. 
# I want to make this "View your claim " button like the admin's one. where they can see everyone's claims, accept or deny them 
# However, when students press their button, it will tell them whether it is accepted or denied. If acepted, it must tell them where to find it. 

