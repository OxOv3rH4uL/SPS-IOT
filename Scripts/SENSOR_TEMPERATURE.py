from pymongo import MongoClient
import datetime
import time
import adafruit_dht
from board import D22
from dotenv import load_dotenv
import os
load_dotenv()


##INITIAL VECHILE AND IOT DATABASE SETUP
connection_uri = os.getenv("connection_url")
client = MongoClient(connection_uri)
db = os.getenv("db")

##GLOBAL KINDA VARIABLES
VEHICLE="#####"
TYPE="#######"
SENSOR_NAME="#####"
SENSOR_TYPE="######"


##GETTING DATAS FROM SENSORS
# def get_sensor_data(SENSOR_TYPE):
# 	if SENSOR_TYPE == "DHT11":
		

# 		return temp,humid
# 	elif SENSOR_TYPE == "DHT22":
# 		dht_device = adafruit_dht.DHT22(D22)
# 		temp = dht_device.temperature
# 		humid = dht_device.humidity
# 		if temp is None and humid is None:
# 			print("MAKE SURE TO CONNECT THE PIN AT D22")
# 		return temp,humid



#SENSORS SETUP
sensors_coll = db.sensors

# Check if the sensor already exists
existing_sensor = sensors_coll.find_one({"name": SENSOR_NAME})

if not existing_sensor:
    datas = {
        "name": SENSOR_NAME,
        "type": SENSOR_TYPE,
        "created_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    }

    res = sensors_coll.insert_one(datas)
    time.sleep(2)
    app_sens = sensors_coll.find_one(sort=[('created_at', -1)])
else:
    app_sens = existing_sensor

# EQUIPMENT SETUP
equipment_coll = db.equipment

# Check if the equipment already exists
existing_equipment = equipment_coll.find_one({"name": VEHICLE})

if not existing_equipment:
    datas = {
        "name": VEHICLE,
        "type": TYPE,
        "sensors": app_sens,
        "created_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    }

    res = equipment_coll.insert_one(datas)
else:
    # If the equipment exists, use the existing document
    app_equipment = existing_equipment


while True:
	if SENSOR_TYPE == "DHT11":
		dht_device = adafruit_dht.DHT11(D22)
	elif SENSOR_TYPE == "DHT22":
		dht_device = adafruit_dht.DH22(D22)
	temp = dht_device.temperature
	humid = dht_device.humidity
	if temp is None and humid is None:
		print("MAKE SURE TO CONNECT THE PIN AT D22")
	vals = {
		"$set":{
			"data":[{
				"name":"Temperature",
				"value":str(temp)
				},
				{
				"name":"Humidity",
				"value":str(humid)
				}
			],
			"updated_at":datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

		}
	}

	app_sens = sensors_coll.find({"name":SENSOR_NAME})
	up_id = app_sens[0]['_id']

	if "data" not in app_sens[0]:
		sensors_coll.update_one({"_id":up_id},vals)
	else:
		update_query = {"$unset": {"data": []}}
		result = sensors_coll.update_one({"_id":up_id},update_query)
		result = sensors_coll.update_one({"_id":up_id},vals)
	time.sleep(3)

	app_sens = sensors_coll.find({"name":SENSOR_NAME})
	up_id = app_sens[0]['_id']
	updated = {
		"$set":{
			"sensors":app_sens[0],
			"updated_at":datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
		}
	}

	del_first = {
		"$unset":{
			"sensors":""
		}
	}
	equip = equipment_coll.find({"name":VEHICLE})
	up_id = equip[0]['_id']
	result = equipment_coll.update_one({"_id":up_id},del_first)
	result = equipment_coll.update_one({"_id":up_id},updated)
	dht_device.exit()
	# print("Updated")
	time.sleep(10)




	



