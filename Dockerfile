FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements_finance.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements_finance.txt

# Copy application files
COPY uae_expat_finance_bot.py .

# Create directory for user data
RUN mkdir -p /app/user_profiles

# Set environment variables (override these when running)
ENV TELEGRAM_BOT_TOKEN=""
ENV ANTHROPIC_API_KEY=""

# Run the bot
CMD ["python", "uae_expat_finance_bot.py"]
