"""script to generate hospital data CSV"""

import csv
import os
from faker import Faker

faker = Faker()

# set seed to get same data every time
faker.seed_instance(42)

HOSPITALS = 10000
PROCEDURES = 100
OUTPUT_DIR = None

if os.path.exists("/app/output"):
    # container
    OUTPUT_DIR = "/app/output"
else:
    # locally
    OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")

output_file = os.path.join(OUTPUT_DIR, "hospitals_and_procedures.csv")
print(f"output_file: {output_file}")

# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Create a smaller list of procedure names to randomly assign to hospitals
procedure_names = [faker.bs() for _ in range(100)]

# Pre-generate all hospital data to avoid redundant faker calls
hospital_data = [
    (hospital_id, faker.company(), faker.address())
    for hospital_id in range(1, HOSPITALS + 1)
]

with open(output_file, mode="w", encoding="utf-8", newline="") as file:
    writer = csv.writer(file)

    # header
    writer.writerow(
        ["Hospital ID", "Hospital Name", "Location", "Procedure Name", "Cost", "Date"]
    )

    rows = []

    # Generate hospital and procedure data
    for hospital_id, hospital_name, location in hospital_data:
        for _ in range(PROCEDURES):
            procedure_name = faker.random_element(procedure_names)
            cost = faker.random_number(digits=4)
            procedure_date = faker.date_this_year()
            rows.append(
                [
                    hospital_id,
                    hospital_name,
                    location,
                    procedure_name,
                    cost,
                    procedure_date,
                ]
            )

        # write in batches of 100k rows to reduce memory usage
        if len(rows) >= 100000:
            writer.writerows(rows)
            rows.clear()

    # write any remaining rows
    if rows:
        writer.writerows(rows)

print(f"CSV file '{output_file}' generated successfully.")
