// Copyright (c) 2016, STPL and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Price List Prince"] = {
	"filters": [
		{
			"fieldname":"item_code",
			"label": __("Item"),
			"fieldtype": "Link",
			"options": "Item"
		},
		{
			"fieldname":"price_list",
			"label": __("Price List"),
			"fieldtype": "Link",
			"options": "Price List",
			"default": "Gujarat Stockist",
		}

	]
};
