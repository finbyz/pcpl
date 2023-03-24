// Copyright (c) 2023, STPL and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Secondary Monthly Sales Master"] = {
	"filters": [
		{
			"fieldname":"fiscal_year1",
			"label": __("Fiscal Year1"),
			"fieldtype": "Link",
			"options": "Fiscal Year",
			"reqd": 1
		}
	]
};
