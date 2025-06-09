# linkedin_bot
A Streamlit-based LinkedIn automation bot that uses Selenium and proxy rotation to log into multiple accounts, search for jobs, apply filters, and auto-submit “Easy Apply” applications. It handles authentication via cookies, bypasses LinkedIn detection, and fills dynamic job forms intelligently.

### 📌 **LinkedIn Job Application Automation Bot (Python + Selenium + Streamlit)**

This advanced automation bot is designed to streamline the job application process on LinkedIn using **Selenium**, **undetected-chromedriver**, and a **Streamlit GUI**. It supports **multi-account job applications** with automated login, proxy handling, form filling, and intelligent navigation through the “Easy Apply” process — making it ideal for users managing multiple profiles or large-scale job outreach.

---

### ✅ **Key Features**

* **🔐 Cookie-Based Auto Login**: Saves and loads session cookies for each account to bypass login screens and reduce bot detection.
* **🌍 Proxy Integration**: Rotates between authenticated proxies to simulate access from different IPs and avoid rate limiting or bans.
* **🎯 Job Search Automation**: Automatically searches for jobs using customizable filters like title, location, posting date, and “Easy Apply” availability.
* **🤖 Easy Apply Submission**: Handles the full “Easy Apply” flow including:

  * Navigating forms
  * Detecting and answering job-specific questions
  * Uploading input where required (experience, salary, summary, etc.)
  * Skipping or discarding if forms are too complex
* **🛡️ Anti-Detection Features**: Uses undetected ChromeDriver and simulates human-like behavior with randomized delays, scrolling, and typing.
* **📋 Streamlit Interface**: Upload a CSV of accounts, run applications, and view live progress and results.

---

### 🧠 **Technical Highlights**

* **Python 3**
* **Selenium with undetected-chromedriver**
* **Streamlit for interactive GUI**
* **Dynamic form handling via XPath and CSS selectors**
* **Multithreading support for sequential multi-account execution**
* **Session persistence via cookie JSON files**
* **Proxy extension generator using custom Chrome extensions**

---

### 📂 **CSV Format Example**

The bot uses a CSV file with columns:

```csv
email,password,proxy
example1@gmail.com,password123,username:pass@ip:port
example2@gmail.com,password456,username:pass@ip:port
```

---

### 💼 **Use Cases**

* Automate bulk job applications for multiple candidates
* Use in recruitment agencies for batch processing
* Boost visibility by applying to new listings daily
* Practice automation workflows and bot development in Selenium

---

### ⚠️ **Disclaimer**

This bot is for educational and research purposes only. Automating LinkedIn activity may violate their Terms of Use. Use responsibly and at your own risk.

