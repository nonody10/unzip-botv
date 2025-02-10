FROM debian:latest

RUN apt update && apt upgrade -y && \
    apt install -y ffmpeg gcc git p7zip-full python3-pip tzdata zstd && \
    ln -sf /usr/share/zoneinfo/Europe/Paris /etc/localtime
ENV TZ=Europe/Paris
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"
RUN pip3 install -U pip setuptools wheel && \
    mkdir /app
WORKDIR /app
RUN git clone https://github.com/orgservice/unzip-bot.git /app && \
    pip3 install -U -r requirements.txt
COPY .env /app/.env
CMD ["/bin/bash", "start.sh"]
