# from docker hub we take python:3 image into our docker container
FROM python:3.10-slim-buster

# this will make a folder in docker container
WORKDIR /backend-flask

# copy the file from current foolder to container
COPY requirements.txt requirements.txt

# runs the below cmd inside container
RUN pip3 install -r requirements.txt

# copies /backend-flask to /backend-flask inside container
COPY . .

# sets container env variables
ENV FLASK_ENV=development

EXPOSE ${PORT}
CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0", "--port=4567"]