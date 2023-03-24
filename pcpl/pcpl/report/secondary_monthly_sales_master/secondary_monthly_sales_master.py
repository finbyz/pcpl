# Copyright (c) 2023, Finbyz Tech. Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, getdate
from itertools import zip_longest


def execute(filters={'fiscal_year1':'2021-2022'}):
	data = get_data(filters)
	# return data


def get_data(filters):

	columns = [
		{
			"fieldname": "month",
			"label": ("Month"),
			"fieldtype": "Data",
			"width": 100
		},
	]

	terr = frappe.db.sql(f"""
			SELECT Distinct name, lft, rgt from `tabTerritory` where territory_type = 'Zone' and is_secondary_ = 1
		""", as_dict =1)

	terr_dict = {f"{row.name}": (row.lft, row.rgt) for row in terr}

	for type in ['CN', 'Transfer-CN', 'Net Sales', 'Target', 'Achieve']:
		for row in terr:
			columns.append(
				{ "label": _(f"{row.name} - {type}"),"fieldname": f"{row.name}_{type}","fieldtype": "Currency", "width": 150})
		columns.append(
				{ "label": _(f"{type} - Total"),"fieldname": f"{type}_total","fieldtype": "Currency", "width": 150})

	bet_dates1 = get_period_date_ranges(period = "Monthly", fiscal_year = filters.get("fiscal_year1"))

	month_list = []
	if bet_dates1:
		for dt in bet_dates1:
			if get_mon(dt[0]) not in month_list:
				month_list.append(get_mon(dt[0]))
		
	
	result1 = {f"{month_list[i]}_{filters.get('fiscal_year1')}": bet_dates1[i] for i in range(len(month_list))}


	final_list = []

	for row in month_list:
		si_data = []
		final_data = {'month' : row}
		for type in ['CN', 'Transfer-CN', 'Net Sales', 'Target', 'Achieve']:
			condition = None
			if type == "CN":
				condition = " and si.cn = 1"
			elif type == "Transfer-CN":
				condition = "and si.transfer_cn = 1"
			elif type == "Net Sales":
				condition = "and si.transfer_cn = 0 and si.cn = 0"

			for terr in terr_dict:
				if condition:
					si_data.append(frappe.db.sql(f"""
						SELECT 
							IF(si.total_amount, SUM(si.total_amount), 0) as total, '{terr}_{type}' as territory,'{type}' as type
						FROM
							`tabSales Secondary` as si
						WHERE
							si.docstatus = 1 and si.territory in (select name from `tabTerritory` where lft >= {flt(terr_dict[terr][0])} and rgt <= {flt(terr_dict[terr][1])}) and si.posting_date >= '{result1[f"{row}_{filters.get('fiscal_year1')}"][0]}' and si.posting_date <= '{result1[f"{row}_{filters.get('fiscal_year1')}"][1]}' {condition}
					""", as_dict = 1))
				else:
					si_data.append(frappe.db.sql(f"""
						SELECT 
							sum(td.target_amount) as target_amount, '{terr}_{type}' as territory,'{type}' as type
						FROM 
							`tabTerritory` as terr 
						JOIN 
							`tabTarget Detail` as td on terr.name = td.parent
						WHERE
							terr.lft >= {flt(terr_dict[terr][0])} and rgt <= {flt(terr_dict[terr][1])}
					""", as_dict = 1))
			total_cn=0
			total_tcn=0
			total_ns=0
			total_target=0
			total_ach=0
			for data in si_data:
				
				final_data.update({data[0]['territory'] : 1})
				if data[0]['type']:
					if data[0]['type'] =="CN":
						total_cn+=1	
					elif data[0]['type'] =="Transfer-CN":
						total_tcn+=1
					elif data[0]['type'] =="Net Sales":
						total_ns+=1
				
			if data[0]['type']=="CN":
				final_data.update({" CN - Total" : total_cn})
			elif data[0]['type']=="Transfer-CN":	
				final_data.update({"Transfer-CN - Total" : total_tcn})
			elif data[0]['type']=="Net Sales":	
				final_data.update({"Net Sales - Total" : total_ns})
			print(final_data)		
			
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
