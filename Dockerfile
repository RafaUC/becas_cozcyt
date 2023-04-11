FROM debian:latest

#Update and upgrade system
RUN apt update
RUN apt -y upgrade
RUN apt-get install python3 python3-pip libmariadb-dev \
    nano -y
#RUN apt-get install apache2 python3 python3-pip libmariadb-dev \
#    libapache2-mod-wsgi-py3 python3-dev openssh-client nano -y

# Configure timezone
ENV TZ=America/Mexico_City
RUN ln -snf  /etc/l/usr/share/zoneinfo/$TZocaltime && echo $TZ > /etc/timezone

ENV PYTHONUNBUFFERED=1
RUN mkdir /app
WORKDIR /app
COPY requirements.txt /app/
RUN pip3 install -r requirements.txt
COPY . /app/
EXPOSE 8000