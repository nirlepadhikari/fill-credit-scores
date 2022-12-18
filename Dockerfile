FROM python:3.7

# Install dependencies
RUN pip install --upgrade pip

# Copy the current directory contents into the container at /app
COPY . /app

# Set the working directory to /app
WORKDIR /app


# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# This is a long running process and does not need any ports exposed
CMD ["python", "main.py"]