# Copyright (c) 2022, STPL and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns, data = [], []
	data = get_data(filters)
	columns = get_columns()
	return columns, data

def get_data(filters):
	conditions = ''
	if filters.get("purchase_receipt"):
		conditions = f" and pr.name = '{filters.get('purchase_receipt')}'"
	
	if filters.get("purchase_order"):
		conditions = f" and po.name = '{filters.get('purchase_order')}'"

	data = frappe.db.sql(f"""
		select 
			po.name as purchase_order, po.transaction_date, po.supplier, s.supplier_group,
			pr.name as purchase_receipt, pr.posting_date,
			DATEDIFF(pr.posting_date, po.transaction_date) AS day_diff
		from
			`tabPurchase Order` as po
			left join `tabPurchase Receipt Item` as pri on pri.purchase_order = po.name
			join `tabPurchase Receipt` as pr on pr.name = pri.parent
			join `tabSupplier` as s on s.name = po.supplier
		where
			po.docstatus = 1 and pr.docstatus = 1 and s.disabled = 0 {conditions}
	""", as_dict = 1)

	return data

def get_columns():
	columns = [
		{
			"label": _("Purchase Order"),
			"fieldname": "purchase_order",
			"fieldtype": "Link",
			"options": "Purchase Order",
			"width": 170
		},
		{
			"label": _("Purchase Date"),
			"fieldname": "transaction_date",
			"fieldtype": "Date",
			"width": 150
		},
		{
			"label": _("Supplier Name"),
			"fieldname": "supplier",
			"fieldtype": "Data",
			"width": 200
		},
		{
			"label": _("Supplier Group"),
			"fieldname": "supplier_group",
			"fieldtype": "Link",
			"options": "Supplier",
			"width": 170
		},
		{
			"label": _("Purchase Receipt No"),
			"fieldname": "purchase_receipt",
			"fieldtype": "Link",
			"options": "Purchase Receipt",
			"width": 170
		},
		{
			"label": _("Purchase Receipt Date"),
			"fieldname": "posting_date",
			"fieldtype": "Date",
			"width": 150
		},
		{
			"label": _("Material Recived in Days"),
			"fieldname": "day_diff",
			"fieldtype": "Data",
			"width": 150
		}

	]
	return columns