# F1_Ergast_kandityo

Repository contains CSV Database Tables which are used to analyze data to find out best f1 driver.
Database tables are from "http://ergast.com/mrd/db/".

generateData.py takes data from laptimes.csv and results.csv and calculates percent value for driver from every race.
Laptimes.csv is used for races starting from 1996 and for races before 1996 we use results.csv to calculate finish time.

Data is then written in driver_results.csv.
analyze.py is used to iterate through the data taken from driver_result.csv and come to conclusion who would be the best driver.

