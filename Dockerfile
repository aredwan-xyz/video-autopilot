# Video Autopilot — containerized pipeline + dashboard.
# Build:  docker build -t video-autopilot .
# Run dashboard:  docker run --env-file .env -p 8000:8000 -v "$PWD/output:/app/output" video-autopilot
# Run daily job:  docker run --env-file .env -v "$PWD/output:/app/output" video-autopilot python -m src.orchestrator --all
FROM python:3.11-slim

# ffmpeg is the one heavy system dependency; fonts for caption rendering.
RUN apt-get update \
 && apt-get install -y --no-install-recommends ffmpeg fonts-dejavu-core curl unzip \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install python deps first for better layer caching.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code.
COPY . .

# Default caption font if the repo didn't ship one.
RUN mkdir -p assets/fonts assets/music \
 && [ -f assets/fonts/Montserrat-ExtraBold.ttf ] \
 || curl -fsSL -o assets/fonts/Montserrat-ExtraBold.ttf \
      "https://github.com/google/fonts/raw/main/ofl/montserrat/Montserrat%5Bwght%5D.ttf" || true

EXPOSE 8000

# Default command runs the dashboard. Override for the daily job (see header).
CMD ["uvicorn", "webapp.server:app", "--host", "0.0.0.0", "--port", "8000"]
