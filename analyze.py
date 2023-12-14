# Program which analyses driver comapred to their teammates using premade datasets
# Made by: Joona Manninen
import pandas as pd
import json
import warnings


# Function to calculate and update driver averages based on teammates' averages
def get_new_average(dataframe, driver_averages, num):
    # Create a new DataFrame to store updated data
    new_dataframe = pd.DataFrame(
        columns=["driverid", "driver_name", "result", "average"]
    )

    # Iterate through each row in the input DataFrame
    for index, row in dataframe.iterrows():
        driver_id = row["driverid"]
        driver_name = row["driver_name"]
        results_str = row["result"]
        old_average = float(row["average"])

        result_list = []
        counter = 0
        total_time = 0

        if len(results_str) == 2 and check == 0:
            # Create a new data entry for driver who doesn't have results.
            new_data = {
                "driverid": driver_id,
                "driver_name": driver_name,
                "result": [],
                "average": 1.0,
            }
        elif len(results_str) == 0:
            # Create a new data entry for driver who doesn't have results.
            new_data = {
                "driverid": driver_id,
                "driver_name": driver_name,
                "result": [],
                "average": 1.0,
            }
        else:
            # Check if 'result' column is a JSON string or already parsed list
            if check == 0:
                results = json.loads(results_str)
            else:
                results = results_str

            # Iterate through each result item in the results list. This is where driver results are stored and we go through them one by one.
            for result_item in results:
                time = result_item["time"]
                tm_id = result_item["tmId"]
                # When driver doesn't have teammate
                if tm_id == -1:
                    product = time
                    # Adding the new result to the list.
                    result_list.append({"time": product, "tmId": tm_id})
                    total_time = product + total_time
                    counter += 1
                # When driver has teammate
                else:
                    tm_average = driver_averages.get(tm_id, None)

                    if tm_average is not None:
                        # Product is the drivers time multiplied by his teammate average.
                        product = time * tm_average
                        # Adding the new result to the list.
                        result_list.append({"time": product, "tmId": tm_id})
                        total_time = product + total_time
                        counter += 1

            new_average = total_time / counter
            # Update the driver's average
            if old_average < new_average:
                average = old_average + pow(abs(1 - new_average), num)
            else:
                average = old_average - pow(abs(1 - new_average), num)

            # Create a new data entry for the updated driver
            new_data = {
                "driverid": driver_id,
                "driver_name": driver_name,
                "result": result_list,
                "average": round(average, 6),
            }

        warnings.simplefilter(action="ignore", category=FutureWarning)
        # Append the new data to the new DataFrame
        new_dataframe = new_dataframe.append(new_data, ignore_index=True)

    # Move this line outside of the if condition
    return new_dataframe


# Function to fix JSON-like strings by replacing single quotes with double quotes
def fix_json_string(json_str):
    return json_str.replace("'", '"')


champions_list = [
    "hamilton",
    "rosberg",
    "alonso",
    "raikkonen",
    "farina",
    "fangio",
    "ascari",
    "hawthorn",
    "jack_brabham",
    "hill",
    "phil_hill",
    "damon_hill",
    "surtees",
    "clark",
    "hulme",
    "rindt",
    "stewart",
    "emerson_fittipaldi",
    "hunt",
    "lauda",
    "mario_andretti",
    "scheckter",
    "keke_rosberg",
    "piquet",
    "senna",
    "mansell",
    "prost",
    "michael_schumacher",
    "villeneuve",
    "hakkinen",
    "button",
    "max_verstappen",
    "vettel",
    "jones",
]

# Create an empty DataFrame to store the updated results
new_results_df = pd.DataFrame(columns=["driverid", "driver_name", "result", "average"])

# Reading the dataframes from CSV files
results_df = pd.read_csv("./data/driver_results.csv")
qualifying_results_df = pd.read_csv("./data/driver_qualifying_results.csv")

driver_averages = {row["driverid"]: row["average"] for _, row in results_df.iterrows()}
qualifying_averages = {
    row["driverid"]: row["average"] for _, row in qualifying_results_df.iterrows()
}
# Fixing the result column
results_df["result"] = results_df["result"].apply(fix_json_string)
qualifying_results_df["result"] = qualifying_results_df["result"].apply(fix_json_string)
# Getting driver data
driver_info_df = pd.read_csv("./data/drivers.csv")
selected_columns = driver_info_df[["driverRef", "surname", "forename"]]


check = 0
counter = 1

# Get the initial updated results DataFrame
new_results_df = get_new_average(results_df, driver_averages, counter)
new_qualifying_results_df = get_new_average(
    qualifying_results_df, qualifying_averages, counter
)

qualifying_averages = {
    row["driverid"]: row["average"] for _, row in qualifying_results_df.iterrows()
}

driver_averages = {
    row["driverid"]: row["average"] for _, row in new_results_df.iterrows()
}

check = 1

# Iterate the counter and update the results DataFrame
while counter < 20:
    counter += 1
    new_results_df = get_new_average(new_results_df, driver_averages, counter)

    driver_averages = {
        row["driverid"]: row["average"] for _, row in new_results_df.iterrows()
    }

merged_data = new_results_df.merge(
    selected_columns, left_on="driver_name", right_on="driverRef", how="left"
)
new_results_df = new_results_df.sort_values(by="average", ascending=False)


# Filter the merged DataFrame to keep only drivers in the champions_list
filtered_data = merged_data[merged_data["driver_name"].str.lower().isin(champions_list)]

# Rename the columns if needed
filtered_data = filtered_data.rename(
    columns={
        "forename": "Driver Forename",
        "surname": "Driver Surname",
        "average": "Average",
    }
)

# Dropping useless columns
filtered_data.drop(["driverRef"], axis=1, inplace=True)
filtered_data.drop(["driverid"], axis=1, inplace=True)
# Adding analyzed races column which shiws how many races was analyzed for each friver
filtered_data["Analyzed_races"] = filtered_data["result"].apply(lambda x: len(x))
filtered_data = filtered_data.sort_values(by="Average")
# Reset the index after sorting
filtered_data = filtered_data.reset_index(drop=True)
filtered_data = filtered_data[
    ["Driver Surname", "Driver Forename", "driver_name", "Average", "Analyzed_races"]
]

filtered_data = filtered_data[filtered_data["Analyzed_races"] > 35]
filtered_data.to_csv("./results/final_results_over_35.csv", index=False)

print(filtered_data)


##########################################
# QUALIFYING TIMES
##########################################


counter = 1
# Iterating qualifying times and calculating new averages.
while counter < 15:
    counter += 1
    new_qualifying_results_df = get_new_average(
        new_qualifying_results_df, qualifying_averages, counter
    )

    qualifying_averages = {
        row["driverid"]: row["average"]
        for _, row in new_qualifying_results_df.iterrows()
    }


merged_qualifying_data = new_qualifying_results_df.merge(
    selected_columns, left_on="driver_name", right_on="driverRef", how="left"
)

# Filter the merged DataFrame to keep only drivers in the champions_list
filtered_qualifying_data = merged_qualifying_data[
    merged_qualifying_data["driver_name"].str.lower().isin(champions_list)
]

# Rename the columns if needed
filtered_qualifying_data = filtered_qualifying_data.rename(
    columns={
        "forename": "Driver Forename",
        "surname": "Driver Surname",
        "average": "Average",
    }
)

# Drop any redundant columns
filtered_qualifying_data.drop(["driverRef"], axis=1, inplace=True)
filtered_qualifying_data.drop(["driverid"], axis=1, inplace=True)
filtered_qualifying_data["Analyzed_races"] = filtered_qualifying_data["result"].apply(
    lambda x: len(x)
)
filtered_qualifying_data = filtered_qualifying_data.sort_values(by="Average")
# Reset the index after sorting
filtered_qualifying_data = filtered_qualifying_data.reset_index(drop=True)
filtered_qualifying_data = filtered_qualifying_data[
    ["Driver Surname", "Driver Forename", "driver_name", "Average", "Analyzed_races"]
]

print(filtered_qualifying_data)


filtered_qualifying_data.to_csv("./results/final_qualifying_results.csv", index=False)
