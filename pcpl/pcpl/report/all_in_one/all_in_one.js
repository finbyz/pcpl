// Copyright (c) 2022, STPL and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["All In One"] = {
	"filters": [
		{
			"fieldname": "month",
			"label": __("Month"),
			"fieldtype": "Select",
			"options" : ["January","February","March","April","May","June","July","August","September","Octomber","November","December"],
			"depends_on":"eval:doc.base_on == 'Weekly'",
			"mandatory_depends_on":"eval:doc.base_on == 'Weekly'",
		},
		{
			"fieldname": "year",
			"label": __("Year"),
			"fieldtype": "Link",
			"options" : 'Fiscal Year',
			"reqd":1,
			"default":frappe.sys_defaults.fiscal_year
		},
		{
			"fieldname": "base_on",
			"label": __("Base On"),
			"fieldtype": "Select",
			"options" : ["Weekly","Monthly",'Quarterlly'],
			"reqd":1,	
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
			"options" : ['Division' ,'Sub Division', 'Zone'],
			"reqd":1
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "80",
			"depends_on":"eval:doc.base_on == 'Weekly'"
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "80",
			"depends_on":"eval:doc.base_on == 'Weekly'"
		},
		
		{
			"fieldname":"quarter",
			"label": __("Monthly Distribution"),
			"fieldtype": "Link",
			"options":"Monthly Distribution",
			"width": "80",
			"depends_on":"eval:doc.base_on == 'Quarterlly'",
			"mandatory_depends_on":"eval:doc.base_on == 'Quarterlly'"
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

