// Copyright (c) 2023, STPL and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Monthly-Cumulative Achivement"] = {
	"filters": [
	
		{
			"fieldname": "year",
			"label": __("Year"),
			"fieldtype": "Select",
			"options" : ['2022-2023','2023-2024','2024-2025','2025-2026','2026-2027','2027-2028','2028-2029','2029-2030','2030-2031'],
			"reqd":1
		},
		{
			"fieldname": "base_on",
			"label": __("Base On"),
			"fieldtype": "Select",
			"options" : ["Monthly"],	
			
		},
		{
			"fieldname": "group_by",
			"label": __("Group by"),
			"fieldtype": "Select",
			"options" : ['Division' ,'Sub Division', 'Zone'],
			"reqd":1
		},
		{
			"fieldname":"select_month",
			"label": __("Select Month"),
			"fieldtype": "MultiSelectList",
			"options": ['January','February','March','April','May','June','July','August','September','October','November','December'],
			"width": "80",
			"depends_on":"eval:doc.base_on == 'Monthly'",
			"mandatory_depends_on":"eval:doc.base_on == 'Monthly'"
			
		},
	]
};
