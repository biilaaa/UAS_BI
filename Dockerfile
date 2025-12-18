FROM python:3.11

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH="/app"

# Izinkan start.sh dijalankan
RUN chmod +x start.sh

# Jalankan keduanya
CMD ["./start.sh"]
