// Copyright (c) 2023, STPL and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Item Group and Territory wise Net Sales"] = {
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
			"fieldname":"parent_devision",
			"label": __("Parent Devision"),
			"fieldtype": "Link",
			"options": "Territory",
			"depends_on": "eval:doc.territory_type == 'sub division'",
			"get_query": () =>{
				return {
					filters: {"territory_type": 'Division'}
				}
			},
			"hidden" : 1
		}
	]
};
