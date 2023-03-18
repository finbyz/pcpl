// Copyright (c) 2022, STPL and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales Invoice Trends Princecare"] = {
	"filters": [
		{
			"fieldname":"period",
			"label": __("Period"),
			"fieldtype": "Select",
			"options": [
				{ "value": "Weekly", "label": __("Weekly") },
				{ "value": "Monthly", "label": __("Monthly") },
				{ "value": "Quarterly", "label": __("Quarterly") },
				{ "value": "Half-Yearly", "label": __("Half-Yearly") },
				{ "value": "Yearly", "label": __("Yearly") }
			],
			"default": "Monthly",
			on_change : () => {
				let filter_based_on = frappe.query_report.get_filter_value('period');
				frappe.query_report.toggle_filter_display('from_date', filter_based_on !== 'Weekly');
				frappe.query_report.toggle_filter_display('to_date', filter_based_on !== 'Weekly');
				frappe.query_report.toggle_filter_display('fiscal_year', filter_based_on == 'Weekly');
				frappe.query_report.refresh();
			}
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default" : frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"hidden" : 1
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default" : frappe.datetime.add_days(frappe.datetime.get_today(), -1),
			"hidden" : 1
		},
		{
			"fieldname":"based_on",
			"label": __("Based On"),
			"fieldtype": "Select",
			"options": [
				{ "value": "Item", "label": __("Item") },
				{ "value": "Item Group", "label": __("Item Group") },
				{ "value": "Customer", "label": __("Customer") },
				{ "value": "Customer Group", "label": __("Customer Group") },
				{ "value": "Territory", "label": __("Territory") },
				{ "value": "Project", "label": __("Project") }
			],
			"default": "Item",
			"dashboard_config": {
				"read_only": 1,
			}
		},
		{
			"fieldname":"group_by",
			"label": __("Group By"),
			"fieldtype": "Select",
			"options": [
				"",
				{ "value": "Item", "label": __("Item") },
				{ "value": "Item Group", "label": __("Item Group") },
				{ "value": "Customer", "label": __("Customer") }
			],
			"default": ""
		},
		{
			"fieldname":"fiscal_year",
			"label": __("Fiscal Year"),
			"fieldtype": "Link",
			"options":'Fiscal Year',
			"default": frappe.sys_defaults.fiscal_year
		},
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company")
		},
		{
			"fieldname":"parent_customer_group",
			"label": __("Parent Customer Group"),
			"fieldtype": "Link",
			"options": "Customer Group",
			"depends_on": "eval:(doc.group_by == 'Customer' || doc.group_by == 'Item Group') && doc.based_on == 'Customer Group'",
			get_query: () => {
				return {
					filters: {
						'is_group': 1
					}
				}
			}
		},
		{
			"fieldname":"parent_devision",
			"label": __("Parent Devision"),
			"fieldtype": "Link",
			"options": "Territory",
			"get_query": () =>{
				return {
					filters: {"territory_type": 'Zone'}
				}
			},
		}
	]
};

