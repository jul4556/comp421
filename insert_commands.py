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
print "-- Drop existing tables:"
print "DROP TABLE clients, inventory, order_contains, orders, products, shipment_contains, shipments, suppliers;\n"


print "-- Create tables:"
Suppliers = ('CREATE TABLE Suppliers('
	'\n\tsupplier_id SERIAL PRIMARY KEY,'
	'\n\tname VARCHAR(100),'
	'\n\taddress VARCHAR(255),'
	'\n\tphone_number VARCHAR(100),'
	'\n\temail VARCHAR(255));')

Products = ('CREATE TABLE Products('
   '\n\tbarcode BIGINT PRIMARY KEY NOT NULL,'
   '\n\tsupplier_id INTEGER,'
   '\n\tname VARCHAR(100),'
   '\n\tunit_weight INTEGER,'
   '\n\tunits_per_case INTEGER,'
   '\n\tcost_per_case NUMERIC,'
   '\n\tcase_weight NUMERIC,'
   '\n\tshelf_life INTEGER,'
   '\n\tFOREIGN KEY (supplier_id) REFERENCES Suppliers(supplier_id));')

Shipments = ('CREATE TABLE Shipments('
   '\n\tshipment_id SERIAL PRIMARY KEY,'
   '\n\tdate_received DATE,'
   '\n\tsupplier_id INTEGER,'
   '\n\tis_considered INTEGER NOT NULL DEFAULT(0),'# ***
   '\n\tFOREIGN KEY (supplier_id) REFERENCES Suppliers(supplier_id));')

Shipment_contains = ('CREATE TABLE Shipment_contains('
   '\n\tshipment_id INTEGER,'
   '\n\tbarcode BIGINT,'
   '\n\tquantity INTEGER CHECK (quantity > 0),'
   '\n\tPRIMARY KEY (shipment_id, barcode),'
   '\n\tFOREIGN KEY (shipment_id) REFERENCES Shipments(shipment_id),'
   '\n\tFOREIGN KEY (barcode) REFERENCES Products(barcode));')

Inventory = ('CREATE TABLE Inventory('
   '\n\tshipment_id INTEGER,'
   '\n\tbarcode BIGINT,'
   '\n\texpiry_date DATE,'
   '\n\tquantity INTEGER,'
   '\n\tPRIMARY KEY(shipment_id, barcode),'
   '\n\tFOREIGN KEY (barcode) REFERENCES Products(barcode),'
   '\n\tFOREIGN KEY (shipment_id) REFERENCES Shipments(shipment_id));')

Clients = ('CREATE TABLE Clients('
   '\n\tclient_id SERIAL PRIMARY KEY,'
   '\n\tname VARCHAR(100),'
   '\n\taddress VARCHAR(255),'
   '\n\tphone_number VARCHAR(100),'
   '\n\temail VARCHAR(255));')

Orders = ('CREATE TABLE Orders('
   '\n\torder_id SERIAL PRIMARY KEY,'
   '\n\tclient_id INTEGER,'
   '\n\tdelivery_date DATE,'
   '\n\tis_delivered INTEGER NOT NULL DEFAULT(0),'
   '\n\tis_considered INTEGER NOT NULL DEFAULT(0),' # *** Also deleted price per unit
   '\n\tFOREIGN KEY (client_id) REFERENCES Clients(client_id));')

Order_contains = ('CREATE TABLE Order_contains('
   '\n\torder_id INTEGER,'
   '\n\tbarcode BIGINT,'
   '\n\tquantity INTEGER CHECK (quantity > 0),'
   '\n\tPRIMARY KEY(order_id, barcode),'
   '\n\tFOREIGN KEY (order_id) REFERENCES Orders(order_id),'
   '\n\tFOREIGN KEY (barcode) REFERENCES Products(barcode));')

print Suppliers, '\n'
print Products, '\n'
print Shipments, '\n'
print Shipment_contains, '\n'
print Inventory, '\n'
print Clients, '\n'
print Orders, '\n'
print Order_contains, '\n'

# ---------- FILL SUPPLIERS TABLE ----------------

print "-- Insert records into Suppliers table:"

table = 'Suppliers'
columns = '(name,address,phone_number,email)'
n = 15
for i in range (1,n+1):
	values = "('Supplier%s', '%s', '%s', 'supplier%s@%s')"%(i,fake.address().replace('\n',''),fake.phone_number(),i,fake.domain_name())	
	print 'INSERT INTO %s %s VALUES %s;'%(table,columns,values)

print
# ------------- FILL PRODUCTS TABLE ---------------

print "-- Insert records in Products table:"

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

print "-- Insert records into Shipments table:"


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

print "-- Insert records in Shipment_contains table:"

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

print "-- Insert records into Inventory table:"

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
print "-- Insert records into Clients table:"

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

print "-- Insert records into Orders table:"

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

print "-- Insert records into Order_contains table:"

'''
CREATE TABLE Order_contains(
   order_id INTEGER,
   barcode BIGINT,
   shipment_id INTEGER,
   quantity INTEGER CHECK (quantity > 0),
   PRIMARY KEY(order_id, barcode),
   FOREIGN KEY (order_id) REFERENCES Orders(order_id),
   FOREIGN KEY (barcode) REFERENCES Products(barcode)
);
'''

#inventory = shipmentID_barcode_quantity.copy()

table = 'Order_contains'
columns = '(order_id, barcode, quantity)'

for oid in range(1,number_of_orders+1):
	b_arcodes = barcodes[:]
	random.shuffle(b_arcodes)
	for j in range(random.randint(1,5)):
		b = b_arcodes.pop()
		values = '(%s,%s,%s)'%(oid, b, random.randint(1,15))
		print 'INSERT INTO %s %s VALUES %s;'%(table,columns,values)

print 
# Once order_contains table is filled, 
# must set is_considered in orders to 1 for all oids entered to order_contains.
# Since all orders are expanded in order_contains, we will set all is_considered to 1.

print "-- Set all is_considered swtiches from '0' to '1' in Orders table:"

print "UPDATE orders SET is_considered = 1 WHERE is_considered = 0;"

print 
# Now we'll insert other orders to order contains, 
# but these orders will not be considered, ie. is_considered = 0. 

#for oid in range(number_of_orders+1, number_of_orders + 6):
#	print 


print "-- Add 5 more records to Orders table with default is_considered switch = '0'"

table = 'Orders'
columns = '(client_id, delivery_date)'

delivery_date = date_to_string(datetime.now() + timedelta(days = 5))

c_list = client_ids[:]
random.shuffle(c_list)

for i in range(number_of_orders):
	client_id = c_list.pop()
	values = "(%s,%s)"%(client_id, delivery_date)
	print 'INSERT INTO %s %s VALUES %s;'%(table,columns,values)


print 

print "-- Data modification commands:"

print "-- 1)"
print "/*\nDELETE FROM inventory WHERE expiry_date <= '2016-10-25';\n*/\n"

print "-- 2)"
print "/*\nUPDATE orders SET is_delivered = 1 WHERE date = '2017-02-25' AND is_delivered = 0;\n*/\n"

command_3 = ('/*'
'\nDO' 
'\n$$'
'\nDECLARE cid INTEGER := 14;'
"\nDECLARE ddate DATE := '2017-02-25';"
'\nDECLARE bcode BIGINT := 188092200086;'
'\nDECLARE amount_to_add INTEGER := 3;'
'\nBEGIN'
'\nIF EXISTS (SELECT barcode FROM order_contains WHERE barcode = bcode AND order_id IN' 
	'\n\t(SELECT order_id FROM orders WHERE client_id = cid AND delivery_date = ddate))' 
'\nTHEN'
	'\n\tUPDATE order_contains SET quantity = quantity+amount_to_add WHERE barcode = bcode AND order_id IN'
		'\n\t\t(SELECT order_id FROM orders WHERE client_id = cid AND delivery_date = ddate);'
'\nELSE'
	'\n\tINSERT INTO order_contains (barcode, quantity, order_id) VALUES'
		'\n\t\t(bcode, amount_to_add, (SELECT order_id FROM orders WHERE client_id = cid AND delivery_date = ddate));'
'\nEND IF;'
'\nEND'
'\n$$'
'\n*/')

print "-- 3)"
print command_3




'''
@ SAMSON
INSERT YOUR COMMAND HERE AND MAKE SURE IT RUNS 
BY UNCOMMENTING THE /* */
Make it in the same format as above (ie. the code prints it with tabs and newlines). 
Be sure to add a description of the data modification you made and screenshots for proof that it works, ie. before and after. 
'''

