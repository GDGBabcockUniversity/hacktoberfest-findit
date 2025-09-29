![FindIt](/Team1/static/images/findit-logo.png)




## Overview

FindIt is a web application designed to streamline the process of reporting lost items and finding found items. The platform facilitates communication between users to aid in the recovery of lost possessions.

## Features

- **User Registration and Authentication:**
  - Users can register for a new account.
  - Login and logout functionality is provided.

- **Report Lost Items:**
  - Users can report their lost items, providing details such as color, type, brand, and last known location.
  - Contact information can be submitted for communication purposes.

- **Find Found Items:**
  - Users who find items can report them, including a description, found location, and contact information.
  - Claim functionality allows users to request contact information to verify ownership.

- **Notification System:**
  - Users receive notifications when their reported item is found or when an item they've claimed has contact information available.

- **Search Functionality:**
  - Efficient search functionality based on location or item description.

## Getting Started

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/Shadowdevsbu/lost-and-found-system
   ```

2. **Navigate to Project Directory:**
    ```bash
    cd lost-and-found-system
    ```
3. **Create a Virtual Environment:**
- For Mac & Linux
    ```bash
    python -m venv shadow && source shadow/bin/activate
    ```
- For windows
    ```bash
    python -m venv shadow 
    .\shadow\Scripts\activate
    ```
4. **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
   
5. **Database Setup:**
- Configure your database settings in settings.py.
- Run migrations:
    ```py
        python manage.py makemigrations
    ```
6. **Run the Development Server:**
    ```bash
    python manage.py runserver
    ```
7. **Visit the App:**
    Open your web browser and go to http://localhost:8000 to access the app.