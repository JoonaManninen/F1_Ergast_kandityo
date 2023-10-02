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
                average = old_average + abs(pow((1 - new_average), num))
            else:
                average = old_average - abs(pow((1 - new_average), num))

            # Create a new data entry for the updated driver
            new_data = {
                "driverid": driver_id,
                "driver_name": driver_name,
                "result": result_list,
                "average": average,
            }

        warnings.simplefilter(action="ignore", category=FutureWarning)
        # Append the new data to the new DataFrame
        new_dataframe = new_dataframe.append(new_data, ignore_index=True)

    # Move this line outside of the if condition
    return new_dataframe


# Function to fix JSON-like strings by replacing single quotes with double quotes
def fix_json_string(json_str):
    return json_str.replace("'", '"')


# Create an empty DataFrame to store the updated results
new_results_df = pd.DataFrame(columns=["driverid", "driver_name", "result", "average"])

# Read the original results DataFrame and create a dictionary of driver averages
results_df = pd.read_csv("driver_results.csv")
driver_averages = {row["driverid"]: row["average"] for _, row in results_df.iterrows()}

check = 0
results_df["result"] = results_df["result"].apply(fix_json_string)
counter = 1

# Get the initial updated results DataFrame
new_results_df = get_new_average(results_df, driver_averages, counter)

print(new_results_df)

check = 1


# Iterate the counter and update the results DataFrame
while counter < 50:
    counter += 1
    new_results_df = get_new_average(new_results_df, driver_averages, counter)


# Extract the "driver_name" and "average" columns from the final DataFrame
driver_average_dict = new_results_df[["driver_name", "average"]].to_dict(
    orient="records"
)

sorted_data = sorted(driver_average_dict, key=lambda x: x["average"])

# Open a file for writing
with open("driver_averages.txt", "w") as file:
    # Iterate through the dictionary and write each entry as a separate line
    for item in sorted_data:
        file.write(f"Driver: {item['driver_name']}, Average: {item['average']}\n")

# Print each player and their average in separate rows
for item in sorted_data:
    print(f"Driver: {item['driver_name']}, Average: {item['average']}")
