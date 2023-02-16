FROM python:3
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg
WORKDIR /app
COPY . .
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
CMD ["python", "phoebe.py"]