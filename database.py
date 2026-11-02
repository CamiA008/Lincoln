# database.py
# Everything that talks to the Supabase database lives in this file.
# lost_and_found.py only imports these functions, so the page code never
# needs to know how the data is stored.
#
# Every row comes back as a dictionary, so columns are read BY NAME,
# e.g. claim["status"], never by position like claim[4].

### This was doen with the help of claude 
 
import streamlit as st
from supabase import create_client
from pathlib import Path
import uuid
 
IMAGE_BUCKET = "item-images"  # Supabase Storage bucket where photos are saved
 
 
# ---------------- CONNECTION ----------------
# The URL and key are read from Streamlit's Secrets, never written in the code.
@st.cache_resource  # create the connection once and reuse it, instead of on every click
def get_supabase():
    # .strip() removes accidental spaces or line breaks from copying the values
    return create_client(st.secrets["SUPABASE_URL"].strip(), st.secrets["SUPABASE_KEY"].strip())
 
 
supabase = get_supabase()
 
 
 
# ---------------- LOST ITEMS ----------------
def get_all_items():
    # Returns a list of dictionaries, e.g. {"id": 1, "item_name": "Sweater", ...}
    return supabase.table("lost_items").select("*").order("id").execute().data
 
 
def get_item(item_id):
    rows = supabase.table("lost_items").select("*").eq("id", item_id).execute().data
    if len(rows) > 0:
        return rows[0]
    return None
 
 
def add_item(item, image_path):
    # item is an Item object (from object.py)
    supabase.table("lost_items").insert({
        "item_name": item.item_name,
        "category": item.category,
        "brand": item.brand,
        "color": item.color,
        "location_found": item.location_found,
        "date_found": str(item.date_found),
        "image_path": image_path,
    }).execute()
 
 
def delete_item(item):
    # Delete the photo too, so storage doesn't fill up with unused images
    if item["image_path"]:
        try:
            supabase.storage.from_(IMAGE_BUCKET).remove([item["image_path"]])
        except Exception:
            pass  # if the photo is already gone, still delete the item
 
    supabase.table("lost_items").delete().eq("id", item["id"]).execute()
 
 
# ---------------- PHOTOS ----------------
def upload_image(uploaded_file):
    # Saves the photo in Supabase Storage and returns its file name.
    # Raises an error if the upload fails.
    extension = Path(uploaded_file.name).suffix.lower()
    image_path = f"{uuid.uuid4()}{extension}"  # random unique file name
    supabase.storage.from_(IMAGE_BUCKET).upload(image_path, uploaded_file.getvalue())
    return image_path
 
 
def delete_image(image_path):
    try:
        supabase.storage.from_(IMAGE_BUCKET).remove([image_path])
    except Exception:
        pass  # if the photo is already gone, nothing to do
 
 
@st.cache_data(ttl=3600)  # remember downloaded photos for 1 hour so the page loads faster
def get_image(image_path):
    # Downloads the photo from Supabase Storage and returns its bytes
    try:
        return supabase.storage.from_(IMAGE_BUCKET).download(image_path)
    except Exception:
        return None
 
 
# ---------------- CLAIMS ----------------
def get_all_claims():
    return supabase.table("claims").select("*").order("id").execute().data
 
 
def get_claims_for_student(student_name):
    # Linear search that ignores capitals and extra spaces, so "Ana" and "ana " both match
    wanted = student_name.strip().lower()
    result = []
    for claim in get_all_claims():
        if (claim["student_name"] or "").strip().lower() == wanted:
            result.append(claim)
    return result
 
 
def get_claim_for_item(item_id):
    rows = supabase.table("claims").select("*").eq("item_id", item_id).execute().data
    if len(rows) > 0:
        return rows[0]
    return None
 
 
def add_claim(item_id, student_name, claim_date, delivery, bus_number):
    supabase.table("claims").insert({
        "item_id": item_id,
        "student_name": student_name,
        "claim_date": claim_date,
        "status": "Pending",
        "delivery": delivery,
        "bus_number": bus_number,
    }).execute()
 
 
def set_claim_status(claim_id, status):
    supabase.table("claims").update({"status": status}).eq("id", claim_id).execute()
 
 
def delete_claim(claim_id):
    supabase.table("claims").delete().eq("id", claim_id).execute()
 
 
def close_claim(claim):
    # The item was picked up or sent on the bus:
    # delete the claim FIRST (it points to the item), then the item and its photo
    delete_claim(claim["id"])
    item = get_item(claim["item_id"])
    if item:
        delete_item(item)
