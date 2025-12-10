FROM python:3.11-slim

WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

RUN chmod +x ./entrypoint.sh


# Expose port
EXPOSE 5001



# Run the application
ENTRYPOINT [ "./entrypoint.sh" ]