import math
import os
import psycopg2
from psycopg2.extras import execute_values
import time
import json
from faker import Faker
from datetime import datetime, timedelta
import random

fake = Faker()


def generate_persons_data(sample_size: int) -> list:
    persons = []
    for _ in range(sample_size):
        f_name = fake.first_name()
        l_name = fake.last_name()
        national_code = ''.join([str(random.randint(0, 9)) for i in range(10)])
        place_of_birth = {
            'lat': round(random.uniform(35.6, 35.8), 8),
            'long': round(random.uniform(51.24, 51.5), 8),
        }
        start_date = datetime.strptime('1950-01-01', '%Y-%m-%d')
        end_date = datetime.strptime('2000-12-31', '%Y-%m-%d')
        birthday = fake.date_between(start_date, end_date)
        timestamp = datetime.now()
        persons.append({
            'f_name': f_name,
            'l_name': l_name,
            'national_code': national_code,
            'place_of_birth': json.dumps(place_of_birth),
            'birthday': birthday,
            'time_stamp': timestamp,
        })
    return persons


def generate_houses_data(sample_size: int, owner_ids: list) -> list:
    houses = []
    owner_ids.append(None)
    for _ in range(sample_size):
        area = random.randint(60, 200)
        number_of_bedroom = float(random.randint(1, 4))
        number_of_bathroom = float(random.randint(2, 5) / 2)
        year = str(random.randint(2000, datetime.now().year))
        plot_size = random.randint(0, 60)
        floor = random.randint(0, 10)
        if plot_size != 0 and floor in [0, 1]:
            is_plot_owned = random.choice([True, False])
        else:
            is_plot_owned = False
        parking_lot_owned = random.randint(0, 5)
        is_single_unit = random.choice([True, False]) if floor in [0, 1] else False
        owner_id = random.choice(owner_ids) if owner_ids else None
        house_price = random.randint(70 * area, 180 * area)
        timestamp = datetime.now()
        houses.append({
            'area': area,
            'number_of_bedroom': number_of_bedroom,
            'number_of_bathroom': number_of_bathroom,
            'year': year,
            'plot_size': plot_size,
            'floor': floor,
            'is_plot_owned': is_plot_owned,
            'parking_lot_owned': parking_lot_owned,
            'is_single_unit': is_single_unit,
            'owner_id': owner_id,
            'house_price': house_price,
            'time_stamp': timestamp,
        })
    return houses


def generate_and_insert_data():
    db_host = os.getenv('DB_HOST', 'postgres')
    db_name = os.getenv('DB_NAME', 'internship_project')
    db_user = os.getenv('DB_USER', 'postgres')
    db_pass = os.getenv('DB_PASS', 'password')

    while True:
        try:
            conn = psycopg2.connect(
                host=db_host,
                database=db_name,
                user=db_user,
                password=db_pass
            )
            print(f"Connected to PostgreSQL and {db_name} database")
            break
        except Exception as e:
            print(f"Database connection error: {e}")
            print("Retrying...")
            time.sleep(2)
    cur = conn.cursor()

    try:
        cur.execute('''
            CREATE TABLE IF NOT EXISTS Persons (
                id SERIAL PRIMARY KEY,
                f_name VARCHAR(50),
                l_name VARCHAR(50),
                national_code VARCHAR(10) UNIQUE,
                place_of_birth JSON,
                birthday DATE,
                time_stamp TIMESTAMP
            )
        ''')
        conn.commit()
        print("Table 'Persons' created.")
    except Exception as e:
        print(f"Table 'Persons' creation error: {e}")

    try:
        cur.execute('''
            CREATE TABLE IF NOT EXISTS Houses (
                id SERIAL PRIMARY KEY,
                area INTEGER,
                number_of_bedroom FLOAT,
                number_of_bathroom FLOAT,
                year VARCHAR(4),
                plot_size INTEGER,
                floor INTEGER,
                is_plot_owned BOOLEAN,
                parking_lot_owned INTEGER,
                is_single_unit BOOLEAN,
                owner_id INTEGER REFERENCES persons(id),
                house_price BIGINT,
                time_stamp TIMESTAMP
            )
        ''')
        conn.commit()
        print("Table 'Houses' created.")
    except Exception as e:
        print(f"Table 'Houses' creation error: {e}")
    time.sleep(40)
    while True:
        num_persons = 7
        persons_data = generate_persons_data(num_persons)
        try:
            persons_records = [
                (p['f_name'], p['l_name'], p['national_code'], p['place_of_birth'], p['birthday'], p['time_stamp']) for
                p
                in persons_data]
            execute_values(cur, """
                INSERT INTO Persons (f_name, l_name, national_code, place_of_birth, birthday, time_stamp)
                VALUES %s
                RETURNING id
            """, persons_records)
            inserted_ids = [record[0] for record in cur.fetchall()]
            conn.commit()
            print(f"{num_persons} records inserted into 'persons' table.")
            cur.execute("""
                SELECT COUNT(*) FROM persons
            """)
            conn.commit()
            print(f"{cur.fetchone()[0]} records have been inserted into 'persons' table.")
        except Exception as e:
            print(f"Error inserting data into 'persons': {e}")
            conn.rollback()

        num_houses = 130
        try:
            houses_data = generate_houses_data(num_houses, inserted_ids)
            houses_records = [
                (
                    h['area'],
                    h['number_of_bedroom'],
                    h['number_of_bathroom'],
                    h['year'],
                    h['plot_size'],
                    h['floor'],
                    h['is_plot_owned'],
                    h['parking_lot_owned'],
                    h['is_single_unit'],
                    h['owner_id'],
                    h['house_price'],
                    h['time_stamp']
                ) for h in houses_data
            ]
            execute_values(cur, """
                INSERT INTO Houses (
                    area, number_of_bedroom, number_of_bathroom, year, plot_size, floor,
                    is_plot_owned, parking_lot_owned, is_single_unit, owner_id, house_price, time_stamp
                )
                VALUES %s
            """, houses_records)
            conn.commit()
            print(f"{num_houses} records inserted into 'houses' table.")
            cur.execute("""
                SELECT COUNT(*) FROM houses
            """)
            flag = False
            conn.commit()
            print(f"{cur.fetchone()[0]} records have been inserted into 'houses' table.")
        except Exception as e:
            print(f"Error inserting data into 'houses': {e}")
            conn.rollback()
        print()
        time.sleep(2)


if __name__ == '__main__':
    generate_and_insert_data()
