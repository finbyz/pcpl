// Copyright (c) 2023, STPL and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Secondary Sale Quarter Planning"] = {
	"filters": [
		{
			"fieldname": "year",
			"label": __("Year"),
			"fieldtype": "Select",
			"options" : ['2022-2023','2023-2024','2024-2025','2025-2026','2026-2027','2027-2028','2028-2029','2029-2030','2030-2031'],
			"reqd":1
		}
	]
};
