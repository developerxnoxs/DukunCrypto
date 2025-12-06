FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    wget \
    gnupg2 \
    software-properties-common \
    xvfb \
    x11vnc \
    fluxbox \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

RUN dpkg --add-architecture i386 && \
    mkdir -pm755 /etc/apt/keyrings && \
    wget -O /etc/apt/keyrings/winehq-archive.key https://dl.winehq.org/wine-builds/winehq.key && \
    wget -NP /etc/apt/sources.list.d/ https://dl.winehq.org/wine-builds/debian/dists/bookworm/winehq-bookworm.sources && \
    apt-get update && \
    apt-get install -y --install-recommends winehq-stable || \
    apt-get install -y wine wine32 wine64 || \
    echo "Wine installation skipped - will use pymt5linux bridge"

RUN apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --no-cache-dir pymt5linux || echo "pymt5linux not available"

COPY . .

RUN mkdir -p /app/mt5 /var/log/supervisor && \
    chmod +x /app/scripts/mt5_launcher.sh 2>/dev/null || true

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DISPLAY=:99

ENV BOT_MODE=polling
ENV MT5_ENABLE_TRADING=false
ENV MT5_RISK_PERCENT=1.0
ENV MT5_MAX_POSITIONS=5

EXPOSE 5000
EXPOSE 5900
EXPOSE 8001

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
