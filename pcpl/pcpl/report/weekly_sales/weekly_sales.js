// Copyright (c) 2022, STPL and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Weekly Sales"] = {
	"filters": [
		{
			"fieldname": "month",
			"label": __("Month"),
			"fieldtype": "Select",
			"options" : ["January","February","March","April","May","June","July","August","September","Octomber","November","December"],
			"reqd":1
		}
	]
};
