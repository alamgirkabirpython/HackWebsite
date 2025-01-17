import streamlit as st
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from itertools import permutations
import time

def login_to_website(url, email, email_field_name, password_field_name, login_button_xpath, password, success_url):
    """
    Attempts to log in to the website using the provided credentials.
    Returns:
        bool: True if login is successful (based on URL match), False otherwise.
    """
    try:
        browser = webdriver.Edge()
        browser.get(url)
        time.sleep(4)

        # Enter email and password
        browser.find_element(By.NAME, email_field_name).send_keys(email)
        browser.find_element(By.NAME, password_field_name).send_keys(password)

        # Click login button
        WebDriverWait(browser, 5).until(
            EC.element_to_be_clickable((By.XPATH, login_button_xpath))
        ).click()

        time.sleep(5)  # Wait for page to load (adjust if necessary)

        # Check if the URL indicates a successful login
        if browser.current_url == success_url:
            return True

    except Exception as e:
        st.error(f"An error occurred during login: {e}")

    finally:
        browser.close()

    return False


def password_testing(url, email, email_field_name, password_field_name, login_button_xpath, input_chars, success_url):
    """
    Function to test password combinations for a given email on a specified website.
    It generates all permutations of the input characters.
    """
    st.write(f"Testing password combinations for {email} on {url}...")

    # Phase 1: Test all permutations of the input characters
    if input_chars:
        st.write("Testing all permutations of the input string...")

        # Generate all permutations of the input string
        total_attempts = len(list(permutations(input_chars)))  # Total permutations of the input string
        progress_bar = st.progress(0)
        attempt_count = 0

        # Generate permutations and attempt login
        for perm in permutations(input_chars):
            attempt_password = ''.join(perm)
            attempt_count += 1

            # Print the attempted password
            st.text(f"Attempting password: {attempt_password}")

            # Attempt login
            success = login_to_website(
                url, email, email_field_name, password_field_name, login_button_xpath, attempt_password, success_url
            )
            progress = attempt_count / total_attempts
            progress_bar.progress(progress)

            if success:
                st.success(f"Login successful with password: {attempt_password}")
                st.write("Login URL indicates success.")
                st.balloons()
                return  # Exit the function upon success

    st.warning("Testing completed. No valid password found.")


# Streamlit App
st.title("Automated Login App with Password Testing")
st.write("Enter your email and test password combinations.")

# Input fields
url = st.text_input("Login URL", placeholder="Enter the login page URL", value="https://app.pallyy.com/login")
email = st.text_input("Email", placeholder="Enter your email")
email_field_name = st.text_input("Email field name (HTML 'name' attribute)", value="email")
password_field_name = st.text_input("Password field name (HTML 'name' attribute)", value="password")
login_button_xpath = st.text_input("Login button XPath", value='/html/body/div[1]/div/div/div/form/button')

# Password testing inputs
input_chars = st.text_input("Input characters for password testing (e.g., 'alom1234'):")
success_url = st.text_input("Success URL (URL that indicates successful login)", value="https://app.pallyy.com/dashboard/scheduling/calendar/month")

if st.button("Start Testing"):
    if not url or not email or not input_chars or not success_url:
        st.error("Please provide all inputs.")
    else:
        password_testing(
            url, email, email_field_name, password_field_name, login_button_xpath, input_chars, success_url
        )
