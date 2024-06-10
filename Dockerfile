# Define the base image
FROM python:3.12-slim

# Upgrade pip package manager to the latest version
RUN pip install --upgrade pip

# Set the working directory inside the container
WORKDIR /code

COPY requirements.txt /code/

# Install Python dependencies listed in the requirements.txt file
RUN pip install -r requirements.txt


# Copy the contents of the current directory (in Docker context) into the container's /app directory
COPY src /code/

# Copy the entrypoint.sh script into the container
COPY entrypoint.sh /entrypoint.sh

# Grant execution permissions to the entrypoint.sh script inside the container
RUN chmod +x /entrypoint.sh

# Set the entry point for the container, running the entrypoint.sh script
ENTRYPOINT ["bash", "/entrypoint.sh"]

# Expose port 8000 to allow external access to the application
EXPOSE 8000