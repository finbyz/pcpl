// Copyright (c) 2022, STPL and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Monthly Free Aritcle Scheme"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd": 1,
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd": 1,
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname": "sales_scheme",
			"label": __("Sales Scheme"),
			"fieldtype": "Link",
			"options": "Sales Scheme",
			"width": "80"
		},
		{
			"fieldname": "customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
			"width": "80"
		},
		{
			"fieldname": "item_code",
			"label": __("Item Code"),
			"fieldtype": "Link",
			"options": "Item",
			"width": "80"
		},
	]
};
