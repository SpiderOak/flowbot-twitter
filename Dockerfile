FROM python:2.7

# Download & Install Semaphor
RUN apt-get update
RUN apt-get install curl
RUN apt-get -y install libxss1
RUN curl -O -J https://spideroak.com/releases/semaphor/debian
RUN dpkg -i semaphor*.deb
RUN apt-get install -f

# Install python dependencies
ADD requirements.txt /src/requirements.txt
RUN cd /src; pip install -r requirements.txt

# Copy code
COPY . /src
WORKDIR /src

ENTRYPOINT ["python"]
CMD ["run.py"]