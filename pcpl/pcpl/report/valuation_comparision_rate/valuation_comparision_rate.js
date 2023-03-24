// Copyright (c) 2023, STPL and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Valuation Comparision Rate"] = {
	"filters": [
		{
			"fieldname": "item_code",
			"label": __("Item List"),
			"fieldtype": "Link",
			"options" : "Item",	
			
		},
		{
			"fieldname": "item_group",
			"label": __("Item Group"),
			"fieldtype": "Link",
			"options" : "Item Group",	
			
		},


		
	

	]
};
