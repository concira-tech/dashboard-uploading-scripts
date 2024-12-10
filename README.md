# Concira Dashboard Uploading Scripts

This is a Flask-based application for managing various services like Room Service, Laundry, and Housekeeping.


## Prerequisites

1. Python 3.10 or later.
2. Firebase Admin SDK credentials.
3. Environment variables set in .env file.


## Folder Structure

```
project_root/
├── app/                 # Contains main application logic
│   ├── firebase.py      # Firebase initialization
│   ├── helpers.py       # Shared helper functions
│   ├── routes.py        # API route registration
│   ├── services/        # Service-specific logic
│       ├── room_service.py
├── logs/                # Log files
├── sample_files/        # Sample Excel files
├── .env                 # Environment variables
├── pm2-config.json      # PM2 configuration for managing the app
├── requirements.txt     # Python dependencies
├── run.py               # Entry point for the application
```

## Setup Instructions

1. Clone the repository:
    ```
    git clone <repository_url>
    cd <repository_folder>
    ```

2. Create and activate a virtual environment:
    ```
    conda create --name <environment-name> python=3.10
    conda activate <environment-name>
    ```

3. Install dependencies:

    ```
    pip install -r requirements.txt
    ```

4. Set up the .env file:

- Copy the provided .env.example (if available) and fill in the required Firebase and other environment variables.

5. Add Firebase Admin SDK credentials:
- Save the Firebase Admin SDK credentials as specified in app/firebase.py.

## Running the Application

**Note:** Install npm, node and pm2 for running the server.

1. Run locally using Flask:

    ```
    python run.py
    ```

2. Run with Gunicorn (Production):

    ```
    gunicorn -w 4 -b 0.0.0.0:8000 run:app

    ```

3. Run with PM2:

    ```
    pm2 start pm2-config.json
    ```