# Week 1 — App Containerization

## Docker ext for VSCode
I didn't get docker ext preinstalled in gitpod. so installed it from extensions.

# create a Dockerfile in backend-flask folder
inside it copy the flow it needs to execute
```
FROM python:3.10-slim-buster
WORKDIR /backend-flask
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
ENV FLASK_ENV=development
EXPOSE ${PORT}
CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0", "--port=4567"]
```

and save the file

after that open terminal goto backend-flask cd into it and run 
`python3 -m flask run --host=0.0.0.0 --port=4567`

and this will run flask app on a host port 4567

wait for 30 secs or so and goto ports tab in termial and see if there is an url with lock symbol. unlock it and open the url in new tab.

we will get 404 error and that's fine.

to make it work, create system env variables to access them and run.
below are the steps it do it
- `export BACKEND_URL="*"`
- `export FRONTEND_URL="*"`

it delete those env variables
- `unset BACKEND_URL`
- `unset FRONTEND_URL`

build docker image wit dockerfile with below command
`docker build -t backend-flask ./backend-flask`

after build we need to run te docker
`docker run --rm -p 4567:4567 -it backend-flask`

after run goto ports tab and see if the lock is unlocked. and click the url and 404 is expected.

to set the env variables there are few ways to do it
- first set env in local machine export FRONTEND_URL = "*" export BACKEND_URL = "*" and then run
`docker run --rm -p 4567:4567 -it -e FRONTEND_URL -e BACKEND_URL backend-flask`
- second way is to use directly
`docker run --rm -p 4567:4567 -it -e FRONTEND_URL="*" -e BACKEND_URL="*" backend-flask`
- and we can create these varibles in dockerfile so it won't fail while conatinerizing it
`ENV FRONETEND_URL="*"`
`ENV BACKEND_URL="*"`

# delete image
`docker image rm backend-flask --force`

## Create a new Dockerfile for frontend
copt the below code into frontend-react-js folder
```
FROM node:16.18
ENV PORT=300
COPY . /frontend-react-js
WORKDIR /frontend-react-js
RUN npm install
EXPOSE ${PORT}
CMD ["npm", "start"]
```

# build container
`docker build -t frontend-react-js ./frontend-react-js`

# run container
`docker run -p 3000:3000 -d frontend-react-js`

# multiple containers
docker-composer.yml

```
version: "1.0"
services:
  backend-flask:
    environment:
      FRONTEND_URL: "https://3000-${GITPOD_WORKSPACE_ID}.${GITPOD_WORKSPACE_CLUSTER_HOST}"
      BACKEND_URL: "https://4567-${GITPOD_WORKSPACE_ID}.${GITPOD_WORKSPACE_CLUSTER_HOST}"
    build: ./backend-flask
    ports:
      - "4567:4567"
    volumes:
      - ./backend-flask:/backend-flask
  frontend-react-js:
    environment:
      REACT_APP_BACKEND_URL: "https://4567-${GITPOD_WORKSPACE_ID}.${GITPOD_WORKSPACE_CLUSTER_HOST}"
    build: ./frontend-react-js
    ports:
      - "3000:3000"
    volumes:
      - ./frontend-react-js:/frontend-react-js
```

## new addition to docker-compose.yml
```
dymanodb-local:
    user: root
    command: "-jar DynamoDBLocal.jar --sharedDb -dbPath ./data"
    image: "amazon/dynamodb-local:latest"
    container_name: dynamodb-local
    ports:
      - "8000:8000"
    volumes:
      - ".docker/dynamodb:/home/dynamodblocal/data"
    working_dir: /home/dynamodblocal
  db:
    image: postgres:13-alpine
    restart: always
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - db:/var/lib/postgresql/data
```

after adding this run `docker compose up` and make ports public

in new terminal run `psql -Upostgres -h localhost`
password is password