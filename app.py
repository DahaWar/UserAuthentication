from flask import Flask, render_template, redirect, url_for, send_file
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
from flask_socketio import SocketIO, emit
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.units import inch
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

app = Flask(__name__)
socketio = SocketIO(app)

# Define user credentials
users = {
    #'daha.warsame@lyse.no': 'Uwas12olafsen.',
    #'nhtestlab10@gmail.com': 'Test1234!',
    'nhtestlab4@gmail.com': 'Prod123!F'
}

def log_message(message):
    socketio.emit('log_message', message)
    socketio.sleep(0)  # Ensure the message is sent immediately

# Function to log in and check status
def login_and_check_status(username, password):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("window-size=1920,1080")
    chrome_options.add_argument("start-maximized")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    #driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        log_message(f'Testing {username} now')
        driver.get('https://tv.altibox.no/')  # Replace with the actual login page URL
        log_message('Opened login page.')

        # Accept all cookies
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "coi-banner__accept"))
        ).click()
        log_message('Accepted cookies.')

        # Click the login button
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "loginButton"))
        ).click()
        log_message('Clicked login button.')

        # Wait for the email address field to be present and fill it in
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "floatingLabelInput50"))
        ).send_keys(username)
        log_message('Entered email address.')

        # Fill in the password field
        driver.find_element(By.ID, "floatingLabelInput55").send_keys(password)
        log_message('Entered password.')

        # Click the submit button using a proper CSS selector for multiple classes
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn.btn-primary"))
        ).click()
        log_message('Clicked submit button.')

        # Check for the "Brukt opp alle dine bytter" indicator
        try:
            log_message('Checking for "Brukt opp alle dine bytter" button.')
            button_element = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[10]/div/div/main/button'))
            )
            button_element.click()
            log_message(f'{username} - Failed (Brukt opp alle dine bytter)')
            return "Failed", "Brukt opp alle dine bytter"
        except TimeoutException:
            log_message('No secondary button indicating used up switches found, proceeding.')

        # Check for the failure indicator immediately after submitting
        try:
            log_message('Checking for failure indicator.')
            WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn.btn-primary"))
            )
            log_message(f'{username} - Failed (Incorrect credentials)')
            return "Failed", "Incorrect credentials"
        except TimeoutException:
            log_message('No failure indicator found, proceeding.')

        # Try to click the "Bytt enhet" button if it exists
        try:
            log_message('Checking for "Bytt enhet" button.')
            bytt_enhet_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "styles_optionButton__x0pJ1"))
            )
            bytt_enhet_button.click()
            log_message('Clicked "Bytt enhet" button.')
        except TimeoutException:
            log_message('Bytt enhet button not found, proceeding.')

        # Wait for the user element to be present to confirm login completion
        log_message('Checking for user element.')
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "overflowHidden"))
        ).click()
        log_message('Clicked user element.')

        # Check for the success indicator using XPath
        try:
            log_message('Checking for success indicator.')
            WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div/div[2]/div[3]/nav/div/div/article/button'))
            )
            log_message(f'{username} - Passed')
            return "Passed", ""
        except TimeoutException:
            log_message(f'{username} - Failed (Success indicator not found)')
            return "Failed", "User could not login or changes can no longer be made"
    except (TimeoutException, NoSuchElementException, WebDriverException) as e:
        log_message(f'{username} - Failed (Exception: {str(e)})')
        return "Failed", "Changes can no longer be made(AKA too many tries)"
    finally:
        driver.quit()
        log_message('Closed browser.')

def generate_pdf(results, date):
    pdf_filename = f'login_test_results_{date}.pdf'
    document = SimpleDocTemplate(pdf_filename, pagesize=letter)
    styles = getSampleStyleSheet()
    styleN = styles['Normal']
    styleH = styles['Heading1']

    elements = []

    # Title
    title = Paragraph(f'Login Test Results - {date}', styleH)
    elements.append(title)
    elements.append(Paragraph(' ', styleN))  # Add a space

    # Table data
    data = [['User', 'Status', 'Reason']]
    for index, row in results.iterrows():
        status_color = "green" if row['Status'] == 'Passed' else "red"
        status_text = f'<font color="{status_color}">{row["Status"]}</font>'
        status_paragraph = Paragraph(status_text, styles['Normal'])
        data.append([index, status_paragraph, row['Reason']])

    # Create the table
    table = Table(data, colWidths=[2 * inch, 1.5 * inch, 3.5 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    elements.append(table)
    document.build(elements)
    return pdf_filename

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/start_test')
def start_test():
    # Get the current date in the format "dd.mm"
    current_date = datetime.now().strftime("%d.%m")

    # Initialize the results DataFrame
    results = pd.DataFrame(index=users.keys(), columns=['Status', 'Reason'])

    # Perform login tests for each user
    for user, pwd in users.items():
        status, reason = login_and_check_status(user, pwd)
        results.loc[user, 'Status'] = status
        results.loc[user, 'Reason'] = reason

    # Ensure specific failure reasons and empty reasons for Passed
    results['Reason'] = results.apply(
        lambda row: row['Reason'] if row['Status'] == 'Failed' and row['Reason'] != "" else (
            "" if row['Status'] == 'Passed' else 'User could not login or changes can no longer be made'), axis=1)

    # Generate PDF report
    pdf_filename = generate_pdf(results, current_date)

    # Convert DataFrame to a list of dictionaries for easy rendering in HTML
    results_list = results.reset_index().to_dict('records')

    return render_template('results.html', results=results_list, date=current_date, pdf_filename=pdf_filename)

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
