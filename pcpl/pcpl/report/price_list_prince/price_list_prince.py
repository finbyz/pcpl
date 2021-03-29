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
			"label": _("Item"),
			"fieldname": "item_code",
			"fieldtype": "Link",
			"options": "Item",
			"width": 150
		},
		{
			"label": _("Item Name"),
			"fieldname": "item_name",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("MRP"),
			"fieldname": "price_list_rate1",
			"fieldtype": "Float",
			"width": 120
		},
		{
			"label": _("Price List Rate"),
			"fieldname": "price_list_rate",
			"fieldtype": "Float",
			"width": 120
		},
		{
			"label": _("Price List"),
			"fieldname": "price_list",
			"fieldtype": "Link",
			"options": "Price List",
			"width": 150
		},
		{
			"label": _("Valid From"),
			"fieldname": "valid_from",
			"fieldtype": "Date",
			"width": 100
		},
		{
			"label": _("Valid Upto"),
			"fieldname": "valid_upto",
			"fieldtype": "Date",
			"width": 100
		}
	]
	return columns

def get_data(filters):
        datasales =  frappe.db.sql("""
                SELECT
                        `ip`.item_code,
                        `ip`.item_name,
                        if(`ipp`.price_list = "MRP", `ipp`.price_list_rate, null),
                        `ip`.price_list_rate,
                        `ip`.price_list,
                        `ip`.valid_from,
                        `ip`.valid_upto
                FROM
                        `tabItem Price` ip, `tabItem Price` ipp
                WHERE
                        `ipp`.price_list = "MRP" <> `ip`.price_list
                        AND `ipp`.item_code = `ip`.item_code
                        AND `ip`.price_list = %(price_list)s
                        {conditions}""".format(conditions=get_conditions(filters)), filters,as_list=1)

        return datasales

def get_conditions(filters) :
	conditions = []

	if filters.get("item_code"):
		conditions.append(" and `ip`.item_code=%(item_code)s")
	if filters.get("price_list"):
		conditions.append(" and `ip`.price_list=%(price_list)s")	

	return " ".join(conditions) if conditions else ""
