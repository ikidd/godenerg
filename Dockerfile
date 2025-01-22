FROM python:3.9-slim-buster

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /axpert
WORKDIR /axpert

COPY requirements.txt .
RUN python3.9 -m pip install --no-cache-dir --upgrade \
    pip \
    setuptools==58.2.0 \
    wheel
RUN python3.9 -m pip install --no-cache-dir \
    -r requirements.txt

EXPOSE 8889
EXPOSE 8890

CMD ["python3.9", "main.py", "--usb", "-d", "/dev/hidraw0", "--status", "-f", "json"]
