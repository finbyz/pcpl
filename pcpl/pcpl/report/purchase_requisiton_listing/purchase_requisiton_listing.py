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
			"label": _("ID"),
			"fieldname": "name",
			"fieldtype": "Link",
			"options": "Material Request",
			"width": 150
		},
		{
			"label": _("Transaction Date"),
			"fieldname": "transaction_date",
			"fieldtype": "Date",
			"width": 120
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
			"width": 150
		},
		{
			"label": _("Quantity"),
			"fieldname": "qty",
			"fieldtype": "Float",
			"width": 120
		},
		{
			"label": _("Created By"),
			"fieldname": "owner",
			"fieldtype": "Link",
			"options": "User",
			"width": 150
		}

	]
	return columns

def get_data(filters):
        datasales =  frappe.db.sql("""
                SELECT
                        `tabMaterial Request`.name,
                        `tabMaterial Request`.transaction_date,
                        `tabMaterial Request Item`.item_code,
                        `tabMaterial Request Item`.uom,
                        `tabMaterial Request Item`.qty,
                        `tabMaterial Request`.owner
                FROM
                        `tabMaterial Request Item`,`tabMaterial Request`
                WHERE
                        `tabMaterial Request Item`.`parent`=`tabMaterial Request`.`name`
                        AND `tabMaterial Request`.docstatus = 1
                        AND `tabMaterial Request`.transaction_date BETWEEN %(from_date)s AND %(to_date)s
                        {conditions}""".format(conditions=get_conditions(filters)), filters,as_list=1)

        return datasales

def get_conditions(filters) :
	conditions = []

	if filters.get("item_code"):
		conditions.append(" and `tabMaterial Request Item`.item_code=%(item_code)s")

	return " ".join(conditions) if conditions else ""
