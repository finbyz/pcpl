// Copyright (c) 2022, STPL and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Zone Wise Sales"] = {
	"filters": [
		{
			"fieldname":"invoice_no",
			"label": __("Invoice No"),
			"fieldtype": "Link",
			"options": "Sales Invoice",
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default":frappe.defaults.get_user_default("year_start_date"),
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default":frappe.defaults.get_user_default("year_end_date"),
		},
		{
			"fieldname":"customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
		},
		{
			"fieldname":"item_code",
			"label": __("Item"),
			"fieldtype": "Link",
			"options": "Item",
		},
		{
			"fieldname":"status",
			"label": __("Status"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				var options = []
				var status=["Draft", "Return", "Credit Note Issued", "Submitted", "Paid", "Partly Paid", "Unpaid", "Unpaid and Discounted", "Partly Paid and Discounted", "Overdue and Discounted", "Overdue", "Internal Transfer"]				
				for (let option of status){
					options.push({
						"value": option,
						"description": ""
					})
				}
				return options
			}
		},
		{
			"fieldname":"zone",
			"label": __("Zone"),
			"fieldtype": "Link",
			"options": "Customer Group",
			"get_query": function(){
				return {
					filters:{
						"is_group": 1
					}
				}
			}
		},
		{
			"fieldname":"devision",
			"label": __("Devision"),
			"fieldtype": "Link",
			"options": "Customer Group",
			"get_query": function(){
				return {
					filters:{
						"is_group": 0
					}
				}
			}
		},
	]
};


