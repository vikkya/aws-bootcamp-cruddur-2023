# Week 4 — Postgres and RDS

instead of using UI to create db, we are using cli interface to create db with required options

```
aws rds create-db-instance \
  --db-instance-identifier cruddur-db-instance \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version  14.6 \
  --master-username root \
  --master-user-password huEE33z2Qvl383 \
  --allocated-storage 20 \
  --availability-zone ap-south-1a \
  --backup-retention-period 0 \
  --port 5432 \
  --no-multi-az \
  --db-name cruddur \
  --storage-type gp2 \
  --publicly-accessible \
  --storage-encrypted \
  --no-enable-performance-insights \
  --no-deletion-protection
```

check if we have postgres installed or not. if not then use gitpod.yml postgres commands to install.

goto postgres bash or any new bash
` psql -Upostgres --host localhost `

to run the above command make sure docker-compose.yml is up and running.

to list databases ` \l `

to create database ` create database cruddur; `

create schema.sql as paste all the sql querires you want to run.

to execute things in schema.sql run below cmd in backend-flask directory
` psql cruddur < db/schema.sql -h localhost -U postgres `


create db-create, db-drop, db-schema-load shell scripts in backend-flask\db folder

add table creation sql to schema.sql 

```
CREATE TABLE public.users (
  uuid UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  display_name text,
  handle text,
  cognito_user_id text,
  created_at TIMESTAMP default current_timestamp NOT NULL
);
```

```
CREATE TABLE public.activities (
  uuid UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  message text NOT NULL,
  replies_count integer DEFAULT 0,
  reposts_count integer DEFAULT 0,
  likes_count integer DEFAULT 0,
  reply_to_activity_uuid integer,
  expires_at TIMESTAMP,
  created_at TIMESTAMP default current_timestamp NOT NULL
);
```

## auto run all db, table creation and insertion

change db-setup permission to executable 
` chmod u+x ./bin/db-setup `
after that run ./bin/db-setup


## add layers to lambda
- create lambda function
- in lambda page left side check layers option
- create layer. name can be anything, architecture x86_64
- to upload a zip, 
  - download that package from pypi.org and for linux env check python version and download whl file
  - extract that whl file and copy that to a folder called python
  - zip the python folder (ex. layer.zip)
  - upload it to lambda layer
- in code tab go bottom of the page to layers
- and choose arn or custom layer
- add the arn or custom layer and version

this should do the job.
ref video [Video 1](https://www.youtube.com/watch?v=_TUNZuvjyDQ)
[Video 2](https://www.youtube.com/watch?v=lrEAu75zhNI)