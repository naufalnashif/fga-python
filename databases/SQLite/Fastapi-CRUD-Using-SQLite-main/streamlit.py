import streamlit as st
import requests
import json

# Base URL of your FastAPI app
BASE_URL = "http://localhost:8000"

# Helper function to fetch all tracks
def get_tracks():
    response = requests.get(f"{BASE_URL}/tracks")
    if response.status_code == 200:
        return response.json()
    return []

# Helper function to fetch a single track by ID
def get_track_by_id(track_id):
    response = requests.get(f"{BASE_URL}/tracks/{track_id}")
    if response.status_code == 200:
        return response.json()
    return None

# Helper function to create a new track
def create_track(track_data):
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/tracks", data=json.dumps(track_data), headers=headers)
    return response.status_code

# Helper function to update a track
def update_track(track_id, track_data):
    headers = {'Content-Type': 'application/json'}
    response = requests.put(f"{BASE_URL}/tracks/{track_id}", data=json.dumps(track_data), headers=headers)
    return response.status_code

# Helper function to delete a track
def delete_track(track_id):
    response = requests.delete(f"{BASE_URL}/tracks/{track_id}")
    return response.status_code

# Streamlit UI
st.title("Track Management")

st.sidebar.title("Options")
option = st.sidebar.selectbox("Choose an action", ["View Tracks", "Add Track", "Update Track", "Delete Track"])

if option == "View Tracks":
    st.header("All Tracks")
    tracks = get_tracks()
    if tracks:
        st.write(tracks)
    else:
        st.write("No tracks found")

elif option == "Add Track":
    st.header("Add a New Track")
    name = st.text_input("Track Name")
    artist = st.text_input("Artist Name")
    album = st.text_input("Album Name")
    genre = st.text_input("Genre")
    length = st.number_input("Length (in seconds)", min_value=0)
    
    if st.button("Add Track"):
        track_data = {
            "name": name,
            "artist": artist,
            "album": album,
            "genre": genre,
            "length": length
        }
        status_code = create_track(track_data)
        if status_code == 201:
            st.success("Track added successfully")
        else:
            st.error("Failed to add track")

elif option == "Update Track":
    st.header("Update an Existing Track")
    track_id = st.number_input("Track ID", min_value=1, step=1)
    track = get_track_by_id(track_id)
    
    if track:
        name = st.text_input("Track Name", value=track['name'])
        artist = st.text_input("Artist Name", value=track['artist'])
        album = st.text_input("Album Name", value=track['album'])
        genre = st.text_input("Genre", value=track['genre'])
        length = st.number_input("Length (in seconds)", min_value=0, value=track['length'])
        
        if st.button("Update Track"):
            track_data = {
                "name": name,
                "artist": artist,
                "album": album,
                "genre": genre,
                "length": length
            }
            status_code = update_track(track_id, track_data)
            if status_code == 200:
                st.success("Track updated successfully")
            else:
                st.error("Failed to update track")
    else:
        st.write("Track not found")

elif option == "Delete Track":
    st.header("Delete an Existing Track")
    track_id = st.number_input("Track ID", min_value=1, step=1)
    
    if st.button("Delete Track"):
        status_code = delete_track(track_id)
        if status_code == 200:
            st.success("Track deleted successfully")
        else:
            st.error("Failed to delete track")

