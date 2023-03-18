// Copyright (c) 2023, STPL and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Front 15"] = {
	"filters": [
		{
			"fieldname":"fiscal_year",
			"label": __("Fiscal Year"),
			"fieldtype": "Link",
			"options": "Fiscal Year",
			"reqd": 1
		},
		{
			"fieldname":"period",
			"label": __("Period"),
			"fieldtype": "Select",
			"options": [
				{ "value": "Yearly", "label": __("Yearly") },
				{ "value": "Quarterly", "label": __("Quarterly") },
			],
			"reqd": 1
		},
		{
			"fieldname":"quarter",
			"label": __("Quarter"),
			"fieldtype": "Select",
			"depends_on": "eval:doc.period == 'Quarterly'",
			"options": [
				{ "value": "Quarter1", "label": __("Quarter1") },
				{ "value": "Quarter2", "label": __("Quarter2") },
				{ "value": "Quarter3", "label": __("Quarter3") },
				{ "value": "Quarter4", "label": __("Quarter4") }
			],
			"default": "Quarter1"
		},
		{
			"fieldname":"ethical",
			"label": __("Ethical"),
			"fieldtype": "Link",
			"options": "Territory",
			"get_query": () =>{
				return {
					filters: {"parent_territory": 'Ethical'}
				}
			},
		},
		{
			"fieldname":"list_limit",
			"label": __("Total Customer Count"),
			"fieldtype": "Int",
			"default": 15,
			'reqd' : 1
		}
	]
};
