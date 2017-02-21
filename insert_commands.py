from faker import Faker
import random
fake = Faker()
from datetime import datetime
from datetime import timedelta
from time import strftime
#print fake.name()
#print fake.email()
#print fake.address().replace('\n', '')
#print fake.phone_number()
#print fake.domain_name() #mayer.com
#print fake.domain_word() #gusikowsk

# --------- CREATE TABLES ---------------

Suppliers = ('CREATE TABLE Suppliers('
	'supplier_id SERIAL PRIMARY KEY,'
	'name VARCHAR(100),'
	'address VARCHAR(255),'
	'phone_number VARCHAR(100),'
	'email VARCHAR(255));')


Products = ('CREATE TABLE Products('
   'barcode BIGINT PRIMARY KEY NOT NULL,'
   'supplier_id INTEGER,'
   'name VARCHAR(100),'
   'unit_weight INTEGER,'
   'units_per_case INTEGER,'
   'cost_per_case NUMERIC,'
   'case_weight NUMERIC,'
   'shelf_life INTEGER,'
   'FOREIGN KEY (supplier_id) REFERENCES Suppliers(supplier_id));')

Shipments = ('CREATE TABLE Shipments('
   'shipment_id SERIAL PRIMARY KEY,'
   'date_received DATE,'
   'supplier_id INTEGER,'
   'is_considered INTEGER NOT NULL DEFAULT(0),'# ***
   'FOREIGN KEY (supplier_id) REFERENCES Suppliers(supplier_id));')


Shipment_contains = ('CREATE TABLE Shipment_contains('
   'shipment_id INTEGER,'
   'barcode BIGINT,'
   'quantity INTEGER CHECK (quantity > 0),'
   'PRIMARY KEY (shipment_id, barcode),'
   'FOREIGN KEY (shipment_id) REFERENCES Shipments(shipment_id),'
   'FOREIGN KEY (barcode) REFERENCES Products(barcode));')


Inventory = ('CREATE TABLE Inventory('
   'shipment_id INTEGER,'
   'barcode BIGINT,'
   'expiry_date DATE,'
   'quantity INTEGER,'
   'PRIMARY KEY(shipment_id, barcode),'
   'FOREIGN KEY (barcode) REFERENCES Products(barcode),'
   'FOREIGN KEY (shipment_id) REFERENCES Shipments(shipment_id));')

Clients = ('CREATE TABLE Clients('
   'client_id SERIAL PRIMARY KEY,'
   'name VARCHAR(100),'
   'address VARCHAR(255),'
   'phone_number VARCHAR(100),'
   'email VARCHAR(255));')

Orders = ('CREATE TABLE Orders('
   'order_id SERIAL PRIMARY KEY,'
   'client_id INTEGER,'
   'delivery_date DATE,'
   'is_delivered INTEGER NOT NULL DEFAULT(0),'
   'is_considered INTEGER NOT NULL DEFAULT(0),' # *** Also deleted price per unit
   'FOREIGN KEY (client_id) REFERENCES Clients(client_id));')

Order_contains = ('CREATE TABLE Order_contains('
   'order_id INTEGER,'
   'barcode BIGINT,'
   'shipment_id INTEGER,'
   'quantity INTEGER CHECK (quantity > 0),'
   'PRIMARY KEY(order_id, barcode),'
   'FOREIGN KEY (order_id) REFERENCES Orders(order_id),'
   'FOREIGN KEY (barcode, shipment_id) REFERENCES Inventory(barcode, shipment_id));')



print Suppliers, '\n'
print Products, '\n'
print Shipments, '\n'
print Shipment_contains, '\n'
print Inventory, '\n'
print Clients, '\n'
print Orders, '\n'
print Order_contains, '\n'

# ---------- FILL SUPPLIERS TABLE ----------------

table = 'Suppliers'
columns = '(name,address,phone_number,email)'
n = 15
for i in range (1,n+1):
	values = "('Supplier%s', '%s', '%s', 'supplier%s@%s')"%(i,fake.address().replace('\n',''),fake.phone_number(),i,fake.domain_name())	
	print 'INSERT INTO %s %s VALUES %s;'%(table,columns,values)

print
# ------------- FILL PRODUCTS TABLE ---------------

f = open("../data/hummus_data.csv", "r").read().replace('$','').replace('\r','')
lines = f.split('\n')
barcodes = [w for w in lines[0].split(',')]
names = [w for w in lines[1].replace('\'', '').split(',')]
unit_weights = [w for w in lines[2].split(',')]
units_per_case = [w for w in lines[3].split(',')]
cost_per_case = [w for w in (lines[4].replace(' ', '')).split(',')]

# Duplicated barcodes --> fix below:
'''
188092200048
188092200123
'''

switch1 = 0
switch2 = 0
for i in range(len(barcodes)):
	if barcodes[i] == '188092200048' and switch1 == 0:
		#print "foundit1"
		barcodes[i] = '188092200047'
		switch1 = 1
	if barcodes[i] == '188092200123' and switch2 == 0:
		#print "foundit2"
		barcodes[i] = '188092200122'
		switch2 = 1
	
	if switch1 == 1 and switch2 == 1:
		break





#print barcodes
#print names
#print unit_weights
#print units_per_case
#print cost_per_case

'''
CREATE TABLE Products(
   barcode BIGINT PRIMARY KEY,		###
   supplier_id INTEGER,
   name VARCHAR(30),		 	###
   unit_weight INTEGER,		 	###
   units_per_case INTEGER,	 	###
   cost_per_case NUMERIC,	 	###
   case_weight NUMERIC,		 	###
   total_cases_per_pallete INTEGER,	###
   shelf_life INT
   FOREIGN KEY (supplier_id) REFERENCES Suppliers(supplier_id)
);

'''

number_suppliers = 1

supplier_ids = []
for i in range(1,number_suppliers+1):
	supplier_ids.append(i)

table = 'Products'
columns = '(barcode, supplier_id, name, unit_weight, units_per_case, cost_per_case, case_weight, shelf_life)'




#SET SHELF LIFE OF PRODUCTS ***
#       FOR NOW, ALL PRODUCTS HAVE SAME SHELF LIFE.
#       CAN CHANGE MANUALLY AFTER FOR LOOP IF U WANT
life = 14 # lasts 14 days after shipment is received
barcode_shelflife = {}
for barcode in barcodes:
        barcode_shelflife[barcode] = life


for i in range(len(barcodes)):
	r = random.randint(0,len(barcodes))
	#print r
	values = "(%s,%s,\'%s\',%s,%s,%s,%s,%s)"%(barcodes[i],
						random.choice(supplier_ids),
						names[i], 
						unit_weights[i], 
						units_per_case[i], 
						cost_per_case[i], 
						int(units_per_case[i]) * int(unit_weights[i]),
						barcode_shelflife[barcodes[i]])
	print 'INSERT INTO %s %s VALUES %s;'%(table,columns,values)


def shelf_life(barcode):
	return barcode_shelflife[barcode]

print

# ---------------- Shipments table ----------------------
def date_to_string(date):
	s = "%s"%date
	s = s.split(' ')
	return "\'%s\'"%s[0]

number_of_shipments = 20

table = 'Shipments'
columns = '(date_received, supplier_id)'
#	Supplier ID must reference the supplier table. Randomly sample from supplier_list

date_list = [] #will be used to construct dictionary shipmentID_date, so that we can use it in Inventory(expiry_date)

for i in range(number_of_shipments):
	date_list.append(datetime.now() - timedelta(days = 7*i))

for date in reversed(date_list):
	values = "(%s,%s)"%(date_to_string(date), random.choice(supplier_ids))
	print 'INSERT INTO %s %s VALUES %s;'%(table,columns,values)


# 	ShipmentID - Date dictionary, will be used in Inventory to generate exp.dates
shipmentID_date = {}
sid = 1
for date in reversed(date_list):
	shipmentID_date[sid] = date
	sid+=1

print
# ----------- Shipment_contains ---------------
'''
CREATE TABLE Shipment_contains(
   shipment_id INTEGER,
   barcode BIGINT,
   quantity INTEGER CHECK (quantity > 0),
   PRIMARY KEY (shipment_id, barcode),
   FOREIGN KEY (shipment_id) REFERENCES Shipments(shipment_id),
   FOREIGN KEY (barcode) REFERENCES Products(barcode)
);
'''

number_of_shipments = len(date_list)
shipment_ids = []

for i in range(1,number_of_shipments+1):
	shipment_ids.append(i)


table = 'Shipment_contains'
columns = '(shipment_id,barcode,quantity)'

# Assumption: In each shipment, we always order a certain amount of each item.

# This is the range of amounts we can order for each item. 
# Based on actual amounts, it seems like the range is [5,30] cases for each flavour/unit_weight combination.
r_min = 5
r_max = 30

shipmentID_barcode_quantity = {}

for shipment_id in shipment_ids:
	barcode_dict = {}
	for barcode in barcodes:
		r = random.randint(r_min,r_max)
		values = "(%s,%s,%s)"%(shipment_id, barcode, r)
		print 'INSERT INTO %s %s VALUES %s;'%(table,columns,values)
		barcode_dict[barcode] = r
	shipmentID_barcode_quantity[shipment_id] = barcode_dict.copy()

#print shipmentID_barcode_quantity[3]['188092000440'] # this outputs the quantity ordered in shipment X for barcode Y

print
# ---------------- INVENTORY ---------------------
def get_expiry_date(barcode, shipment_id):
	sdate = shipmentID_date[shipment_id]
	exp = sdate + timedelta(days = shelf_life(barcode))
	return date_to_string(exp)



'''
CREATE TABLE Inventory(
   shipment_id INTEGER,
   barcode BIGINT,
   expiry_date DATE,
   quantity INTEGER,
   PRIMARY KEY(shipment_id, barcode),
   FOREIGN KEY (barcode) REFERENCES Products(barcode),
   FOREIGN KEY (shipment_id) REFERENCES Shipments(shipment_id)
);
'''
table = 'Inventory'
columns = '(barcode,shipment_id, expiry_date, quantity)'

for shipment_id in shipment_ids: #sort table by shipment IDs 
	for barcode in barcodes:
		quantity = shipmentID_barcode_quantity[shipment_id][barcode]
		#NOTE: expiry_date can be automatically generated. Know by the nature of the product (store shelf_life). We can implement this after.
		values = '(%s,%s,%s,%s)'%(barcode, shipment_id, get_expiry_date(barcode, shipment_id), quantity)
		print 'INSERT INTO %s %s VALUES %s;'%(table,columns,values)

print
# --------------------- CLIENTS -----------------------
'''
CREATE TABLE Clients(
   client_id SERIAL PRIMARY KEY,
   name VARCHAR(30),
   address VARCHAR(255),
   phone_number VARCHAR(30),
   email VARCHAR(255)
);
'''

table = 'Clients'
columns = '(name, address, phone_number, email)'


# CUSTOMIZATION TO MAKE IT MORE REALISTIC, FK IT FOR NOW
names = ['INSERT CLIENT NAMES HERE']
addresses = ['INSERT CORRESPONDING ADDRESS HERE']
phone_numbers = ['INSERT CORRESPONDING PHONE NUMBERS HERE']
emails = ['INSERT CORRESPONDING EMAILS HERE']

n = 20	 #Number of clients
for i in range (1,n+1):
        values = "('Client%s', '%s', '%s', 'client%s@%s')"%(i,fake.address().replace('\n',''),fake.phone_number(),i,fake.domain_name())
        print 'INSERT INTO %s %s VALUES %s;'%(table,columns,values)

client_ids = [i for i in range(1,n+1)]


print
# -------------------- ORDERS -----------------------
'''
CREATE TABLE Orders(
   order_id SERIAL PRIMARY KEY,
   client_id INTEGER,
   delivery_date DATE,
   is_delivered INTEGER NOT NULL DEFAULT(0),
   FOREIGN KEY (client_id) REFERENCES Clients(client_id)
);
'''

table = 'Orders'
columns = '(client_id, delivery_date)'

#	Assume one delivery date for now
delivery_date = date_to_string(datetime.now() + timedelta(days = 2))

c_list = client_ids[:]
random.shuffle(c_list)


number_of_orders = 20
for i in range(number_of_orders):
	client_id = c_list.pop()
	values = "(%s,%s)"%(client_id, delivery_date)
	print 'INSERT INTO %s %s VALUES %s;'%(table,columns,values)


print
# --------------------- ORDER CONTAINS ------------------------
'''
CREATE TABLE Order_contains(
   order_id INTEGER,
   barcode BIGINT,
   shipment_id INTEGER,
   quantity INTEGER CHECK (quantity > 0),
   price_per_unit NUMERIC CHECK (price_per_unit > 0),
   PRIMARY KEY(order_id, barcode),
   FOREIGN KEY (order_id) REFERENCES Orders(order_id),
   FOREIGN KEY (barcode, shipment_id) REFERENCES Inventory(barcode, shipment_id)
);
'''


