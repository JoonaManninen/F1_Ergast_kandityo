# F1_Ergast_kandityo

Repository contains CSV Database Tables which are used to analyze data to find out best f1 driver.
Database tables are from "http://ergast.com/mrd/db/".

generateData.py takes data from laptimes.csv and results.csv and calculates percent value for driver from every race.
Laptimes.csv is used for races starting from 1996 and for races before 1996 we use results.csv to calculate finish time.

Data is then written in driver_results.csv.
analyze.py is used to iterate through the data taken from driver_result.csv and come to conclusion who would be the best driver.

RESULTS

Forename	Firstname	Average	Analyzed races
Fangio	Juan	0.992707	16
Button	Jenson	0.99403	291
Ascari	Alberto	0.994388	11
Hamilton	Lewis	0.994537	314
Villeneuve	Jacques	0.995221	154
Hunt	James	0.995442	9
Hill	Damon	0.99555	72
Prost	Alain	0.995624	56
Surtees	John	0.995928	6
Rindt	Jochen	0.995971	4
Andretti	Mario	0.996677	18
Hill	Graham	0.997399	20
Senna	Ayrton	0.99779	40
Clark	Jim	0.998215	8
Rosberg	Nico	0.998362	197
Verstappen	Max	0.998456	168
Lauda	Niki	0.998517	37
Mansell	Nigel	0.998529	42
Schumacher	Michael	0.998615	237
Hill	Phil	0.99887	14
Alonso	Fernando	0.999616	350
Jones	Alan	0.999743	18
Scheckter	Jody	1.000694	18
Piquet	Nelson	1.000697	29
Rosberg	Keke	1.001174	11
Vettel	Sebastian	1.001338	286
Fittipaldi	Emerson	1.001902	14
Stewart	Jackie	1.002202	22
Farina	Nino	1.002902	16
Räikkönen	Kimi	1.003241	330
Hawthorn	Mike	1.003668	11
Hulme	Denny	1.003742	17
Häkkinen	Mika	1.005212	95
Brabham	Jack	1.005552	26
