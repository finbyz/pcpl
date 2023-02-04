# Copyright (c) 2022, STPL and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns, data = [], []
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_columns(filters):
	columns = [
		{
			"label": _("Sales Invoice No"),
			"fieldname": "sales_invoice_no",
			"fieldtype": "Data", 
			"width": 200
		},
		{
			"label": _("Sales Scheme"),
			"fieldname": "sales_scheme",
			"fieldtype": "Data", 
			"width": 250
		},
		{
			"label": _("Customer"),
			"fieldname": "customer",
			"fieldtype": "Link", 
			"options":"Customer",
			"width": 250
		},
		{
			"label": _("Product"),
			"fieldname": "product",
			"fieldtype": "Data",
			"width": 200
		},
		{
			"label": _("Item Group"),
			"fieldname": "item_group",
			"fieldtype": "Data",
			"width": 200
		},
		{
			"label": _("Rate"),
			"fieldname":"rate",
			"fieldtype": "Currency", 
			"width": 200
		},
		{
			"label": _("QTY"),
			"fieldname": "qty",
			"fieldtype": "Float", 
			"width": 150
		},
		{
			"label": _("Amount"),
			"fieldname": "amount",
			"fieldtype": "Currency", 
			"width": 150
		},]

	return columns
def get_data(filters):

	condition = ''
	if filters.get("item_code"):
		condition += f" and sii.item_code = '{filters.get('item_code')}'"

	if filters.get("item_group"):
		condition += f" and sii.item_group = '{filters.get('item_group')}'"

	if filters.get("sales_scheme"):
		condition += f" and sii.sales_scheme = '{filters.get('sales_scheme')}'"
	if filters.get("customer"):
		condition+= f"and si.customer = '{filters.get('customer')}'"

	data = frappe.db.sql("""
	SELECT 
			si.invoice_no as sales_invoice_no,sii.sales_scheme as sales_scheme,si.customer,sii.item_name as product,sii.item_group,sii.free_item_pricelist_rate as rate,sii.qty as qty,(sii.free_item_pricelist_rate*sii.qty) as amount

	FROM
			`tabSales Invoice` si
	JOIN
			`tabSales Invoice Item` as sii on sii.parent = si.name

	where 
	     si.invoice_for_free_item =1 and si.docstatus=1 and si.posting_date between '{}' and '{}' {}
	
	 """ .format(filters.from_date,filters.to_date, condition), as_dict = 1
	 )
	return data