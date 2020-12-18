"""
Name: Devika Naik
CS230: Section SN4
Data: McDonald's Data Set
URL: Link to your web application online (see extra credit)
Description: This program contains two queries. The first query returns the top 10 closet McDonald's locations to you
based on the address or zip code you entered. The second query shows a map of the United States and all McDonald's store
locations. The user can then select which store types they would like to display. They can choose to select one,
more or none.


Sources used:
Haversine Formula: https://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points
Interface formatting: https://discuss.streamlit.io/t/creating-a-nicely-formatted-search-field/1804/2
Streamlit code: https://www.youtube.com/watch?v=_9WiB2PDO7k
                https://docs.streamlit.io/_/downloads/en/latest/pdf/
"""

# Import necessary packages.
import streamlit as st
import pandas as pd
from PIL import Image
from geopy.geocoders import Nominatim
from math import radians, cos, sin, asin, sqrt
from operator import itemgetter

# Use streamlit to code in header, subheader, and title.
st.header("Devika Naik")
st.subheader("CS230: Final Project")
st.title("Find a McDonald's Near You\n")

# Insert an image of McDonald's.
img = Image.open("mcdonalds.jpg")
st.image(img, width=700)

# Include this line to increase the speed of the program by saving cache.
@st.cache

# Function to read data from the CSV file.
# Returns a dataframe of the data from the CSV file.
# Data frame is coded to set one of the columns as the dataframe's index.
# Columns X and Y are required to be renamed in order for geopy.geocoders to be able to access information on coordinates.
def read_data():
    file_name = "mcdonalds.csv"
    data = pd.read_csv(file_name)
    data.set_index('storeNumber', inplace=True)
    data = data.rename(columns={'X': 'longitude'})
    data = data.rename(columns={'Y': 'latitude'})
    return data

# Start of code for first query.
# Determine the corrdinates of the user based on address or zip code entered.
# Ultilizes geopy functionality.
# Returns value are the X and Y coordinates.
def get_coordinates(zip_code):
    geolocator = Nominatim(user_agent="United States")
    your_location = geolocator.geocode(zip_code)
    longitude = your_location.longitude
    latitude = your_location.latitude
    return longitude, latitude

# Calculate distances between users lat/long and all lat/long of McDonald's locations to get distances.
# Utiltizes the Haversine Formula in Python that determines the distance between two geopoints.
# Returns the distance between user's coordinates (from get_coordinates) and each McDonald's location listed in the CSV file.
def get_distances(lat1, long1, lat2, long2):
    lat1, long1, lat2, long2 = float(lat1), float(long1), float(lat2), float(long2)
    lat1, long1, lat2, long2 = map(radians, [lat1, long1, lat2, long2])
    dlon = long2 - long1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    km = 6371 * c
    return km

# Function that creates a dictionary of all store keys as the key and distance from user as the value.
# The dictionary is then sorted is ascending order and returns the top 10 closest stores.
def find_nearest(lat, long):
    distances = {}
    for index, row in read_data().iterrows():
        d = get_distances(row['latitude'], row['longitude'], lat, long)
        distances[index] = d
    n = 10
    top_10 = dict(sorted(distances.items(), key=itemgetter(1), reverse=False)[:n])
    return top_10

# Function that creates and displays the top 10 nearest stores to the user and contains only certain columns from the original dataset.
# Does not have a return value.
def display_nearest(top_10):
    nearest_stores = pd.DataFrame(columns=["Store Number", "Store Type", "Address", "City", "State", "Zip"])
    for store in top_10:
        info = read_data().loc[int(store)]
        store_type = info['storeType']
        address = info['address']
        city = info['city']
        state = info['state']
        zip = info['zip']
        nearest_stores = nearest_stores.append({"Store Number": store, "Store Type": store_type, "Address": address, "City": city,
                            "State": state, "Zip": zip}, ignore_index=True)
    nearest_stores = nearest_stores.set_index("Store Number")
    st.write(nearest_stores)

# User interface component asking user to enter their address or zipcode.
# If statement sets up case a where when the user has entered an input and presses the enter key on their keyboard the program returns an output.
zip_code = st.text_input("Please enter your address or zipcode: ")
if zip_code:
    long2, lat2 = get_coordinates(zip_code)
    top_10 = find_nearest(float(lat2), float(long2))
    display_nearest(top_10)

# Start of code for second query.
st.title("\nView Our Stores\n")

# Displays a world map with all the US McDonald's locations included in the CSV.
# User can select one or more store types and the map will automatically refresh to show the specific location types.
# The zoom of the map auto updates as well.
# If the user has no filters selected, the map will show all stores, else, it will show those selected.
stores = read_data()
types = stores['storeType'].unique()
type_choice = st.multiselect("Please select the store types you'd like to view: ", types)
if not type_choice:
    st.map(stores)
else:
    boolean_series = stores.storeType.isin(type_choice)
    filtered_stores = stores[boolean_series]
    st.map(filtered_stores)






