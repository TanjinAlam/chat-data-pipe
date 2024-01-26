FROM python:3.9

WORKDIR /app

# Copy requirements file
COPY requirements.txt .

RUN apt-get update -y

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port that the application runs on
# EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]