#!/env/bin/bash

# Clone the repository
git clone https://github.com/your-username/ML_CS_Pro_Backend.git

# Navigate to the project directory
cd ML_CS_Pro_Backend

# Create a virtual environment (optional but recommended)
python -m venv venv

# Activate the virtual environment
# On Windows:
# source venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install project dependencies
pip install -r requirements.txt

# Configure the database settings
# Open ML_CS_Pro_Backend/settings.py and update the DATABASES section with your MySQL database details.
# Apply database migrations
python manage.py makemigrations
python manage.py migrate

# Create a superuser
python manage.py createsuperuser

# Start the development server
python manage.py runserver

echo "Visit http://127.0.0.1:8000/ in your browser to access the Django welcome page."

