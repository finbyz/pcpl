# Copyright (c) 2022, STPL and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	columns, data = [], []
	data = get_data(filters)
	columns = get_column(filters)
	return columns, data

def get_data(filters):
	condition = ""

	if filters.get('price_list_type') == 'Buying':
		condition += f" buying = 1"
	if filters.get('price_list_type') == 'Selling':
		condition += f" selling = 1"
	if filters.get('valid_from'):
		condition += f" and valid_from > '{filters.get('valid_from')}' " 
	if filters.get('valid_upto'):
		condition += f" and valid_upto < '{filters.get('valid_upto')}' " 
	if filters.get('price_list'):
		condition += f" and price_list = '{filters.get('price_list')}'"
	data =  frappe.db.sql(f''' SELECT brand , item_code , item_name , uom , price_list_rate 
								From `tabItem Price` 
								Where {condition} ''',as_dict=1)

	return data

def get_column(filters):
	columns = [
		{
			"label": _("Brand"),
			"fieldname": "brand",
			"fieldtype": "Data",
			"width": 200
		},
		{
			"label": _("Item Code"),
			"fieldname": "item_code",
			"fieldtype": "Link",
			"options": "Item",
			"width": 200
		},
		{
			"label": _("Item Name"),
			"fieldname": "item_name",
			"fieldtype": "Data",
			"width": 200
		},
		{
			"label": _("UOM"),
			"fieldname": "uom",
			"fieldtype": "Link",
			"options": "UOM",
			"width": 100
		},
		{
			"label": _("Rate"),
			"fieldname": "price_list_rate",
			"fieldtype": "Float",
			"width": 100
		},
	]
	return columns