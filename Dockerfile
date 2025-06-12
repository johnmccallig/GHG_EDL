FROM --platform=linux/amd64 python:3.7

# Set up code directory
RUN mkdir -p /code
WORKDIR /code

# Install linux dependencies
RUN apt-get update \
    && apt-get install -y libssl-dev npm

RUN npm install n -g

RUN npm install -g ganache

COPY requirements.txt .

RUN pip install -r requirements.txt
#RUN pip install -r requirements-dev.txt

# Copy over edited brownie scripts to install director
# from https://stackoverflow.com/questions/68721661/eth-brownie-no-module-named-users-someuser 

COPY scripts.py .
RUN cp /code/scripts.py /usr/local/lib/python3.7/site-packages/brownie/project/scripts.py

