# FROM buildpack-deps:bullseye
ARG HAYSTACK_BASE_IMAGE=deepset/haystack:cpu-v1.13.2
FROM $HAYSTACK_BASE_IMAGE




# change active user to root
USER root 

# create the app directory
RUN mkdir -p /usr/src/app/

# set mssql as owner of the app directory
RUN chown root /usr/src/app/


# Setting Home Directory for containers
WORKDIR /usr/src/app

# Installing python dependencies
COPY requirements.txt /usr/src/app/


RUN pip install --no-cache-dir -r requirements.txt

# Copying src code to Container
COPY . /usr/src/app




# Setting Persistent data
VOLUME ["/app-data"]

# Running Python Application
ENTRYPOINT ["./gunicorn.sh"]
CMD ["python3", "server.py"]
