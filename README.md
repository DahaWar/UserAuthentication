# UserAuthentication

This project provides an automated solution for testing the login functionality of the Altibox TV platform. It uses Selenium WebDriver to perform browser automation and Flask to create a web interface for running the tests and viewing the results. The results are displayed on the web page and can be downloaded as a PDF report.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Setup](#setup)
- [Usage](#usage)
- [Test Scenario](#test-scenario)
- [Logging](#logging)
- [Generating PDF Reports](#generating-pdf-reports)
- [Contributing](#contributing)
- [License](#license)

## Overview

This project automates the login process for multiple user accounts on the Altibox TV platform. It verifies whether the login is successful or if it fails, and captures the reason for any failures. The results are logged in real-time and can be viewed on a web interface.

## Features

- Automated login testing for multiple users.
- Real-time logging of test progress and results.
- PDF report generation with colored status indicators for each test.
- Headless browser testing using Selenium WebDriver.
- Flask web interface to start tests and view/download results.

## Setup

### Prerequisites

- Python 3.x
- pip (Python package installer)

### Installation

1. Clone the repository:

```sh
git clone https://github.com/yourusername/login-automation-testing.git
cd login-automation-testing
```

2. Install the required packages:

```sh
pip install -r requirements.txt
```

## Usage

1. **Run the Flask Application:**

```sh
python app.py
```

2. **Open your browser and navigate to:**

```
http://127.0.0.1:5000
```

3. **Start the Test:**
   - Click on the "Start Test" button on the web page to initiate the login tests.
   - The results will be displayed in real-time on the web page.

4. **Download the PDF Report:**
   - After the tests are completed, you can download the PDF report by clicking the "Download PDF" button.

## Test Scenario

The test scenario, named "User Authentication", involves the following steps:

1. **Open Login Page:** Navigates to the login page URL.
2. **Accept Cookies:** Clicks the "Accept Cookies" button if present.
3. **Enter Credentials and Submit:** Enters the email and password, and clicks the submit button.
4. **Check for Specific Failure Indicators:** Looks for incorrect credentials indicator and logs a failure if found.
5. **Check for Success Indicator:** Attempts to click the user element to confirm successful login.

## Logging

Real-time logging is implemented using Flask-SocketIO to update the web page with the current status of each test step. Each step logs both success and failure messages, providing detailed information on the progress and any issues encountered.

## Generating PDF Reports

The results of the login tests are compiled into a PDF report with the following details:
- User email
- Status (Passed or Failed)
- Reason for failure (if applicable)

The statuses are color-coded:
- **Green:** Passed
- **Red:** Failed

## Contributing

Contributions are welcome! If you have any suggestions or improvements, please create an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

Feel free to customize the README further based on your project's specifics and personal preferences.
