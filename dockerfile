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