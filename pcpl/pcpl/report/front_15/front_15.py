# Copyright (c) 2023, Finbyz Tech. Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, getdate

def execute(filters=None):

	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	columns = [
		{ "label": _("Zone"),"fieldname": "zone","fieldtype": "Link","options" : "Customer Group", "width": 100},
		{ "label": _("Division"),"fieldname": "customer_group","fieldtype": "Link","options" : "Customer Group", "width": 100},
		{ "label": _("Customer Name"),"fieldname": "customer","fieldtype": "Link","options" : "Customer", "width": 300},
		{ "label": _("City"),"fieldname": "city","fieldtype": "Data", "width": 300},
		{ "label": _("Sales Figure"),"fieldname": "sales_figure","fieldtype": "Currency", "width": 300},
		{ "label": _("Sales Executive"),"fieldname": "sales_person","fieldtype": "Link", "options" : "Sales Person","width": 300},
	]
	return columns

def get_data(filters):
	bet_dates = get_period_date_ranges(filters.get("period"), filters.get("fiscal_year"))

	qtr_dict = {
		"Quarter1" : 0,
		"Quarter2" : 1,
		"Quarter3" : 2,
		"Quarter4" : 3
	}
	if filters.get('period') and filters.get('quarter'):
		between_date = bet_dates[qtr_dict[filters.get('quarter')]]
	elif filters.get('period'):
		between_date = bet_dates[0]
	
	conditions = ""
	if filters.get('ethical'):
		conditions += f"and si.place_of_supply like '%%{filters.get('ethical')}%%'"

	data = frappe.db.sql(f"""
		SELECT 
			cg.parent_customer_group as zone, si.customer_group, si.customer, si.customer_city as city, GROUP_CONCAT(DISTINCT st.sales_person) as sales_person, si.place_of_supply, SUM(si.total) as sales_figure
		FROM
			`tabSales Invoice` as si
		JOIN
			`tabSales Team` as st on si.name = st.parent
		JOIN 
			`tabCustomer Group` as cg on si.customer_group = cg.name
		WHERE
			si.docstatus = 1
			and cg.parent_customer_group in ("A Zone", "B Zone", "D Zone")
			and	si.posting_date between '{between_date[0]}' and '{between_date[1]}' {conditions}
		GROUP BY
			si.customer
		ORDER BY
			SUM(si.total) desc
		LIMIT {filters.get('list_limit')}
	""", as_dict = 1)

	return data


@frappe.whitelist(allow_guest=True)
def get_period_date_ranges(period, fiscal_year=None, year_start_date=None):
	from dateutil.relativedelta import relativedelta

	if not year_start_date:
		year_start_date, year_end_date = frappe.get_cached_value(
			"Fiscal Year", fiscal_year, ["year_start_date", "year_end_date"]
		)

	increment = {"Monthly": 1, "Quarterly": 3, "Half-Yearly": 6, "Yearly": 12}.get(period)

	period_date_ranges = []
	for i in range(1, 13, increment):
		period_end_date = getdate(year_start_date) + relativedelta(months=increment, days=-1)
		if period_end_date > getdate(year_end_date):
			period_end_date = year_end_date
		period_date_ranges.append([year_start_date, period_end_date])
		year_start_date = period_end_date + relativedelta(days=1)
		if period_end_date == year_end_date:
			break

	return period_date_ranges