// Copyright (c) 2023, STPL and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Secondary Monthly Sales Master"] = {
	"filters": [
		{
			"fieldname":"fiscal_year",
			"label": __("Fiscal Year"),
			"fieldtype": "Link",
			"options": "Fiscal Year",
			"reqd": 1
		},
		{
			"fieldname":"zone",
			"label": __("Zone"),
			"fieldtype": "Link",
			"options": "Territory",
			"get_query": () =>{
				return {
					filters: {"territory_type": 'Zone', 'is_secondary_': 1}
				}
			}
		}
	]
};
