FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . .

# Streamlit runs on port 8080 in Cloud Run
EXPOSE 8080

CMD ["streamlit", "run", "position_sizer_app.py", "--server.port=8080", "--server.enableCORS=false", "--server.enableXsrfProtection=false"]
