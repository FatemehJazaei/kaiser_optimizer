FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libegl1 \
    libglib2.0-0 \
    libxkbcommon-x11-0 \
    libfontconfig1 \
    libdbus-1-3 \
    libx11-xcb1 \
    libxcb1 \
    libxcb-glx0 \
    libxcb-keysyms1 \
    libxcb-image0 \
    libxcb-shm0 \
    libxcb-icccm4 \
    libxcb-sync1 \
    libxcb-xfixes0 \
    libxcb-shape0 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-cursor0 \      
    x11-xserver-utils \
    fonts-dejavu \
    fonts-freefont-ttf \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENV SAVE_DIR=/app/host-saves
ENV QT_AUTO_SCREEN_SCALE_FACTOR=0
ENV QT_SCALE_FACTOR=1
ENV QT_FONT_DPI=96

CMD ["python", "main.py"]
