import csv
import tomli_w

# Define the path to your CSV and TOML files
csv_file_path = 'testDataCopy.csv'
toml_file_path = 'convertedData.toml'
strToBool = {"True": True, "False": False, "true": True, "false": False, True: True, False: False, "1": True, "0": False, 1: True, 0: False}

# Function to convert CSV data to the required dictionary format
def csv_to_dict(csv_file_path: str) -> list[dict[str, object]]:
    with open(csv_file_path, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        print (reader)
        data_list = []
        for row in reader:
            print (row)
            # Assuming CSV columns match the required TOML structure
            # Convert and adjust the following line as per your CSV structure
            data = {
                "time": {
                    "elapsedTime": row["elapsedTime"],
                    "currentTime": row["serverTime"]
                },
                "valves": {
                    "xv1": strToBool.get(row["xv1"]),
                    "xv2": strToBool.get(row["xv2"]),
                    "xv3": strToBool.get(row["xv3"]),
                    "xv4": strToBool.get(row["xv4"]),
                    "xv5": strToBool.get(row["xv5"]),
                    "xv6": strToBool.get(row["xv6"]),
                    # Add other valves as per your CSV structure
                },
                "pressures": {
                    "pi1": float(row["pi1"]),
                    "pi2": float(row["pi2"]),
                    # Add other pressures as per your CSV structure
                },
                "temps": {
                    "t1": float(row["t1"]),
                    "t2": float(0),
                    # Add other temperatures as per your CSV structure
                },
                "loads": {
                    "tankMass": float(row["dm"]),
                    "thrust": float(row["l1"]),
                    # Add other loads as per your CSV structure
                }
            }
            data_list.append(data)
    return data_list

# Convert the CSV data to the required format
data_list = csv_to_dict(csv_file_path)

# Write the data to a TOML file
data = {"name": "testData", "content": data_list}
with open(toml_file_path, 'wb') as toml_file:
    tomli_w.dump(data, toml_file)