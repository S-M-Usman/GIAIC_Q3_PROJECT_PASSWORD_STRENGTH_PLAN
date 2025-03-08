import json
import os
import re
from typing import List, Dict

# FILE PATHS
PASSWORDS_FILE = "storage/passwords.json"
LINKS_FILE = "storage/links.json"

# ENSURING STORAGE DIRECTORY EXISTS
os.makedirs("storage", exist_ok=True)

# REGEX PASSWORD PATTERN (Minimum 8 characters, 1 letter, 1 digit, 1 special character)
password_regex_pattern = re.compile(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$")

def data_loader(file_path: str) -> List[Dict]:
    """Loads JSON data from a file."""
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return []

def data_saver(file_path: str, data: List[Dict]):
    """Saves JSON data to a file."""
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

def password_validator(password: str) -> bool:
    """Validates password against security rules."""
    return bool(password_regex_pattern.match(password))

def password_evaluator(password: str) -> Dict:
    """Evaluates the strength of a given password."""
    password_strength_score = 0
    password_strength_feedback = []

    # Checking password length
    if len(password) >= 8:
        password_strength_score += 1
    else:
        password_strength_feedback.append("❌ Password must be at least 8 characters long.")

    # Checking for uppercase & lowercase mix
    if re.search(r"[A-Z]", password) and re.search(r"[a-z]", password):
        password_strength_score += 1
    else:
        password_strength_feedback.append("❌ Include both uppercase and lowercase letters.")

    # Presence of at least one number
    if re.search(r"\d", password):
        password_strength_score += 1
    else:
        password_strength_feedback.append("❌ Add at least one number (0-9).")

    # Presence of at least one special character
    if re.search(r"[!@#$%^&*]", password):
        password_strength_score += 1
    else:
        password_strength_feedback.append("❌ Include at least one special character (!@#$%^&*).")

    # Ranking system based on score
    password_strength_ranking = ["Weak", "Moderate", "Good", "Strong", "Excellent"]
    password_rank = password_strength_ranking[min(password_strength_score, 4)]

    return {
        "score": password_strength_score,
        "rank": password_rank,
        "feedback": password_strength_feedback
    }

def check_repeated_password(password: str) -> (bool| str):
    """Checks if a password has been used recently (last 5 passwords)."""
    passwords = data_loader(PASSWORDS_FILE)

    for entry in passwords:
        if entry["password"] == password:
            return False, "❌ This password was recently used. Choose another."

    return True, "✅ Password is unique and not reused."

def add_password(password: str) -> str:
    """Adds a password to history with its strength score, ensuring no reuse of last 5 passwords."""
    passwords = data_loader(PASSWORDS_FILE)

    is_unique, history_message = check_repeated_password(password)
    if not is_unique:
        return history_message

    if not password_validator(password):
        return "❌ Password does not meet security criteria."

    analysis = password_evaluator(password)
    
    passwords.append({
        "password": password, 
        "score": analysis["score"], 
        "rank": analysis["rank"], 
        "feedback": analysis["feedback"]
    })

    # Maintain last 5 passwords
    if len(passwords) > 5:
        passwords.pop(0)

    data_saver(PASSWORDS_FILE, passwords)
    return "✅ Success: Password added successfully."

def store_link(site: str, username: str, password: str) -> str:
    """Stores a password with an associated site link and username."""
    links = data_loader(LINKS_FILE)

    for entry in links:
        if entry["site"] == site and entry["username"] == username:
            return "❌ Error: A password is already stored for this site and username."

    analysis = password_evaluator(password)
    links.append({
        "site": site, 
        "username": username, 
        "password": password, 
        "score": analysis["score"], 
        "rank": analysis["rank"]
    })

    data_saver(LINKS_FILE, links)
    return "✅ Success: Password saved for the site."

def get_linked_passwords() -> List[Dict]:
    """Retrieves all stored site-password mappings."""
    return data_loader(LINKS_FILE)

# Example usage
if __name__ == "__main__":
    print(add_password("Secure@123"))  # Add password test
    print(store_link("https://example.com", "user123", "Secure@123"))  # Store site password test
    print(get_linked_passwords())  # Fetch all stored links
