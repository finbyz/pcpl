// Copyright (c) 2022, STPL and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Price List Details"] = {
	"filters": [
		{
			"fieldname":"price_list",
			"label": __("Price List"),
			"fieldtype": "Link",
			"options": "Price List"
		},
		{
			"fieldname":"valid_from",
			"label": __("Valid From"),
			"fieldtype": "Date",
		},
		{
			"fieldname":"valid_Upto",
			"label": __("Valid Upto"),
			"fieldtype": "Date",
		},
		{
			"fieldname":"price_list_type",
			"label": __("Price list Type"),
			"fieldtype": "Select",
			"options":'Selling\nBuying',
			"reqd":1
		},
	]
};
