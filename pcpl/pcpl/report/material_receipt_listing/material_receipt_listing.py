# Copyright (c) 2013, STPL and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe import _
import frappe

def execute(filters=None):
	columns, data = get_columns(), get_data(filters)
	return columns, data

def get_columns():
	columns = [
		{
			"label": _("Date"),
			"fieldname": "posting_date",
			"fieldtype": "Date",
			"width": 80
		},
		{
			"label": _("Voucher No"),
			"fieldname": "name",
			"fieldtype": "Link",
			"options": "Purchase Receipt",
			"width": 100
		},
		{
			"label": _("Supplier"),
			"fieldname": "supplier",
			"fieldtype": "Link",
			"options": "Supplier",
			"width": 100
		},
		{
			"label": _("Item Group"),
			"fieldname": "item_group",
			"fieldtype": "Link",
			"options": "Item Group",
			"width": 100
		},
		{
			"label": _("Item"),
			"fieldname": "item_code",
			"fieldtype": "Link",
			"options": "Item",
			"width": 150
		},
		{
			"label": _("UOM"),
			"fieldname": "uom",
			"fieldtype": "Link",
			"options": "UOM",
			"width": 50
		},
		{
			"label": _("Quantity"),
			"fieldname": "qty",
			"fieldtype": "Float",
			"width": 50
		},
		{
			"label": _("Free Item"),
			"fieldname": "free_item",
			"fieldtype": "Check",
			"width": 30
		},
		{
			"label": _("Rate"),
			"fieldname": "rate",
			"fieldtype": "Float",
			"width": 80
		},
		{
			"label": _("Amount"),
			"fieldname": "amount",
			"fieldtype": "Float",
			"width": 100
		}

	]
	return columns

def get_data(filters):
        datasales =  frappe.db.sql("""
                SELECT
                	`tabPurchase Receipt`.posting_date,
                        `tabPurchase Receipt`.name,
                       	`tabPurchase Receipt`.supplier,
                       	`tabPurchase Receipt Item`.item_group,
                        `tabPurchase Receipt Item`.item_code,
                        `tabPurchase Receipt Item`.uom,
                        `tabPurchase Receipt Item`.qty,
                        `tabPurchase Receipt Item`.free_item,
                        `tabPurchase Receipt Item`.rate,
                        `tabPurchase Receipt Item`.amount
                FROM
                        `tabPurchase Receipt Item`,`tabPurchase Receipt`
                WHERE
                        `tabPurchase Receipt Item`.`parent`=`tabPurchase Receipt`.`name`
                        AND `tabPurchase Receipt`.docstatus = 1
                        AND `tabPurchase Receipt`.posting_date BETWEEN %(from_date)s AND %(to_date)s
                        {conditions}""".format(conditions=get_conditions(filters)), filters,as_list=1)

        return datasales

def get_conditions(filters) :
	conditions = []

	if filters.get("item_code"):
		conditions.append(" and `tabPurchase Receipt Item`.item_code=%(item_code)s")
	if filters.get("item_group"):
		conditions.append(" and `tabPurchase Receipt Item`.item_group=%(item_group)s")
	if filters.get("supplier"):
		conditions.append(" and `tabPurchase Receipt`.supplier=%(supplier)s")

	return " ".join(conditions) if conditions else ""
