# Program which calculates drivers level compared to their teammate. Data is from Ergast Database
# Made by: Joona Manninen
import pandas as pd
import warnings


# Function to get the teammates of a driver in a specific race
def get_teammates(driver_id, race_id):
    # Filter the result data for the specified driverId and raceId
    driver_race_data = qualifying_data[
        (qualifying_data["driverId"] == driver_id)
        & (qualifying_data["raceId"] == race_id)
    ]

    if not driver_race_data.empty:
        # Get the constructorId of the specified driver in the specified race
        constructor_id = driver_race_data.iloc[0]["constructorId"]

        # Find the teammate(s) with the same raceId and constructorId (excluding the specified driver)
        teammates = qualifying_data[
            (qualifying_data["raceId"] == race_id)
            & (qualifying_data["constructorId"] == constructor_id)
            & (qualifying_data["driverId"] != driver_id)
        ]

        # Extract teammate driverIds from the teammates DataFrame
        teammate_ids = teammates["driverId"].tolist()

        if len(teammate_ids) == 0:
            return -1

        return teammate_ids[0]

    return None  # No data found for the specified driverId and raceId


# Function to get the list of unique raceIds for a specific driver
def driver_races(driver):
    # Filter the result data for the specified driverId
    driver_data = qualifying_data[qualifying_data["driverId"] == driver]

    # Get a list of unique raceIds for the specified driver
    unique_race_ids = driver_data["raceId"].unique()

    return unique_race_ids


# Convert the time column to float representing seconds
def time_to_seconds(
    time_str,
):
    time_str = str(time_str)

    if time_str == "nan":
        return 0

    parts = time_str.split(":")

    if parts[0] == "\\N":
        return 0

    minutes = int(parts[0])
    seconds = float(parts[1])
    return minutes * 60 + seconds


# Function which makes the comparison between laptimes.
def compare_times(driver_id, race_id, teammate_id):
    if teammate_id == -1:
        return -1
    # Calculate race result times
    driver_race_data = qualifying_data[
        (qualifying_data["raceId"] == race_id)
        & (qualifying_data["driverId"] == driver_id)
    ]
    teammate_race_data = qualifying_data[
        (qualifying_data["raceId"] == race_id)
        & (qualifying_data["driverId"] == teammate_id)
    ]
    # When driver doesn't have result we return -1 and skip to the next iteration of loop.
    if driver_race_data.iloc[0]["q1"] == 0:
        return -1

    if teammate_race_data.iloc[0]["q1"] == 0 and driver_race_data.iloc[0]["q1"] != 0:
        return -1

    if not driver_race_data.empty:
        # Taking the best qualifying time from driver
        driver_finish_time = driver_race_data.iloc[0]["q1"]

    else:
        driver_finish_time = None

    if not teammate_race_data.empty:
        # Taking the best qualifying time from teammate
        teammate_finish_time = teammate_race_data.iloc[0]["q1"]

    else:
        teammate_finish_time = None

    if driver_finish_time is not None and teammate_finish_time is not None:
        result = driver_finish_time / teammate_finish_time
    else:
        result = 1.0  # Default result if data is missing

    if result < 0.9 or result > 1.1:
        return 1

    return result


# Function to get the driver's name based on driverId
def get_driver_name(driver_id):
    driver_info = driver_data[driver_data["driverId"] == driver_id]
    if not driver_info.empty:
        return driver_info.iloc[0]["driverRef"]
    else:
        return "Unknown"


# Create an empty DataFrame to store results
results_df = pd.DataFrame(columns=["driverid", "driver_name", "result", "average"])

# Initialize a dictionary to store raceId to base_result_str mappings
race_results_dict = {}

# Read driver, lap time, and result data from CSV files
driver_data = pd.read_csv("./data/drivers.csv")

qualifying_data = pd.read_csv("./data/qualifying.csv")

# Changing the "time" column data to seconds.
qualifying_data["q1"] = qualifying_data["q1"].apply(time_to_seconds)
qualifying_data["q2"] = qualifying_data["q2"].apply(time_to_seconds)
qualifying_data["q3"] = qualifying_data["q3"].apply(time_to_seconds)

# Get unique driver IDs
unique_drivers = qualifying_data["driverId"].unique()


# Loop through each unique driver
for i in range(len(unique_drivers)):
    sum = 0
    counter = 0
    list = []

    # All raceIds driver has done
    all_driver_races = driver_races(unique_drivers[i])

    # Loop through each race for the current driver
    for j in range(len(all_driver_races)):
        # Getting teammates id

        teammate_id = get_teammates(unique_drivers[i], all_driver_races[j])

        a = compare_times(unique_drivers[i], all_driver_races[j], teammate_id)

        if a == -1:
            continue

        counter += 1
        sum = a + sum

        results = {"time": a, "tmId": teammate_id}
        list.append(results)

    name = get_driver_name(unique_drivers[i])

    # Checking if driver got any values
    if counter == 0:
        counter = 1
        sum = 1.0

    # Calculate the average lap time for the current driver
    average = sum / counter

    new_data = {
        "driverid": unique_drivers[i],
        "driver_name": name,
        "result": list,
        "average": average,
    }

    # Append the new data to the results DataFrame
    warnings.simplefilter(action="ignore", category=FutureWarning)
    results_df = results_df.append(new_data, ignore_index=True)

# Save the results DataFrame to a CSV file
results_df.to_csv("./data/driver_qualifying_results.csv", index=False)

# Print the results DataFrame
print(results_df)
