FROM debian:latest

#Update and upgrade system
RUN apt update
RUN apt -y upgrade
RUN apt-get -y install python3 python3-pip libmariadb-dev \
    python3-cffi python3-brotli libpango-1.0-0 libpangoft2-1.0-0 \
    nano cron \
    lsb-release curl gpg 
    #redis
    
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
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "becas_cozcyt.wsgi"]
