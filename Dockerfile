FROM debian:latest

#Update and upgrade system
RUN apt update
RUN apt -y upgrade
RUN apt-get install python3 python3-pip libmariadb-dev \
    python3-cffi python3-brotli libpango-1.0-0 libpangoft2-1.0-0 \
    nano -y
    
# Configure timezone
ENV TZ=America/Mexico_City
RUN ln -snf  /etc/l/usr/share/zoneinfo/$TZocaltime && echo $TZ > /etc/timezone

ENV PYTHONUNBUFFERED=1
RUN mkdir /app
WORKDIR /app
COPY requirements.txt /app/
RUN pip3 install -r requirements.txt --break-system-packages
COPY . /app/
EXPOSE 8000