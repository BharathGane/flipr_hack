from math import sin, cos, sqrt, atan2, radians
import sqlite3 as sql
from api import app
import pymongo
from pymongo import MongoClient
class Users:
	def create_db(self):
		conn = sql.connect('users.db')
		c = conn.cursor()
		c.execute("create table users (id integer primary key autoincrement,username text not null,password text not null);")
		conn.commit()
		conn.close()

	def insert_user(self,username,password):
		con = sql.connect("users.db")
		cur = con.cursor()
		cur.execute("INSERT INTO users (username,password) VALUES (?,?)", (username,password))
		con.commit()
		con.close()

	def retrieve_users(self):
		con = sql.connect("users.db")
		cur = con.cursor()
		cur.execute("SELECT username, password FROM users")
		users = cur.fetchall()
		con.close()
		return users

	def check_user(self,username,password):
		con = sql.connect("users.db")
		cur = con.cursor()
		cur.execute("SELECT username, password FROM users")
		users = cur.fetchall()
		con.close()
		if (username,password) in users:
			return True
		else:
			return False
class Util:
	def lat_long_distace(self,lat1,lon1,lat2,lon2):
		if lat1 and lat2 and lon1 and lon2:
			R = 6373.1
			dlon = lon2 - lon1
			dlat = lat2 - lat1
			a = sin(dlat / 2)*2 + cos(lat1) * cos(lat2) * sin(dlon / 2)*2
			c = 2 * atan2(sqrt(abs(a)), sqrt(abs(1 - a)))
			distance = R * c *1000
			return distance
		else:
			return 100000

class mongodata:
	def __init__(self):
		self.client = MongoClient('mongodb+srv://backendconcoxdeveloper:V3jUV7QXqEoAtnhy@cluster0-zhjde.mongodb.net')
		self.db = self.client['__CONCOX__']
		self.status = self.db['status']
		self.devices = self.db['devices']
	
	def get_devices(self):
		devices_data = self.devices.find()
		a = []
		list_devices = []
		for i in devices_data:
			if i["id"] not in a:
				a.append(i['id'])
				del i['_id']
				list_devices.append(i)
		return list_devices

	def get_status_for_device(self,id_):
		devices_data = self.devices.find({'id':id_})
		imei = devices_data.next()['imei']	
		list_status = self.status.find({'imei':imei})
		count = 0
		result = []
		for i in list_status:
			del i['_id']
			count+=1
			if count > 10:
				break
			else:
				result.append(i)
		return result

	def get_status_for_device_page(self,id_,page):
		devices_data = self.devices.find({'id':id_})
		imei = devices_data.next()['imei']	
		list_status = self.status.find({'imei':imei})
		count = int(page)*10
		temp = 0
		result = []
		flag = 0
		for i in list_status:
			if temp == count-10:
				flag = 1
			elif temp > count:
				flag = 0
				break
			if flag == 1:
				del i['_id']
				result.append(i)
			temp +=1
		return result

	def find_halts(self):
		devices_data = self.devices.find()
		device_ids = []
		device_imei = []
		halts_all_ids = {}
		for i in devices_data:
			if i["id"] not in device_ids:
				device_ids.append(i['id'])
				device_imei.append(i['imei'])
				del i['_id']
		count = 2
		for i in device_imei:
			if count == 0:
				break;
			count -=1
			halts = []
			status_data = self.status.find({'imei':i})
			gps_data = {}
			for j in status_data:
				if j.get('gps'):
					gps_data[j['createdAt']] = j['gps']
			sorted_gps = sorted(gps_data)
			util = Util()
			max_ = 0
			latitude,longitude = sorted_gps[0],sorted_gps[1]
			time_ = sorted_gps[0]
			if len(sorted_gps) >= 2:
				for j in range(len(sorted_gps)-1):
					time_diff = sorted_gps[j+1] - time_
					min_diff = divmod(time_diff.total_seconds(),60)[0]
					if  min_diff >= 15: 
						lat1,long1 = gps_data[sorted_gps[j]][0],gps_data[sorted_gps[j]][1]
						lat2,long2 = gps_data[sorted_gps[j+1]][0],gps_data[sorted_gps[j+1]][1]
						if util.lat_long_distace(lat1,long1,lat2,long2) < 100:
							if min_diff >  max_:
								max_ = min_diff
						else:
							if max_ !=0:
								halts.append({'gps':[lat1,long2],'time_in_min':max_,'date1':time_,'date2':sorted_gps[j+1]})
							latitude,longitude = gps_data[sorted_gps[j+1]][0],gps_data[sorted_gps[j+1]][1]		
							time_ = sorted_gps[j+1]
				halts_all_ids[i] = halts
		return halts_all_ids