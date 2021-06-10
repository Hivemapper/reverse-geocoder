# Reverse Geocoder

Python script for using the Google Maps API Reverse Geocoder

##### Input: 
* lat
* lon

##### Output: 
* City
* County (aka administrative_area_level_2)
* State (administrative_area_level_1)
* Country

##### Usage
```
pip3 install pandas
```
pip3 install googlemaps==4.3.1
```
From the directory where the simplegecoder.py is saved run the command
```
python3 simplegeocoder.py --input_file=filename.csv --output_file=output.csv --api_key=YourAPIKey
```

(make sure the the filenames you choose in the Python script match accordingly
