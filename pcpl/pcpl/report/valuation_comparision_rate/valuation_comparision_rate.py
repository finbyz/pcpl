# Copyright (c) 2023, STPL and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns, data = [], []
	data  = get_data(filters)
	columns = get_cols(filters)
	return columns, data


def get_data(filters):
	conditions=""
	if filters.get('item_group'):
		conditions += "and ti.item_group = '{}'".format(filters.get("item_group"))
	if filters.get("item_code"):
		conditions += "and ti.item_code = '{}'".format(filters.get("item_code"))
	data = frappe.db.sql(f"""SELECT ti.name, ti.valuation_rate, ti.last_purchase_rate,pii.rate, pi.name as invoice,(ti.last_purchase_rate-pii.rate) as difference
	from `tabItem`as ti 
	 join `tabPurchase Invoice Item` as pii ON pii.item_code = ti.name
	join `tabPurchase Invoice` as pi on pi.name = pii.parent 
	where pii.docstatus=1 {conditions} order by 
	pi.posting_date desc 
	""",as_dict=1)
	duplicate_row=[]
	final_data=[]
	for i, row in enumerate(data,1):
		if row.name not in duplicate_row:
			duplicate_row.append(row.name)
			final_data.append(row)
	return final_data
def get_cols(filters):
	

	columns = [
		{
		"label": "Item List",
		"fieldname": "name",
		"fieldtype": "Link",
		'options': 'Item',
		"width": 200
		},
		{
		"label": "Valuation Rate",
		"fieldname": "valuation_rate",
		"fieldtype": "Currency",
		"width": 200
		},
		
		{
		"label": "Last Purchase Rate",
		"fieldname": "last_purchase_rate",
		"fieldtype": "Currency",
		"width": 200
		},
		{
		"label": "Latest Rate",
		"fieldname": "rate",
		"fieldtype": "Currency",
		"width": 200
		},
		{
		"label": "Invoice",
		"fieldname": "invoice",
		"fieldtype": "Link",
		'options': 'Purchase Invoice',
		"width": 200
		},
		{
		"label": "Difference",
		"fieldname": "difference",
		"fieldtype": "Currency",
		"width": 200
		},
		
		
	]
	return columns

