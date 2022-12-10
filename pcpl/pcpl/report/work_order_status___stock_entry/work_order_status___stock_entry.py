# Copyright (c) 2022, FinByz Tech Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns, data = [], []
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_data(filters):
	status =''
	if filters.get('status') == 'Submited':
		status += f" and se.docstatus = 1"
	if filters.get('status') == 'Draft':
		status += f" and se.docstatus = 0"
	date_fil = ''
	if filters.get('from_date') and filters.get('to_date'):
		date_fil += f" and se.posting_date BETWEEN '{filters.get('from_date')}' and '{filters.get('to_date')}'"

	data=frappe.db.sql(f"""Select
			se.`name`as stock_entry_no ,
			se.`posting_date` as date,
			sed.`item_name` as item_name,
			sed.`t_warehouse` as target_warhouse,
			sed.`s_warehouse` as source_warhouse,
			sed.`qty` as qty,
			se.docstatus as status,
			se.bom_no
			From 
				`tabStock Entry` as se
			left join 
				`tabStock Entry Detail` as sed ON sed.parent = se.name
			Where 
				(se.stock_entry_type = 'Manufacture' and sed.is_finished_item = 1 and se.docstatus < 2 {date_fil} {status}) or  (se.stock_entry_type = 'Manufacture'  and se.docstatus < 2 {date_fil} {status} and is_free = 1 )
		""",as_dict = True)
	for row in data:
		if row.status == 0:
			row.update({'status':'Draft'})
		if row.status == 1:
			row.update({'status':'Submitted'})
	return data


def get_columns(filters):
	columns = [
		{
			"label": _("Stock Entry No"),
			"fieldname": "stock_entry_no",
			"fieldtype": "Link",
			"options": "Stock Entry",
			"width": 140
		},
		{
			"label": _("Date"),
			"fieldname": "date",
			"fieldtype": "Date",
			"width": 140
		},
		{
			"label": _("Item Name"),
			"fieldname": "item_name",
			"fieldtype": "Data",
			"width": 140
		},
		{
			"label": _("Target Warhouse"),
			"fieldname": "target_warhouse",
			"fieldtype": "Link",
			"options": "Warehouse",
			"width": 160
		},
		{
			"label": _("Source Warhouse"),
			"fieldname": "source_warhouse",
			"fieldtype": "Link",
			"options": "Warehouse",
			"width": 140
		},
		{
			"label": _("Quantity"),
			"fieldname": "qty",
			"fieldtype": "Float",
			"width": 120
		},
		{
			"label": _("Status"),
			"fieldname": "status",
			"fieldtype": "data",
			"width": 120
		},
		{
			"label": _("Bom"),
			"fieldname": "bom_no",
			"fieldtype": "link",
			'options':'BOM',
			"width": 120
		},
	]
	return columns