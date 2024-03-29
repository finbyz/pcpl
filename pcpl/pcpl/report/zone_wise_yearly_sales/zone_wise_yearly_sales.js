// Copyright (c) 2023, STPL and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Zone Wise Yearly Sales"] = {
	"filters": [
		
		{
			"fieldname": "year",
			"label": __("year"),
			"fieldtype": "Link",
			"options" : 'Fiscal Year',
			"default":frappe.sys_defaults.fiscal_year
		},
		{
			"fieldname":"is_secondary_",
			"label": __("Is Secondary"),
			"fieldtype": "Check",
			"width": "80",
		}
	]
};
