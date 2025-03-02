
import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

# Database setup
conn = sqlite3.connect("lectures.db")
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS lectures (
                group_code TEXT,
                arrived TEXT,
                start TEXT,
                break_start TEXT,
                break_end TEXT,
                lecture_end TEXT,
                break_duration TEXT,
                lecture_duration TEXT,
                notes TEXT
            )''')
conn.commit()

# UI styling
st.set_page_config(page_title="Lecture Tracker", layout="centered")
st.markdown("""
    <style>
    body {
        background-color: #1e1e2f;
        color: #f0f0f0;
    }
    .main {
        background-color: #2b2b3b;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
    }
    h1 {
        color: #ff79c6;
    }
    .stButton>button {
        background-color: #6272a4;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
    }
    .stButton>button:hover {
        background-color: #50fa7b;
    }
    </style>
""", unsafe_allow_html=True)

# Session state
if 'page' not in st.session_state:
    st.session_state['page'] = 1

if 'group_code' not in st.session_state:
    st.session_state['group_code'] = None

if 'arrival_time' not in st.session_state:
    st.session_state['arrival_time'] = None

if 'start_time' not in st.session_state:
    st.session_state['start_time'] = None

if 'break_start' not in st.session_state:
    st.session_state['break_start'] = None

if 'break_end' not in st.session_state:
    st.session_state['break_end'] = None

if 'lecture_end' not in st.session_state:
    st.session_state['lecture_end'] = None

if 'notes' not in st.session_state:
    st.session_state['notes'] = ""

# Page navigation
def next_page():
    st.session_state['page'] += 1
    st.rerun()

def reset():
    st.session_state['page'] = 1
    st.session_state['group_code'] = None
    st.session_state['arrival_time'] = None
    st.session_state['start_time'] = None
    st.session_state['break_start'] = None
    st.session_state['break_end'] = None
    st.session_state['lecture_end'] = None
    st.session_state['notes'] = ""
    st.rerun()

# Step 1: Select Group and Mark Arrival
def page1():
    st.title("Step 1: Select Group and Mark Arrival")
    st.session_state['group_code'] = st.selectbox("Select Group Code:", ["Group 1", "Group 2"])
    if st.button("Arrived"):
        st.session_state['arrival_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        next_page()

# Step 2: Start Lecture
def page2():
    st.title(f"Step 2: Start Lecture for {st.session_state['group_code']}")
    st.write(f"Arrival Time: {st.session_state['arrival_time']}")
    if st.button("Start Lecture"):
        st.session_state['start_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        next_page()

# Step 3: Break Management or Skip
def page3():
    st.title("Step 3: Manage Breaks or Skip")
    st.write(f"Lecture Start Time: {st.session_state['start_time']}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start Break"):
            st.session_state['break_start'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.rerun()
    
    with col2:
        if st.button("Skip Break"):
            st.session_state['break_start'] = None
            st.session_state['break_end'] = None
            next_page()
    
    if st.session_state['break_start']:
        st.write(f"Break Start Time: {st.session_state['break_start']}")
        if st.button("End Break"):
            st.session_state['break_end'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            next_page()

# Step 4: End Lecture and Save Data
def page4():
    st.title("Step 4: End Lecture & Save Data")
    st.write(f"Break End Time: {st.session_state['break_end'] if st.session_state['break_end'] else 'No Break Taken'}")
    st.session_state['notes'] = st.text_area("Add Notes (Optional):")
    
    if st.button("End Lecture"):
        st.session_state['lecture_end'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        start_dt = datetime.strptime(st.session_state['start_time'], "%Y-%m-%d %H:%M:%S")
        end_dt = datetime.strptime(st.session_state['lecture_end'], "%Y-%m-%d %H:%M:%S")
        
        if st.session_state['break_start'] and st.session_state['break_end']:
            break_start_dt = datetime.strptime(st.session_state['break_start'], "%Y-%m-%d %H:%M:%S")
            break_end_dt = datetime.strptime(st.session_state['break_end'], "%Y-%m-%d %H:%M:%S")
            break_duration = break_end_dt - break_start_dt
        else:
            break_duration = "0:00:00"
        
        lecture_duration = end_dt - start_dt

        c.execute("INSERT INTO lectures (group_code, arrived, start, break_start, break_end, lecture_end, break_duration, lecture_duration, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                  (st.session_state['group_code'], st.session_state['arrival_time'], st.session_state['start_time'],
                   st.session_state['break_start'], st.session_state['break_end'], st.session_state['lecture_end'],
                   str(break_duration), str(lecture_duration), st.session_state['notes']))
        conn.commit()
        
        st.success(f"Lecture data for {st.session_state['group_code']} saved successfully!")
        reset()

# View and Export Records with Headers
def view_records():
    st.title("Lecture Records")
    df = pd.read_sql_query("SELECT * FROM lectures", conn)
    st.dataframe(df)
    
    if st.button("Export to CSV"):
        df.to_csv("lecture_records.csv", index=False)
        st.success("Dataset exported with headers!")
    
    if st.button("Back to Home"):
        reset()

if st.session_state['page'] == 1:
    page1()
elif st.session_state['page'] == 2:
    page2()
elif st.session_state['page'] == 3:
    page3()
elif st.session_state['page'] == 4:
    page4()
elif st.session_state['page'] == 5:
    view_records()

if st.button("View Records"):
    st.session_state['page'] = 5
    st.rerun()
