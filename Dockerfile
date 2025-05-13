FROM archlinux:latest

# Update system and install necessary packages
RUN pacman -Syyu --noconfirm && \
    pacman -S --noconfirm ffmpeg gcc git p7zip python-pip tzdata zstd && \
    ln -s /usr/bin/ffprobe /usr/local/bin/ffprobe && \
    ln -s /usr/bin/ffmpeg /usr/local/bin/ffmpeg && \
    python3 -m venv /venv && \
    pacman -Scc --noconfirm && \
    ln -sf /usr/share/zoneinfo/Europe/Paris /etc/localtime

# Set environment variables
ENV PATH="/venv/bin:$PATH"
ENV TZ=Europe/Paris

# Install Python dependencies
RUN pip3 install -U pip setuptools wheel && \
    mkdir /app

WORKDIR /app

# Clone the repository
RUN git clone https://github.com/orgservice/unzip-bot.git /app && \
    pip3 install -U -r requirements.txt

# Copy environment variables
COPY .env /app/.env

# Expose port for health check
EXPOSE 8080

# Run the bot
CMD ["python3", "-m", "unzipper"]
