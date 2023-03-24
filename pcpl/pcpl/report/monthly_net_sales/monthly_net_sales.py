# Copyright (c) 2023, Finbyz Tech. Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, getdate
from itertools import zip_longest


def execute(filters=None):
	data = get_data(filters)
	return data


def get_data(filters):

	doctype = "Sales Invoice"
	field = "total"
	territory_condition = " and is_secondary_ = 0"
	docstatus_cond = "si.docstatus = 1 and "

	if filters.get('show_secondary'):
		doctype = "Sales Secondary"
		field = "total_amount"
		territory_condition = "and is_secondary_ = 1"
		docstatus_cond = ""

	columns = [
		{
			"fieldname": "month",
			"label": ("Month"),
			"fieldtype": "Data",
			"width": 100
		},
	]

	terr = frappe.db.sql(f"""
			SELECT Distinct name, lft, rgt from `tabTerritory` where territory_type = 'Zone' {territory_condition}
		""", as_dict =1)

	terr_dict = {}

	for row in terr:
		columns.append(
			{ "label": _(f"{row.name} - {filters.get('fiscal_year1')}"),"fieldname": f"{row.name}_{filters.get('fiscal_year1')}","fieldtype": "Currency", "width": 150})
		columns.append(
			{ "label": _(f"{row.name} - {filters.get('fiscal_year2')}"),"fieldname": f"{row.name}_{filters.get('fiscal_year2')}","fieldtype": "Currency", "width": 150})
	
		terr_dict.update({row.name : [row.lft, row.rgt]})

	columns.append(
			{ "label": _(f"Total - {filters.get('fiscal_year1')}"),"fieldname": f"Total_{filters.get('fiscal_year1')}","fieldtype": "Currency", "width": 180})
	columns.append(
			{ "label": _(f"Total - {filters.get('fiscal_year2')}"),"fieldname": f"Total_{filters.get('fiscal_year2')}","fieldtype": "Currency", "width": 180})
	columns.append(
			{ "label": _("Difference"),"fieldname": "diff","fieldtype": "Currency", "width": 200})

	bet_dates1 = get_period_date_ranges(period = "Monthly", fiscal_year = filters.get("fiscal_year1"))
	bet_dates2 = get_period_date_ranges(period = "Monthly", fiscal_year = filters.get("fiscal_year2"))

	month_list = []
	if bet_dates1:
		for dt in bet_dates1:
			if get_mon(dt[0]) not in month_list:
				month_list.append(get_mon(dt[0]))
		
	
	result1 = {f"{month_list[i]}_{filters.get('fiscal_year1')}": bet_dates1[i] for i in range(len(month_list))}
	result2 = {f"{month_list[i]}_{filters.get('fiscal_year2')}": bet_dates2[i] for i in range(len(month_list))}

	final_list = []

	for row in month_list:
		si_data = []
		for terr in terr_dict:
			si_data.append(frappe.db.sql(f"""
				SELECT 
					IF(si.{field}, SUM(si.{field}), 0) as total, '{terr}_{filters.get('fiscal_year1')}' as territory, '{filters.get('fiscal_year1')}' as fiscal_year
				FROM
					`tab{doctype}` as si
				WHERE
					{docstatus_cond} si.territory in (select name from `tabTerritory` where lft >= {flt(terr_dict[terr][0])} and rgt <= {flt(terr_dict[terr][1])}) and si.posting_date >= '{result1[f"{row}_{filters.get('fiscal_year1')}"][0]}' and si.posting_date <= '{result1[f"{row}_{filters.get('fiscal_year1')}"][1]}'
			""", as_dict = 1))

			si_data.append(frappe.db.sql(f"""
				SELECT 
					IF(si.{field}, SUM(si.{field}), 0) as total, '{terr}_{filters.get('fiscal_year2')}' as territory, '{filters.get('fiscal_year2')}' as fiscal_year
				FROM
					`tab{doctype}` as si
				WHERE
					{docstatus_cond} si.territory in (select name from `tabTerritory` where lft >= {flt(terr_dict[terr][0])} and rgt <= {flt(terr_dict[terr][1])}) and si.posting_date >= '{result2[f"{row}_{filters.get('fiscal_year2')}"][0]}' and si.posting_date <= '{result2[f"{row}_{filters.get('fiscal_year2')}"][1]}'
			""", as_dict = 1))

		final_data = {'month' : row}
		fiscal_total = {}
		for data in si_data:
			if fiscal_total.get(data[0]['fiscal_year']):
				fiscal_total[data[0]['fiscal_year']] += flt(data[0].total)
			else:
				fiscal_total[data[0]['fiscal_year']] = flt(data[0].total)
			final_data.update({data[0]['territory'] : data[0].total})
		
		final_data.update({f"Total_{filters.get('fiscal_year1')}" : fiscal_total[filters.get('fiscal_year1')], f"Total_{filters.get('fiscal_year2')}" : fiscal_total[filters.get('fiscal_year2')], 'diff' : (fiscal_total[filters.get('fiscal_year2')] - fiscal_total[filters.get('fiscal_year1')])})

		final_list.append(final_data)

	return columns, final_list

def get_mon(dt):
	return getdate(dt).strftime("%B")

def diff_month(d1, d2):
	return (d1.year - d2.year) * 12 + d1.month - d2.month

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
