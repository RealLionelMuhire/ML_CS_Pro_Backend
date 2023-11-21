# ML_CS_Pro_Backend

ML Corporate Services Software Application - Backend

This Django project serves as the backend for the ML Corporate Services Software Application. It includes features for client data management, administrator accounts, client accounts, and more.

## Getting Started

These instructions will help you set up and run the Django backend for the ML Corporate Services Software Application.

### Prerequisites

- Python 3.x
- Django
- MySQL Database

### Installing

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/ML_CS_Pro_Backend.git

2. Navigate to the project directory:

   ```bash
   cd ML_CS_Pro_Backend

3. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv venv

4. Activate the virtual environment:

   On Windows:

   `venv\Scripts\activate`

   On macOS/Linux:

   `source venv/bin/activate`

5. Install project dependencies:

   ```bash
   pip install -r requirements.txt



### Configure the database settings:

   Open ML_CS_Pro_Backend/settings.py and update the DATABASES section with your MySQL database details.

   Apply database migrations:

   ```bash
   python manage.py makemigrations
   python manage.py migrate

### Create a superuser:

   ```bash
   python manage.py createsuperuser

### Start the development server:

   ```bash
   python manage.py runserver

   Visit http://127.0.0.1:8000/ in your browser to access the Django welcome page.

### Features
Client Data Management
Administrator Accounts (Level 1, Level 2, Level 3)
Client Accounts
Client Account Interface

License
This project is licensed under the MIT License - see the LICENSE.md file for details.
