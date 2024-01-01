# FROM alpine:latest
# RUN apk update
# RUN apk add py-pip
# RUN apk add --no-cache python3-dev 
# RUN ./energysage_venv/bin/activate
# WORKDIR /docker_app
# COPY . /docker_app
# RUN pip --no-cache-dir install -r requirements.txt
# CMD ["python3", "main.py"]


FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /docker_app
WORKDIR /docker_app
COPY requirements.txt /docker_app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . /docker_app
EXPOSE 3000
CMD [ "python", "main.py" ]