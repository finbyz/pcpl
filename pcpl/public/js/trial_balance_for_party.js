// Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Trial Balance for Party"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1
		},
		{
			"fieldname": "fiscal_year",
			"label": __("Fiscal Year"),
			"fieldtype": "Link",
			"options": "Fiscal Year",
			"default": frappe.defaults.get_user_default("fiscal_year"),
			"reqd": 1,
			"on_change": function(query_report) {
				var fiscal_year = query_report.get_values().fiscal_year;
				if (!fiscal_year) {
					return;
				}
				frappe.model.with_doc("Fiscal Year", fiscal_year, function(r) {
					var fy = frappe.model.get_doc("Fiscal Year", fiscal_year);
					frappe.query_report.set_filter_value({
						from_date: fy.year_start_date,
						to_date: fy.year_end_date
					});
				});
			}
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.defaults.get_user_default("year_start_date"),
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.defaults.get_user_default("year_end_date"),
		},
		{
			"fieldname":"party_type",
			"label": __("Party Type"),
			"fieldtype": "Link",
			"options": "Party Type",
			"default": "Customer",
			"reqd": 1,
			on_change : () => {
				let filter_based_on = frappe.query_report.get_filter_value('party_type');
				frappe.query_report.toggle_filter_display('customer', filter_based_on === 'Supplier');
				frappe.query_report.toggle_filter_display('customer_group', filter_based_on === 'Supplier');
				frappe.query_report.toggle_filter_display('supplier', filter_based_on === 'Customer');
				frappe.query_report.toggle_filter_display('supplier_group', filter_based_on === 'Customer');
				frappe.query_report.set_filter_value('customer', null);
				frappe.query_report.set_filter_value('supplier', null);
				frappe.query_report.set_filter_value('customer_group', null);
				frappe.query_report.set_filter_value('supplier_group', null);
				frappe.query_report.refresh();
			}
		},
		{
			"fieldname":"customer_group",
			"label": __("Customer Group"),
			"fieldtype": "Link",
			"options": "Customer Group",
			on_change : () => {
				frappe.query_report.refresh();
			}
		},
		{
			"fieldname":"supplier_group",
			"label": __("Supplier Group"),
			"fieldtype": "Link",
			"options": "Supplier Group",
			"hidden": 1,
			on_change : () => {
				frappe.query_report.refresh();
			}
		},
		{
			"fieldname":"party",
			"label": __("Party"),
			"fieldtype": "Dynamic Link",
			"get_options": function() {
				var party_type = frappe.query_report.get_filter_value('party_type');
				var party = frappe.query_report.get_filter_value('party');
				if(party && !party_type) {
					frappe.throw(__("Please select Party Type first"));
				}
				return party_type;
			}
		},
		{
			"fieldname": "account",
			"label": __("Account"),
			"fieldtype": "Link",
			"options": "Account",
			"get_query": function() {
				var company = frappe.query_report.get_filter_value('company');
				return {
					"doctype": "Account",
					"filters": {
						"company": company,
					}
				}
			}
		},
		{
			"fieldname": "show_zero_values",
			"label": __("Show zero values"),
			"fieldtype": "Check"
		}
	]
}
frappe.provide("finbyzerp")
finbyzerp.view_party_ledger_report = {
    view_party_ledger_report: function(company, from_date, to_date, account, party_type, party){
		window.open(`/app/query-report/Party Ledger/%3Fcompany%3D${company}%26from_date%3D${from_date}%26to_date%3D${to_date}%26account%3D${account}%26party_type%3D${party_type}%26party%3D${party}`,"_blank")
    }
}