FROM python:3.10.2

ENV DATABASE_URL="postgresql://postgres:123qwe123qwe@35.238.209.92/postgres"
ENV IAM_SERVICE_URL="https://iam.forge-code.com"

WORKDIR /code

# Create a virtual environment
RUN python -m venv venv
ENV PATH="/code/venv/bin:$PATH"

# Copy requirements file and install dependencies
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the application code
COPY ./app /code/app

EXPOSE 8002

# Set the default command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002", "--reload"]

# Set restart policy to always
# This ensures that the container restarts automatically if the host computer restarts
# Note: Docker Compose also offers restart policies, if you are using Docker Compose, you can specify the restart policy there instead.
# For Docker Compose, add "restart: always" under the service definition.
# Example:
# services:
#   my_service:
#     restart: always
# For standalone Docker, use the --restart option with the docker run command.
# Example:
# docker run --restart always -d my_image
# This will ensure the container restarts automatically when the host computer restarts.
# For more control over restart policies, you can explore other options like "unless-stopped" or "on-failure".
# docker build -t blog-service .
# docker run -d --restart=always --name blog-service -p 8002:8002 blog-service

