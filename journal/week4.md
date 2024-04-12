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

to list tables ` \l `

to create database ` create database cuddur `

create schema.sql as paste all the sql querires you want to run.

to execute things in schema.sql run below cmd in backend-flask directory
` psql cruddur < db/schema.sql -h localhost -U postgres `
