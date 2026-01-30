FROM python:3.12-slim

RUN apt-get update && \
	apt-get install -y --no-install-recommends \
	ffmpeg \
	git \
	curl \
	build-essential \
	libffi-dev \
	libssl-dev \
	python3-dev \
	&& rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
	pip install --no-cache-dir -r requirements.txt

COPY bot.py .

RUN mkdir -p /music

CMD ["python", "bot.py"]
