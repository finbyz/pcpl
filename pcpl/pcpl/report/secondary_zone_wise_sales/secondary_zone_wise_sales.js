// Copyright (c) 2022, STPL and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Secondary Zone Wise Sales"] = {
	"filters": [
		
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
			"get_query": function(){
				return {
					filters:{
						"is_secondary_customer":1
					}
				}
			}
		},
		{
			"fieldname":"item_code",
			"label": __("Item"),
			"fieldtype": "Link",
			"options": "Item",
		},
		
		{
			"fieldname":"zone",
			"label": __("Zone"),
			"fieldtype": "Link",
			"options": "Customer Group",
			"get_query": function(){
				return {
					filters:{
						"is_group": 1,
						"is_secondary_group":1
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
						"is_group": 0,
						
						
					}
				}
			}
		},
		
		{
			"fieldname":"cn",
			"label":__("CN"),
			"fieldtype":"Check"
		},
		{
			"fieldname":"transfer_cn",
			"label":__("Transfer CN"),
			"fieldtype":"Check"
		}

		
	]
};


