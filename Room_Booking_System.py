# Import Libraries
import streamlit as st
import numpy as np

# Total floors and rooms
FLOORS = 10
ROOMS_PER_FLOOR = [10] * 9 + [7]  # Floors 1-9 have 10 rooms each, Floor 10 has 7 rooms
TOTAL_ROOMS = sum(ROOMS_PER_FLOOR)

# Initialize room booking status
if 'room_status' not in st.session_state:
    st.session_state.room_status = np.zeros(TOTAL_ROOMS, dtype=bool)

def get_room_number(index):
    """Convert index to room number."""
    floor = next(i for i, v in enumerate(np.cumsum(ROOMS_PER_FLOOR)) if index < v)
    room_in_floor = index - (np.cumsum([0] + ROOMS_PER_FLOOR[:-1]))[floor] + 1
    return (floor + 1) * 100 + room_in_floor

def book_rooms(num_rooms):
    """Book the optimal rooms based on rules."""
    available_rooms = [i for i, booked in enumerate(st.session_state.room_status) if not booked]
    if len(available_rooms) < num_rooms:
        return []
    
    # Prioritize rooms on the same floor
    for floor in range(FLOORS):
        floor_rooms = [i for i in available_rooms if get_room_number(i) // 100 == floor + 1]
        if len(floor_rooms) >= num_rooms:
            booked = floor_rooms[:num_rooms]
            for i in booked:
                st.session_state.room_status[i] = True
            return [get_room_number(i) for i in booked]
    
    # If not enough on one floor, minimize total travel time
    booked = available_rooms[:num_rooms]
    for i in booked:
        st.session_state.room_status[i] = True
    return [get_room_number(i) for i in booked]

def reset_bookings():
    """Reset all room bookings."""
    st.session_state.room_status = np.zeros(TOTAL_ROOMS, dtype=bool)

def generate_random_occupancy():
    """Randomly mark rooms as booked."""
    st.session_state.room_status = np.random.choice([True, False], size=TOTAL_ROOMS, p=[0.3, 0.7])

# Streamlit UI
st.title("Hotel Room Booking System")

col1, col2 = st.columns([1, 9])

with col1:
    st.subheader("Lift & Staircase")
    st.markdown("""<div style='width: 40px; height: 1200px; background-color: gray; text-align: center; display: flex; flex-direction: column; justify-content: space-between;'>
                <p style='writing-mode: vertical-lr; transform: rotate(180deg); margin: 10px; font: 16px'>LIFT</p>
                <p style='writing-mode: vertical-lr; transform: rotate(180deg); margin: 10px;'>STAIRS</p>
                </div>""", unsafe_allow_html=True)

with col2:
    st.subheader("Room Booking")
    num_rooms = st.number_input("Enter number of rooms to book (Max 5):", min_value=1, max_value=5, step=1)
    btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1])
    with btn_col1:
        if st.button("Book Rooms"):
            booked_rooms = book_rooms(num_rooms)
            if booked_rooms:
                st.success(f"Rooms booked: {booked_rooms}")
            else:
                st.error("Not enough available rooms.")
    with btn_col2:
        if st.button("Book Random"):
            generate_random_occupancy()
            st.rerun()
    with btn_col3:
        if st.button("Reset Bookings"):
            reset_bookings()
            st.rerun()

    st.subheader("Room Status")
    for floor in range(FLOORS, 0, -1):
        floor_indices = list(range(sum(ROOMS_PER_FLOOR[:floor-1]), sum(ROOMS_PER_FLOOR[:floor])))
        floor_rooms = [
            f"<div style='display:inline-block; padding:10px; margin:5px; border:1px solid black; background-color: {'green' if st.session_state.room_status[i] else 'white'};'>{get_room_number(i)}</div>"
            for i in floor_indices
        ]
        st.markdown(f"**Floor {floor}:** " + " ".join(floor_rooms), unsafe_allow_html=True)

    # Display randomly booked rooms by floor
    st.subheader("Booked Rooms:")
    for floor in range(1, FLOORS + 1):
        booked_on_floor = [get_room_number(i) for i in range(TOTAL_ROOMS) if st.session_state.room_status[i] and get_room_number(i) // 100 == floor]
        if booked_on_floor:
            booked_str = "All" if len(booked_on_floor) == ROOMS_PER_FLOOR[floor-1] else ", ".join(map(str, booked_on_floor))
            suffix = lambda n: 'st' if n == 1 else 'nd' if n == 2 else 'rd' if n == 3 else 'th'
            st.write(f"{floor}{suffix(floor)} Floor - {booked_str}")

