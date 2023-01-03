// Copyright (c) 2022, STPL and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Weekly Sales"] = {
	"filters": [
		{
			"fieldname": "month",
			"label": __("Month"),
			"fieldtype": "Select",
			"options" : ["","January","February","March","April","May","June","July","August","September","Octomber","November","December"],
			
			
		},
		{
			"fieldname": "year",
			"label": __("Year"),
			"fieldtype": "Select",
			"options" : [2022,2023,2024,2025,2026,2027,2028,2029,2030,2031,2032,2033],
			"reqd":1
		},
		{
			"fieldname": "base_on",
			"label": __("Base On"),
			"fieldtype": "Select",
			"options" : ["Weekly","Monthly"],	
			on_change: function() {
				let filter_based_on = frappe.query_report.get_filter_value('base_on');
				frappe.query_report.toggle_filter_display('month', filter_based_on == 'Monthly');
				frappe.query_report.refresh();
			}
			
		},
		{
			"fieldname": "group_by",
			"label": __("Group by"),
			"fieldtype": "Select",
			"options" : ['Division' , 'Zone'],
			
		},
	]
};
