# Sample Data System Engineering Project

Welcome to the **Sample Data System Engineering Project**. This project demonstrates a scalable data pipeline using a
combination of PostgreSQL, PySpark, ClickHouse, and monitoring tools like Prometheus and Grafana.

## Table of Contents

- [Project Overview](#project-overview)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
    - [Prerequisites](#prerequisites)
    - [Cloning and Navigating the Repository](#cloning-and-navigating-the-repository)
    - [Building the Spark Image](#building-the-spark-image)
    - [Starting the Services](#starting-the-services)
- [Directory and File Descriptions](#directory-and-file-descriptions)
- [Key Components and Modules](#key-components-and-modules)
- [Monitoring](#monitoring)
- [Usage](#usage)
- [Acknowledgements](#acknowledgements)

## Project Overview

The purpose of this project is to design and implement a data pipeline that:

1. **Generates synthetic data** with intentional defects.
2. **Processes the data** using PySpark to clean, transform, and join datasets.
3. **Stores the cleaned data** into a high-performance database (ClickHouse).
4. **Monitors the entire system** to ensure data consistency and resource health.

## Project Structure

```plaintext
Internship_project/
├── clickhouse/
│   └── create_clickhouse_tables.sh  # Script to create ClickHouse tables
├── data_generator/
│   ├── data_generator.py       # Script to generate synthetic data
│   ├── Dockerfile              # Dockerfile to build the data generator service
│   └── requirements_data.txt   # Dependencies for data generator
├── prometheus/
│   └── prometheus.yml          # Prometheus configuration file for monitoring
├── spark/
│   ├── apps/
│   │   └── transform.py        # Main PySpark script for data processing
│   ├── jars/                   # JAR files for JDBC connectivity
│   ├── Dockerfile              # Custom Dockerfile to build Spark image
│   ├── requirements_spark.txt  # Dependencies for PySpark
│   └── start-spark.sh          # Script to start Spark services
├── .gitignore                  # Git ignore file
├── docker-compose.yml          # Main Docker Compose file to orchestrate services
└── README.md                   # Project documentation (this file)
```

## Setup Instructions

### Prerequisites

- Docker and Docker Compose installed on your system.
- Adequate system resources to run multiple Docker containers (e.g., PostgreSQL, Spark, ClickHouse, Prometheus, etc.).

### Cloning and Navigating the Repository

1. **Clone the repository**:
   ```bash
   git clone https://github.com/mmz1380/sample-data-system-engineering-project.git
   ```

2. **Navigate to the project root**:
   ```bash
   cd sample-data-system-engineering-project
   ```

### Building the Spark Image

This project uses a **custom-built Spark image**. You need to build this image locally with the following command:

```bash
docker build -t our-own-apache-spark:3.4.0 ./spark
```

This command builds the custom Spark image and tags it as `our-own-apache-spark:3.4.0`. The Dockerfile in the `./spark`
directory handles the necessary installations and configurations.

### Starting the Services

To bring up the entire stack of services, run:

```bash
docker-compose up --build
```

This command starts all services in the background. You can check the status of the services using:

```bash
docker-compose ps
```

**Note:** The ClickHouse Exporter will not work due to certain limitations. Please keep this in mind while setting up
monitoring.

## Directory and File Descriptions

- **`clickhouse/create_clickhouse_tables.sh`**: A shell script to create necessary tables in ClickHouse.
- **`data_generator/`**: Contains the logic for generating synthetic data.
    - **`data_generator.py`**: Generates synthetic datasets with potential defects and injects them into PostgreSQL.
    - **`Dockerfile`**: Builds a Docker image for running the data generator service.
    - **`requirements_data.txt`**: Lists the dependencies for the data generator.
- **`prometheus/`**: Contains Prometheus configuration for monitoring.
    - **`prometheus.yml`**: Configuration file for Prometheus to define scraping targets and settings.
- **`spark/`**: Contains the PySpark data processing logic.
    - **`apps/transform.py`**: Main PySpark script to read, clean, transform, and join datasets.
    - **`jars/`**: Stores necessary JAR files for JDBC connectivity to PostgreSQL and ClickHouse.
    - **`Dockerfile`**: Custom Dockerfile to build the Spark image.
    - **`requirements_spark.txt`**: Lists the dependencies for running PySpark.
    - **`start-spark.sh`**: Script to start Spark master and worker services.
- **`docker-compose.yml`**: Defines all the services and containers required for the project, including PostgreSQL,
  Spark, ClickHouse, Prometheus, Grafana, and other essential services.

## Key Components and Modules

1. **Data Generation**:
    - `data_generator/data_generator.py` generates synthetic data and injects it into PostgreSQL. The data includes
      details of persons and houses, each with potential defects for testing the transformation process.

2. **Data Transformation and Processing**:
    - `spark/apps/transform.py` reads data from PostgreSQL, corrects defects, joins datasets, and writes the cleaned
      data to ClickHouse.

3. **Custom Spark Build**:
    - The custom-built Spark image (tagged `our-own-apache-spark:3.4.0`) is crucial for running the PySpark scripts with
      necessary configurations and dependencies.

## Monitoring

The project includes monitoring using **Prometheus** and **Grafana** to track:

- **Resource Usage**: Monitors CPU, memory, and container status using Prometheus and Node Exporter.
- **Custom Metrics**: Monitors specific job metrics (e.g., number of rows processed, new rows inserted) exposed by the
  PySpark script.

To access Prometheus, go to: `http://localhost:9090/`

To access Grafana, go to: `http://localhost:3000/` (default credentials: `admin` / `admin`).

**Important**: The ClickHouse Exporter service is included but is known not to work in this setup due to certain
limitations.

## Usage

### Starting the Pipeline

1. **Start all services** using Docker Compose:
   ```bash
   docker-compose up -d
   ```

2. **Monitor the data pipeline** using Prometheus and Grafana as explained above.

3. **Inspect PostgreSQL and ClickHouse** to verify data consistency.

### Stopping the Services

To stop all services:

```bash
docker-compose down
```

## Acknowledgements

This project is inspired by the idea of creating a scalable and reliable data pipeline for batch data processing and
monitoring. It uses a range of technologies to achieve this goal, including Docker, PySpark, PostgreSQL, ClickHouse,
Prometheus, and Grafana.

**GitHub Repository**:
[Sample Data System Engineering Project](https://github.com/mmz1380/sample-data-system-engineering-project)
