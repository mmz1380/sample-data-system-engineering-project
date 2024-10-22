# Set-up tutorial for this docker compose

## Pulling and running images and data-dumper script

```bash
docker-compose up --build 
```

## Creating the Connector

After running the docker-compose up, use the following REST call to create a PostgreSQL connector:

#### Bash/WSL:

```bash
curl -X POST http://localhost:8083/connectors -H "Content-Type: application/json" -d '{
  "name": "postgres-connector",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "tasks.max": "1",
    "database.hostname": "postgres",
    "database.port": "5432",
    "database.user": "admin",
    "database.password": "password",
    "database.dbname": "internship_project",
    "database.server.name": "dbserver1",
    "table.whitelist": "public.persons,public.houses",
    "plugin.name": "pgoutput",
    "database.history.kafka.bootstrap.servers": "kafka:9092",
    "database.history.kafka.topic": "schema-changes.internship_project"
  }
}'
```

#### Powershell:

```bash
Invoke-WebRequest -Uri http://localhost:8083/connectors -Method Post -Headers @{"Content-Type"="application/json"} -Body '{
  "name": "postgres-connector",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "tasks.max": "1",
    "database.hostname": "postgres",
    "database.port": "5432",
    "database.user": "admin",
    "database.password": "password",
    "database.dbname": "internship_project",
    "database.server.name": "dbserver1",
    "table.whitelist": "public.persons,public.houses",
    "plugin.name": "pgoutput",
    "database.history.kafka.bootstrap.servers": "kafka:9092",
    "database.history.kafka.topic": "schema-changes.internship_project"
  }
}'
```

## Setting Up ClickHouse

After the containers are running, create the houses table in ClickHouse:

```sql
CREATE TABLE houses
(
    id                 UInt32,
    area               UInt32,
    number_of_bedroom  Float32,
    number_of_bathroom Float32,
    year               String,
    plot_size          UInt32,
    floor              UInt32,
    is_plot_owned      UInt8,
    parking_lot_owned  UInt32,
    is_single_unit     UInt8,
    person_id          UInt32,
    house_price        UInt32,
    full_name          String
) ENGINE = MergeTree()
ORDER BY id;
```

### Check Kafka Connect

Use the REST API to verify connectors:

```bash
curl http://localhost:8083/connectors
```