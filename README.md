# Installation Guide

## Prerequisites

Make sure you have **Python 3** installed on your system.

## Setup Instructions

### 1. Create a Virtual Environment

Run the following command to create a virtual environment:

```sh
python3 -m venv venv
```

### 2. Activate the Virtual Environment

- On **Windows**:
  ```sh
  venv\Scripts\activate
  ```
- On **macOS/Linux**:
  ```sh
  source venv/bin/activate
  ```

### 3. Install Dependencies

Run the following command to install required packages:

```sh
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Edit the file `handle.py` and replace the placeholder values with your actual data:

- `WEBHOOK_URL`: Set this variable to your Discord webhook URL.
- `SPREADSHEET_ID`: Set this variable to your Google Spreadsheet ID.

### 5. Add Google Credentials

Place your Google credentials file inside the `./credential` folder.

### 6. Run the Application

After completing the setup, run the application using:

```sh
python app.py
```

---

Now your application is ready to use! 🚀

<-- Make by Ptsy -->
