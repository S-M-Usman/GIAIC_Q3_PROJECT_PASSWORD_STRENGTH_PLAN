import streamlit as st
import json
import os
import time
from password_utils import password_evaluator

# Set Page Config
st.set_page_config(page_title="🔐 Password Manager", layout="wide")

# Load Custom CSS
def load_css():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Ensure storage directory exists
if not os.path.exists("storage"):
    os.makedirs("storage")

# Load Password History
password_file = "storage/passwords.json"

def load_passwords():
    if os.path.exists(password_file):
        with open(password_file, "r") as f:
            return json.load(f)
    return []

def save_passwords(passwords):
    with open(password_file, "w") as f:
        json.dump(passwords, f, indent=4)

# Load stored passwords
password_history = load_passwords()

# Navbar
st.markdown("""
    <div class="navbar">
        <h1>🔐 Password Manager</h1>
    </div>
""", unsafe_allow_html=True)

# Tabs
tabs = st.tabs(["🔍 Password Checker", "📜 Password History"])

with tabs[0]:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.header("🔹 Check Your Password Strength")
    password = st.text_input("Enter a password:", type="password", key="password_input")
    
    if password:
        result = password_evaluator(password)
        checks = [
            ("Length", lambda p: len(p) >= 8),
            ("Upper & Lowercase", lambda p: any(c.isupper() for c in p) and any(c.islower() for c in p)),
            ("Number", lambda p: any(c.isdigit() for c in p)),
            ("Special Character", lambda p: any(c in "!@#$%^&*()_+-=[]{}|;':,./<>?" for c in p)),
            ("Common/Weak Password", lambda p: result['score'] > 2)
        ]
        
        passed_checks = 0
        progress = 0
        progress_bar = st.progress(progress)
        
        for i, (check, validator) in enumerate(checks):
            with st.spinner(f"Checking {check}..."):
                time.sleep(0.5)  # Simulate step-by-step checking
                if validator(password):
                    st.success(f"✅ {check} Passed")
                    passed_checks += 1
                else:
                    st.error(f"❌ {check} Missing")
                    if i < len(result['feedback']):
                        st.warning(result['feedback'][i])
                    break
                progress += 20
                progress_bar.progress(progress)

        # Check if password already exists
        existing_passwords = [entry['password'] for entry in password_history]
        
        if passed_checks == len(checks):
            st.balloons()
            if password in existing_passwords:
                st.warning("⚠️ This password already exists in your history!")
            else:
                if st.button("Save Password", key="save_password_button", help="Save your password!", use_container_width=True):
                    password_entry = {"password": password, "rank": result['score']}
                    password_history.append(password_entry)
                    save_passwords(password_history)
                    st.success("✅ Password saved successfully!")
                    st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

with tabs[1]:
    st.header("🔹 Password History")
    
    if password_history:
        for i, entry in enumerate(password_history):
            st.markdown(f"<div class='history-card'><h3>{i+1}. {entry['rank']}</h3>", unsafe_allow_html=True)
            st.write(f"🔒 **Password:** {entry['password']}")
            st.write(f"📊 **Strength:** {entry['rank']}")
            
            col1, col2 = st.columns(2)
            with col1:
                new_password = st.text_input(f"Edit password {i}:", type="password", key=f"edit_input_{i}")
                if new_password:
                    if new_password in existing_passwords:
                        st.warning("⚠️ This password already exists!")
                    else:
                        password_history[i]['password'] = new_password
                        save_passwords(password_history)
                        st.success("Password updated!")
                        st.rerun()
            
            with col2:
                if st.button(f"Delete {i}", key=f"delete_{i}"):
                    password_history.pop(i)
                    save_passwords(password_history)
                    st.warning("Password deleted!")
                    st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.write("No password history yet.")
