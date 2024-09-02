"""class for handling sending CSV data to Redis"""

import csv
import json
from flask import flash


class CsvToRedisLoader:
    """CsvToRedisLoader class"""

    HOSPITAL_ID = "Hospital ID"
    PROCEDURE_NAME = "Procedure Name"
    COST = "Cost"
    DATE = "Date"
    HOSPITAL_NAME = "Hospital Name"
    LOCATION = "Location"

    def __init__(self, **kwargs):
        """init redis conn and path to csv file"""
        self.redis_adapter = kwargs.get("redis_adapter")
        self.csv_file = kwargs.get("csv_file")
        self.log = kwargs.get("log")

        if self.csv_file:
            try:
                self.load_csv_to_redis()
            except Exception as e:
                self.log.error(f"Could not load csv file: {e}")

    def load_csv_to_redis(self):
        """read csv data into cache"""
        try:
            self.log.info(f"Starting to load CSV file: {self.csv_file}")
            with open(self.csv_file, mode="r", encoding="utf-8") as file:
                # reader reads each row as a dict
                reader = csv.DictReader(file)
                self._process_csv_rows(reader)
            self.log.info(f"Successfully loaded CSV file: {self.csv_file}")
        except FileNotFoundError:
            self._handle_error(f"The file {self.csv_file} does not exist.")
        except csv.Error as e:
            self._handle_error(f"Error processing CSV file: {e}")
        except Exception as e:
            self._handle_error(f"An unexpected error occurred: {e}")

    def _process_csv_rows(self, reader):
        """process each row and store in redis"""
        current_hospital_id = None
        hospital_data = {}

        for row in reader:
            hospital_id = row[self.HOSPITAL_ID]
            procedure = self._create_procedure_dict(row)

            if hospital_id == current_hospital_id:
                hospital_data["procedures"].append(procedure)
            else:
                # first time through, will eval to false so set current_hospital_id
                # otherwise new hospital, store the data via _store_hospital_data
                if current_hospital_id is not None:
                    self._store_hospital_data(current_hospital_id, hospital_data)

                current_hospital_id = hospital_id
                hospital_data = self._create_hospital_data_dict(row, procedure)

        if current_hospital_id is not None:
            self._store_hospital_data(current_hospital_id, hospital_data)

    def _create_procedure_dict(self, row):
        """dict for procedures"""
        return {
            "procedure_name": row[self.PROCEDURE_NAME],
            "cost": row[self.COST],
            "date": row[self.DATE],
        }

    def _create_hospital_data_dict(self, row, procedure):
        """create dict for hospital"""
        return {
            "hospital_name": row[self.HOSPITAL_NAME],
            "location": row[self.LOCATION],
            "procedures": [procedure],
        }

    def _store_hospital_data(self, hospital_id, hospital_data):
        """store hospital data in Redis"""
        self.redis_adapter.set(
            f"hospital:{hospital_id}",
            json.dumps(hospital_data),
        )

    def _handle_error(self, message):
        """log and flash errors"""
        self.log.error(message)
        flash(message, "danger")
