import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Database connection
conn = sqlite3.connect('carpooling.db')
c = conn.cursor()

print("Stage 1 : Database Connection")


# Database initialization
def init_db():
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, contact TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS carpools (ride_id INTEGER PRIMARY KEY, driver_id INTEGER, departure TEXT, 
                 destination TEXT, date TEXT, time TEXT, seats INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS bookings (booking_id INTEGER PRIMARY KEY, user_id INTEGER, ride_id INTEGER, status TEXT)''')
    conn.commit()

# User registration
def register_user(username, contact):
    c.execute('INSERT INTO users (username, contact) VALUES (?, ?)', (username, contact))
    conn.commit()

# Creating a carpool
def create_carpool(driver_id, departure, destination, date, time, seats):
    c.execute('''INSERT INTO carpools (driver_id, departure, destination, date, time, seats) 
                 VALUES (?, ?, ?, ?, ?, ?)''', (driver_id, departure, destination, date, time, seats))
    conn.commit()

# Search available carpools
def search_carpools(departure, destination, date):
    c.execute('''SELECT * FROM carpools WHERE departure=? AND destination=? AND date=?''', 
              (departure, destination, date))
    return c.fetchall()

# Booking a seat
def book_seat(user_id, ride_id):
    c.execute('INSERT INTO bookings (user_id, ride_id, status) VALUES (?, ?, ?)', (user_id, ride_id, 'pending'))
    conn.commit()


# Delete Carpool
def delete_carpool(ride_id):
    c.execute('DELETE FROM carpools WHERE ride_id = ?', (ride_id,))
    conn.commit()


# Streamlit app
st.title("Carpooling App")

# Initializing database
init_db()

# Registration and Login
st.sidebar.title("User Registration")
username = st.sidebar.text_input("Enter username")
contact = st.sidebar.text_input("Enter contact")
if st.sidebar.button("Register"):
    register_user(username, contact)
    st.sidebar.success("Registered successfully!")

# Creating a carpool
st.header("Create a Carpool")
driver_id = st.number_input("Your user ID", min_value=1)
departure = st.text_input("Departure location")
destination = st.text_input("Destination location")
date = st.date_input("Date")
time = st.time_input("Time")
seats = st.number_input("Available seats", min_value=1)

if st.button("Create Carpool"):
    create_carpool(driver_id, departure, destination, date.strftime('%Y-%m-%d'), time.strftime('%H:%M'), seats)
    st.success("Carpool created!")

# Searching for a carpool
st.header("Search for Carpools")
search_departure = st.text_input("Search by Departure")
search_destination = st.text_input("Search by Destination")
search_date = st.date_input("Date for Search")

if st.button("Search Carpools"):
    results = search_carpools(search_departure, search_destination, search_date.strftime('%Y-%m-%d'))
    st.write(pd.DataFrame(results, columns=['Ride ID', 'Driver ID', 'Departure', 'Destination', 'Date', 'Time', 'Seats']))

# Booking a seat
st.header("Book a Seat")
user_id = st.number_input("Your user ID for booking", min_value=1)
ride_id = st.number_input("Ride ID to book", min_value=1)

if st.button("Book Seat"):
    book_seat(user_id, ride_id)
    st.success("Booking requested. Waiting for driver approval.")

# Function to retrieve all carpools from the database
def get_all_carpools():
    # c.execute("SELECT * FROM carpools")
    c.execute('''
        SELECT carpools.ride_id,users.id AS Driver_ID, users.username AS driver_name, carpools.departure, 
               carpools.destination, carpools.date, carpools.time, carpools.seats 
        FROM carpools
        JOIN users ON carpools.driver_id = users.id
    ''')

    return c.fetchall()

col1,col2,col3 = st.columns([5,1,1])

with col1:
    # Display the contents of the carpools table
    st.header("All Carpools")
    carpools_data = get_all_carpools()
    # Convert data to DataFrame for better display in Streamlit
    carpools_df = pd.DataFrame(carpools_data, columns=['Ride ID', 'Driver ID','Driver Name', 'Departure', 'Destination', 'Date', 'Time', 'Seats'])
    st.dataframe(carpools_df)

with col2:
    # Delete Carpool
    st.subheader("Delete Carpool")
    ride_id_to_delete = st.number_input("Ride ID to delete", min_value=1, step=1)
    if st.button("Delete Carpool"):
        delete_carpool(ride_id_to_delete)
        st.success("Carpool deleted successfully!")


def get_all_users():
    c.execute("SELECT * FROM users")
    return c.fetchall()

# Display the contents of the carpools table
st.header("All Users")
users_data = get_all_users()
# Convert data to DataFrame for better display in Streamlit
users_df = pd.DataFrame(users_data, columns=['User ID', 'User Name', 'Mobile Number'])
# users_df = pd.DataFrame(users_data)
st.dataframe(users_df)    

