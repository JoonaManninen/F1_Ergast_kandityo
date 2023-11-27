# Program which compares races times of driver to their teammate to get their level. Data is from Ergast Database
# Made by: Joona Manninen
import pandas as pd
import warnings


# Function to get the teammates of a driver in a specific race
def get_teammates(driver_id, race_id):
    # Filter the result data for the specified driverId and raceId
    driver_race_data = result_data[
        (result_data["driverId"] == driver_id) & (result_data["raceId"] == race_id)
    ]

    if not driver_race_data.empty:
        # Get the constructorId of the specified driver in the specified race
        constructor_id = driver_race_data.iloc[0]["constructorId"]

        # Find the teammate(s) with the same raceId and constructorId (excluding the specified driver)
        teammates = result_data[
            (result_data["raceId"] == race_id)
            & (result_data["constructorId"] == constructor_id)
            & (result_data["driverId"] != driver_id)
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
    driver_data = result_data[result_data["driverId"] == driver]

    # Get a list of unique raceIds for the specified driver
    unique_race_ids = driver_data["raceId"].unique()

    return unique_race_ids


# Convert the time column to float representing seconds
def time_to_seconds(time_str):
    parts = time_str.split(":")
    minutes = int(parts[0])
    seconds = float(parts[1])
    return minutes * 60 + seconds


# Function which changes the data from time column to seconds
def resulttime_to_seconds(row):
    time_str = row["time"]
    race_id = row["raceId"]
    status = row["statusId"]
    fastestLap = row["fastestLapTime"]

    # Drivers time is \N when he was lapped or did not finish
    if time_str == "\\N":
        # Checking if driver was lapped using statusId
        # StatusIds correspond as follows "11 = +1 Lap", "12 = +2 Laps", "13 = +3 Laps,"" "14 = +4 Laps", "15 = +5 Laps", "16 = +6 Laps", "17 = +7 Laps", "18 = +8 Laps", "19 = +9 Laps"
        # First we check if the statusId falls in the correct range
        if int(status) < 20 and int(status) > 10:
            base_time = race_results_dict.get(race_id)
            # Changing the fastest laptime to second for the calculation
            # Split the time string by ":"

            time_parts = fastestLap.split(":")

            # Format: minutes:seconds.milliseconds

            # Some races don't have fastest laptimes so calculation cannot be done
            if time_parts[0] == "\\N":
                return 0
            else:
                seconds_milliseconds = time_parts[1].split(".")
                minutes = int(time_parts[0])
                seconds, milliseconds = int(seconds_milliseconds[0]), int(
                    seconds_milliseconds[1]
                )
                fastLap = (minutes * 60) + seconds + (milliseconds / 1000)

            # Calculating the estimated time that driver was behind the first finisher using fastest laptime.
            if int(status) == 11:
                base_time = race_results_dict.get(race_id)
                base_time = int(base_time[0])
                total_seconds = base_time + fastLap
            elif int(status) == 12:
                base_time = race_results_dict.get(race_id)
                base_time = int(base_time[0])
                total_seconds = base_time + fastLap * 2
            else:
                base_time = race_results_dict.get(race_id)
                base_time = int(base_time[0])
                total_seconds = base_time + fastLap * 3
            return total_seconds
        else:
            return 0

    # Only race winners time in race is formatted like hours:minutes:second.milliseconds and other are formatted like +5.56.
    if race_id in race_results_dict:
        if time_str.startswith("+"):
            time_str = time_str[1:]
            time_str = time_str.split(":")
            if len(time_str) == 2:
                # Format: minutes:seconds.milliseconds
                seconds_milliseconds = time_str[1].split(".")

                if len(seconds_milliseconds) == 2:
                    # Format second.milliseconds
                    minutes = int(time_str[0])
                    seconds, milliseconds = int(seconds_milliseconds[0]), int(
                        seconds_milliseconds[1]
                    )
                    base_time = race_results_dict.get(race_id)
                    base_time = int(base_time[0])
                    total_seconds = (
                        base_time + (minutes * 60) + seconds + (milliseconds / 1000)
                    )
                else:
                    # Format minutes:second
                    minutes = int(time_str[0])
                    seconds = int(time_str[1])
                    base_time = race_results_dict.get(race_id)
                    base_time = int(base_time[0])
                    total_seconds = base_time + (minutes * 60) + seconds
            else:
                # Format: seconds.milliseconds
                time_str = time_str[0]
                seconds_milliseconds = time_str.split(".")
                seconds, milliseconds = int(seconds_milliseconds[0]), int(
                    seconds_milliseconds[1]
                )
                base_time = race_results_dict.get(race_id)
                base_time = int(base_time[0])
                total_seconds = base_time + seconds + (milliseconds / 1000)
        else:
            return 0

    else:
        # Split the time string by ":"
        time_parts = time_str.split(":")

        if len(time_parts) == 3:
            # Format: hours:minutes:seconds.milliseconds
            seconds_milliseconds = time_parts[2].split(".")
            hours, minutes = int(time_parts[0]), int(time_parts[1])
            seconds, milliseconds = int(seconds_milliseconds[0]), int(
                seconds_milliseconds[1]
            )
            total_seconds = (
                (hours * 3600) + (minutes * 60) + seconds + (milliseconds / 1000)
            )
        else:
            # Format: minutes:seconds.milliseconds
            seconds_milliseconds = time_parts[1].split(".")
            minutes = int(time_parts[0])
            seconds, milliseconds = int(seconds_milliseconds[0]), int(
                seconds_milliseconds[1]
            )
            total_seconds = (minutes * 60) + seconds + (milliseconds / 1000)

        # RaceId doesn't exist, create a new entry with a list containing the base_result_str
        race_results_dict[race_id] = [total_seconds]
    return total_seconds


# Function which makes the comparison between laptimes.
def compare_times(driver_id, race_id, teammate_id, laptime_raceId):
    if race_id in laptime_raceId:
        # Driver time
        dtime = 0
        # Teammate time
        tmtime = 0

        if teammate_id == -1:
            return 1
        # Getting drivers lap data
        driver_laps = lap_time_data[
            (lap_time_data["raceId"] == race_id)
            & (lap_time_data["driverId"] == driver_id)
        ]
        # Getting teammates lap data
        teammate_laps = lap_time_data[
            (lap_time_data["raceId"] == race_id)
            & (lap_time_data["driverId"] == teammate_id)
        ]

        laps = min(len(driver_laps), len(teammate_laps))

        if laps == 0:
            return -1
        else:
            # Iterating through data to get laptimes and adding them up.
            for i in range(laps):
                dtime += driver_laps.iloc[i]["time"]
                tmtime += teammate_laps.iloc[i]["time"]

        result = dtime / tmtime

        return result
    # Situation when the race doesn't have laptime data
    else:
        if teammate_id == -1:
            return -1
        # Calculate race result times
        driver_race_data = result_data[
            (result_data["raceId"] == race_id) & (result_data["driverId"] == driver_id)
        ]
        teammate_race_data = result_data[
            (result_data["raceId"] == race_id)
            & (result_data["driverId"] == teammate_id)
        ]
        # When driver doesn't have result we return -1 and skip to the next iteration of loop.
        if driver_race_data.iloc[0]["time"] == 0:
            return -2

        if (
            teammate_race_data.iloc[0]["time"] == 0
            and driver_race_data.iloc[0]["time"] != 0
        ):
            return -3

        if not driver_race_data.empty:
            driver_finish_time = driver_race_data.iloc[0]["time"]
        else:
            driver_finish_time = None

        if not teammate_race_data.empty:
            teammate_finish_time = teammate_race_data.iloc[0]["time"]
        else:
            teammate_finish_time = None

        if driver_finish_time is not None and teammate_finish_time is not None:
            result = driver_finish_time / teammate_finish_time
        else:
            result = 1.0  # Default result if data is missing

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
driver_data = pd.read_csv("drivers.csv")
lap_time_data = pd.read_csv("lap_times.csv")
result_data = pd.read_csv("results.csv")

# Changing the "time" column data to seconds.
lap_time_data["time"] = lap_time_data["time"].apply(time_to_seconds)
result_data["time"] = result_data.apply(resulttime_to_seconds, axis=1)


# Get unique driver IDs
unique_drivers = driver_data["driverId"].unique()
# All the raceId's that are in the laptime_data, We can use this to check what method we need to use when comparing times
unique_race_ids = pd.unique(lap_time_data["raceId"])


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

        a = compare_times(
            unique_drivers[i], all_driver_races[j], teammate_id, unique_race_ids
        )

        if unique_drivers[i] == 579:
            print(teammate_id, "kek", a, "homo", all_driver_races[j])

        if a == -1 or -2 or -3:
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
results_df.to_csv("driver_results.csv", index=False)

# Print the results DataFrame
print(results_df)
