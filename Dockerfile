# Python base image
FROM python:3.9-slim-buster

# Set working directory
WORKDIR /app

# Copy and install requirements
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY ./app /app/app
COPY ./frontend /app/frontend

# Expose the port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]