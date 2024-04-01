# ML_CS_Pro_Backend

ML Corporate Services Software Application - Backend

This Django project serves as the backend for the ML Corporate Services Software Application. It includes features for client data management, administrator accounts, client accounts, and more.

## Getting Started

These instructions will help you set up and run the Django backend for the ML Corporate Services Software Application.

Or download and run [`setup_project.sh`](./setup_project.sh)

### Prerequisites

- Python 3.x
- Django
- MySQL Database

### Installing

1. Clone the repository:

    git clone https://github.com/RealLionelMuhire/ML_CS_Pro_Backend.git

2. Navigate to the project directory:

    cd ML_CS_Pro_Backend

3. Create a virtual environment (optional but recommended):

    python -m venv venv

4. Activate the virtual environment:

   On Windows:

    venv\Scripts\activate

   On macOS/Linux:

    source venv/bin/activate

5. Install project dependencies:

    pip install -r requirements.txt

### Configure the database settings:

   Open `ML_CS_Pro_Backend/settings.py` and update the `DATABASES` section with your MySQL database details.

   Apply database migrations:

    python manage.py makemigrations
    python manage.py migrate

### Create a superuser:

    python manage.py createsuperuser

### Start the development server:

    python manage.py runserver

   Visit http://127.0.0.1:8000/ in your browser to access the Django welcome page.

### Features

- Client Data Management
- Administrator Accounts (Level 1, Level 2, Level 3)
- Client Accounts
- Client Account Interface

### Third-Party Services Used

- Django REST Framework for building APIs
- Django CORS Headers for handling Cross-Origin Resource Sharing
- Django Crispy Forms for enhancing forms in Django
- Django Debug Toolbar for debugging purposes
- Firebase Admin SDK for integrating with Firebase services
- Google Cloud services including Firestore and Storage for cloud-based data storage
- Google APIs for various functionalities like authentication and calendar integration

### License

This project is licensed under the MIT License - see the LICENSE.md file for details.

