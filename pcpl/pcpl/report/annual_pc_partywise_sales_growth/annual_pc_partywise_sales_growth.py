# Copyright (c) 2023, STPL and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt, getdate, get_datetime


def execute(filters={"fiscal_year1":"2022-2023","fiscal_year2":"2023-2024"}):
	columns, data = [], []
	data  = get_final_data(filters)
	columns = get_cols(filters)
	return columns, data


def get_last_terretory_data(filters = None):
	data = frappe.db.sql(f""" Select  te.parent_territory as territory
				From `tabTerritory` as te
				left join `tabTarget Detail` as td ON td.parent = te.name
				where te.is_group = 0 and td.target_amount > 0 and is_secondary_ = 0 
				Group By te.parent_territory """ , as_dict = 1 )
	for row in data:
		parent_territory,lft,rgt = frappe.db.get_value("Territory" , row.territory ,['parent_territory','lft','rgt'])
		if parent_territory:
			row.update({'parent_territory':parent_territory,'lft':lft,'rgt':rgt})
			
	return data

def get_final_data(filters={"fiscal_year1":"2022-2023","fiscal_year2":"2023-2024"}):
	territory_data = get_last_terretory_data(filters=None)   
	fiscal_year1_bet_dates = get_period_date_ranges("Yearly", filters.get("fiscal_year1"))
	fiscal_year2_bet_dates = get_period_date_ranges("Yearly", filters.get("fiscal_year2"))
	final_data={}
	for row in territory_data:
		terr_list = frappe.db.get_all('Territory',{'lft': ['>=', row.get('lft')],'rgt':['<=',row.get('rgt')]})
		conditions = ''
		conditions += " and si.territory in {} ".format(
				"(" + ", ".join([f'"{l.name}"' for l in terr_list]) + ")")
		net_sales_fiscal_year_1 = frappe.db.sql(f'''select sum(sii.qty * sii.rate) as total_fiscal_year1 , si.customer, si.customer_city
											From `tabSales Invoice` as si 
											left join `tabSales Invoice Item` as sii ON si.name = sii.parent 
											Where si.docstatus = 1 {conditions} and si.posting_date between '{fiscal_year1_bet_dates[0][0]}' and '{fiscal_year1_bet_dates[0][1]}'
											Group By si.customer
											''',as_dict = 1)
		net_sales_fiscal_year_2 = frappe.db.sql(f'''select sum(sii.qty * sii.rate) as total_fiscal_year2,si.customer,si.customer_city
											From `tabSales Invoice` as si 
											left join `tabSales Invoice Item` as sii ON si.name = sii.parent 
											Where si.docstatus = 1 {conditions} and si.posting_date between '{fiscal_year2_bet_dates[0][0]}' and '{fiscal_year2_bet_dates[0][1]}'
											Group By si.customer
											''',as_dict = 1)

		for d in net_sales_fiscal_year_1:
			if not final_data.get((row.get('parent_territory') ,d.get('customer') ,row.get('territory'))):
				final_data[(row.get('parent_territory') ,d.get('customer') , row.get('territory'))]={}
			final_data[(row.get('parent_territory') ,d.get('customer') ,row.get('territory'))].update(d)
			final_data[(row.get('parent_territory') ,d.get('customer') ,row.get('territory'))].update(row)

		for r in net_sales_fiscal_year_2:
			if not final_data.get((row.get('parent_territory') ,r.get('customer') ,row.get('territory'))):
				final_data[(row.get('parent_territory') ,r.get('customer') , row.get('territory'))]={}
			final_data[(row.get('parent_territory') ,r.get('customer') ,row.get('territory'))].update(r)
			final_data[(row.get('parent_territory') ,r.get('customer') ,row.get('territory'))].update(row)
		# print(list(final_data.values()))
		for j in list(final_data.values()):
			fiscal_year_1 = j.get('total_fiscal_year1') if j.get('total_fiscal_year1') else 0
			fiscal_year_2 = j.get('total_fiscal_year2') if j.get('total_fiscal_year2') else 0
			j.update({'difference':(fiscal_year_1 - fiscal_year_2)})
			if fiscal_year_2:
				j.update({'growth': (j.get('difference')/fiscal_year_2 * 100)})
			# j.update({'growth':(fiscal_year_2 )})
		
	return list(final_data.values())
def get_cols(filters=None):
	columns = [
	{
	"label": "Zone",
	"fieldname": "parent_territory",
	"fieldtype": "Link",
	'options': 'Territory',
	"width": 150
	},
	{
	"label": "Division",
	"fieldname": "territory",
	"fieldtype": "Link",
	'options': 'Territory',
	"width": 150
	},
	{
	"label": "Customer",
	"fieldname": "customer",
	"fieldtype": "Link",
	'options': 'Customer',
	"width": 150
	},
	{
	"label": "Customer City",
	"fieldname": "customer_city",
	"fieldtype": "Data",
	"width": 150
	},
	{
	"label": "Net Sales ({})".format(filters.get("fiscal_year1")),
	"fieldname": "total_fiscal_year1",
	"fieldtype": "Float",
	"width": 150,
	"precision":2
	},
	{
	"label": "Net Sales({})".format(filters.get("fiscal_year2")),
	"fieldname": "total_fiscal_year2",
	"fieldtype": "Float",
	"width": 150,
	"precision":2
	},
	{
	"label": "Difference",
	"fieldname": "difference",
	"fieldtype": "Float",
	"width": 150,
	"precision":2
	},
	{
	"label": "Growth %",
	"fieldname": "growth",
	"fieldtype": "Float",
	"width": 150,
	"precision":2
	}

	]	
	return columns


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




	
	
