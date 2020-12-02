FROM python:3.6.9-slim

RUN apt update && \ 
apt upgrade -y && \
apt install unixodbc-dev -y && \
apt-get update \
&& apt-get install gcc g++ -y \
&& apt-get install -y gnupg2 \
&& apt-get clean 

RUN apt-get install curl -y
RUN apt-get install apt-transport-https -y
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/ubuntu/16.04/prod.list | tee /etc/apt/sources.list.d/msprod.list

RUN apt-get update
RUN chmod o+r /etc/resolv.conf
RUN apt-get install nano
RUN export TERM=xterm


ENV ACCEPT_EULA=y DEBIAN_FRONTEND=noninteractive
RUN apt-get install mssql-tools unixodbc-dev -y

COPY . /app

WORKDIR app
ENV PATH="/root/.local/bin:${PATH}"
RUN pip install --user -r requirements.txt
ENTRYPOINT [ "python" ]
CMD [ "app.py" ] 

