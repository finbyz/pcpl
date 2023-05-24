// Copyright (c) 2023, STPL and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Secondary Zone Wise Yearly Sales"] = {
	"filters": [
		
		{
			"fieldname": "year",
			"label": __("year"),
			"fieldtype": "Link",
			"options" : 'Fiscal Year',
			"default":frappe.sys_defaults.fiscal_year
		}
	]
};

