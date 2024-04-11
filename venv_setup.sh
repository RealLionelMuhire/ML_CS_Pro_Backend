#!/bin/bash

# Prompt the user to enter the name of the virtual environment
read -p "Enter the name of the virtual environment: " env_name

# Check if the provided environment name is empty
if [ -z "$env_name" ]; then
    echo "Error: Please provide a valid name for the virtual environment."
    exit 1
fi

# Check if virtualenv is installed
if ! command -v virtualenv &> /dev/null; then
    echo "Error: virtualenv is not installed. Please install it using 'sudo apt install virtualenv'."
    exit 1
fi

# Create the virtual environment
virtualenv $env_name

# Inform the user about the successful creation of the virtual environment
echo "Virtual environment '$env_name' has been created successfully."

