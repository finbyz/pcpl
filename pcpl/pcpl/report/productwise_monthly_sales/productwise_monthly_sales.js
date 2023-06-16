// Copyright (c) 2023, STPL and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Productwise Monthly Sales"] = {
	"filters": [
		{
			"fieldname":"fiscal_year",
			"label": __("Fiscal Year"),
			"fieldtype": "Link",
			"options": "Fiscal Year",
			"reqd": 1
		},
		{
			"fieldname":"territory_type",
			"label": __("Territory Type"),
			"fieldtype": "Select",
			"options": [
				{ "value": "zone", "label": __("Zone") },
				{ "value": "division", "label": __("Division") },
				{ "value": "sub division", "label": __("Sub Devision") },
				
			],
			"reqd": 1
		},
		{	
			"fieldname":"territory",
			"label": __("Territory"),
			"fieldtype": "Link",
			"options": "Territory",
			"get_query": () =>{
				var territory_type = frappe.query_report.get_filter_value('territory_type');
				return {
					filters: {"territory_type": territory_type}
				}
			},
		},
	]
};
