"""A testing module used to generate dummy info for the `user_ratings.json` database."""
import json
import random

def generate_user_id():
    return str(random.randint(100000000001, 999999999999))

def generate_random_ratings():
    return random.randint(1, 5)

def generate_database(num_entries):
    database = {"738290097170153472": {}}
    for _ in range(num_entries):
        user_id = generate_user_id()
        rating = generate_random_ratings()
        database["738290097170153472"][user_id] = rating
        print(f"Test ID: {user_id} | Generated Rating: {rating}")
    return database

def save_database(database, filename):
    with open(filename, 'w') as f:
        json.dump(database, f, indent=4)

def main():
    num_entries = 1000000
    database = generate_database(num_entries)
    save_database(database, "db/user_ratings.json")
    print("Database created successfully!")

main()
