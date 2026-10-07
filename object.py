
import streamlit as st
from datetime import date 

class Item:
    def __init__(self, item_name, category, brand, color, location_found, date_found, image):
        self.item_name = item_name
        self.category = category
        self.brand = brand
        self.color = color
        self.location_found = location_found
        self.date_found = date_found
        self.image = image


        