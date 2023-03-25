# Copyright (c) 2023, Finbyz Tech. Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, getdate
from itertools import zip_longest


def execute(filters):
	data = get_data(filters)
	return data


def get_data(filters):

	columns = [
		{
			"fieldname": "month",
			"label": ("Month"),
			"fieldtype": "Data",
			"width": 100
		},
	]
	territory_cond = ""
	if filters.get('zone'):
		territory_cond = f" and name = '{filters.get('zone')}'"
	terr = frappe.db.sql(f"""
			SELECT Distinct name, lft, rgt from `tabTerritory` where territory_type = 'Zone' {territory_cond} and is_secondary_ = 1
		""", as_dict =1)

	terr_dict = {f"{row.name}": (row.lft, row.rgt) for row in terr}

	for sec_type in ['CN', 'Transfer-CN', 'Net Sales', 'Target', 'Achieve']:
		fieldtype = "Currency"
		if sec_type == "Achieve":
			fieldtype = "Percent"
		for row in terr:
			columns.append(
				{ "label": _(f"{row.name} - {sec_type}"),"fieldname": f"{row.name}_{sec_type}","fieldtype": fieldtype, "width": 150})
		if not filters.get('zone'):
			columns.append(
					{ "label": _(f"{sec_type} - Total"),"fieldname": f"{sec_type}_total","fieldtype": fieldtype, "width": 150})

	bet_dates1 = get_period_date_ranges(period = "Monthly", fiscal_year = filters.get("fiscal_year"))

	month_list = []
	if bet_dates1:
		for dt in bet_dates1:
			if get_mon(dt[0]) not in month_list:
				month_list.append(get_mon(dt[0]))
		
	
	result1 = {f"{month_list[i]}_{filters.get('fiscal_year')}": bet_dates1[i] for i in range(len(month_list))}


	final_list = []

	for row in month_list:
		si_data = []
		final_data = {'month' : row}
		for sec_type in ['CN', 'Transfer-CN', 'Net Sales', 'Target']:
			condition = None
			if sec_type == "CN":
				condition = " and si.cn = 1"
			elif sec_type == "Transfer-CN":
				condition = "and si.transfer_cn = 1"
			elif sec_type == "Net Sales":
				condition = "and si.transfer_cn = 0 and si.cn = 0"
			final_dict = {'CN_total': 0, 'Transfer-CN_total' : 0, 'Net Sales_total': 0, 'Achieve_total': 0, 'Target_total' : 0}
			for terr in terr_dict:
				if condition:
					si_data.append(frappe.db.sql(f"""
						SELECT 
							IF(si.total_amount, SUM(si.total_amount), 0) as total, '{terr}_{sec_type}' as territory,'{sec_type}' as sec_type
						FROM
							`tabSales Secondary` as si
						WHERE
							si.territory in (select name from `tabTerritory` where lft >= {flt(terr_dict[terr][0])} and rgt <= {flt(terr_dict[terr][1])}) and si.posting_date >= '{result1[f"{row}_{filters.get('fiscal_year')}"][0]}' and si.posting_date <= '{result1[f"{row}_{filters.get('fiscal_year')}"][1]}' {condition}
					""", as_dict = 1))
				else:
					target_data = frappe.db.sql(f"""
						SELECT 
							SUM((td.target_amount * IFNULL(mdp.percentage_allocation, 1))/ 100) as total, '{terr}_{sec_type}' as territory, '{sec_type}' as sec_type
						FROM 
							`tabTerritory` as ter 
						JOIN 
							`tabTarget Detail` as td on ter.name = td.parent
						JOIN 
							`tabMonthly Distribution Percentage` as mdp on mdp.parent = td.distribution_id
						WHERE 
							ter.lft >= {flt(terr_dict[terr][0])} and ter.rgt <= {flt(terr_dict[terr][1])} and mdp.month = '{row}' and td.fiscal_year = '{filters.get('fiscal_year')}'
						GROUP BY 
							mdp.month
					""", as_dict = 1)
					if not target_data:
						target_data = [{'total': 0, 'territory': f'{terr}_{sec_type}', 'sec_type' : f'{sec_type}'}]
					si_data.append(target_data)

			for data in si_data:
				final_data.update({data[0]['territory'] : data[0].get('total')})

				if data[0]['sec_type'] == 'Net Sales':
					final_data.update({data[0]['territory'].replace("Net Sales", "Achieve") : data[0].get('total')})
				if data[0]['sec_type'] == 'Target':
					if data[0].get('total'):
						final_data[data[0]['territory'].replace("Target", "Achieve")] = (final_data[data[0]['territory'].replace("Target", "Achieve")] / (flt(data[0].get('total')) or 1)) * 100
					else:
						final_data[data[0]['territory'].replace("Target", "Achieve")] = 0
					final_dict['Achieve_total'] += flt(final_data[data[0]['territory'].replace("Target", "Achieve")])

				if data[0]['sec_type']:
					final_dict[f'{data[0]["sec_type"]}_total'] += flt(data[0].get('total'))

			if not filters.get('zone'):
				final_data.update({f"{sec_type}_total" : final_dict[f"{sec_type}_total"]})
		if not filters.get('zone'):
			final_data.update({"Achieve_total" : (final_dict['Achieve_total'] / len(terr_dict))})
		final_list.append(final_data)

	return columns, final_list

def get_mon(dt):
	return getdate(dt).strftime("%B")

# def diff_month(d1, d2):
# 	return (d1.year - d2.year) * 12 + d1.month - d2.month

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
