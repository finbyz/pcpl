# Copyright (c) 2023, STPL and contributors
# For license information, please see license.txt

import frappe
import frappe
import itertools
from dateutil.relativedelta import relativedelta
from frappe import _
from frappe.utils import getdate
from datetime import datetime


def execute(filters={'year':'2023-2024'}):
	columns, data = [], []
	data  = get_final_data(filters)
	columns = get_columns()
	return columns, data

def get_last_terretory_data(filters={'year':'2023-2024'}):
	lft,rgt=frappe.db.get_value("Territory",'Secondary Party',['lft','rgt'])
	conditions = ""
	if filters.get('year'):
		conditions += f" and td.fiscal_year = '{filters.get('year')}'"
	data = frappe.db.sql(f""" Select  sum(td.target_amount) as target_amount,te.parent_territory as territory
			From `tabTerritory` as te
			left join `tabTarget Detail` as td ON td.parent = te.name
			where te.is_group = 0 and td.target_amount > 0 {conditions} and te.lft>={lft} and te.rgt<={rgt} 
			Group By te.parent_territory """ , as_dict = 1 )

	for row in data:
		parent_territory = frappe.db.get_value("Territory" , row.territory , 'parent_territory')
		if parent_territory:
			row.update({'parent_territory':parent_territory})
	
	new_data = []
	new_dict = {}
	for row in data:
		if not new_dict.get(row.get('parent_territory')):
			new_dict[row.get('parent_territory')] = row.get('target_amount')
		else:
			new_dict[row.get('parent_territory')] = new_dict[row.get('parent_territory')] + row.get('target_amount')
	perr_terr = []
	for row in data:
		zone_dict = {}
		if row.get('parent_territory') not in perr_terr:
			perr_terr.append(row.get('parent_territory'))
			zone_dict.update({ 'target_amount':new_dict[row.parent_territory],'territory':row.parent_territory ,'parent_territory':frappe.db.get_value('Territory' , row.parent_territory , 'parent_territory')})
			new_data.append(zone_dict)
	data = new_data
	return data

def get_period_date_ranges(filters={'year':'2023-2024','quarter':'Quarter 1'}):
	year = filters.get('year')
	period_date_ranges = {}
	year_list=year.split('-')
	period_date_ranges={
		'quarter_1':{'period_start_date':'{}-4-1'.format(year_list[0]),'period_end_date':'{}-6-30'.format(year_list[0])},
		'quarter_2':{'period_start_date':'{}-7-1'.format(year_list[0]),'period_end_date':'{}-9-30'.format(year_list[0])},
		'quarter_3':{'period_start_date':'{}-10-1'.format(year_list[0]),'period_end_date':'{}-12-31'.format(year_list[0])},
		'quarter_4':{'period_start_date':'{}-1-1'.format(year_list[1]),'period_end_date':'{}-3-31'.format(year_list[0])},
	}
	return period_date_ranges


def get_final_data(filters={'year':'2023-2024','quarter':'Quarter 1'}):
	period_date_ranges = get_period_date_ranges(filters)
	territory_data = get_last_terretory_data(filters)    
	final_data = {}
	for row in territory_data:
		terr_list = []
		if row.get('territory') not in terr_list:
			terr_list.append(row.get('territory'))
			sub_terr = frappe.db.get_list("Territory" , {'parent_territory':row.get('territory')},pluck='name')
			for d in sub_terr:
				if d not in terr_list:
					terr_list.append(d)
					sub_of_sub = frappe.db.get_list("Territory" , {'parent_territory':d},pluck='name')
					if sub_of_sub:
						for l in sub_of_sub:
							if l not in terr_list:
								terr_list.append(l)
								sub_of_sub_l = frappe.db.get_list("Territory" , {'parent_territory':d},pluck='name')
								terr_list += sub_of_sub_l
		conditions = ''
		conditions += "  si.territory in {} ".format(
			"(" + ", ".join([f'"{l}"' for l in terr_list]) + ")")
		total =0 
		for d in ['quarter_1','quarter_2','quarter_3','quarter_4']:
			duplicate_row = {}
			date_condi = ""
			date_condi += f" and si.posting_date Between '{period_date_ranges[d].get('period_start_date')}' and '{period_date_ranges[d].get('period_end_date')}'"
			gross_sales = frappe.db.sql(f''' SELECT si.total_amount as amount
											From `tabSales Secondary` as si 
											Where {conditions} {date_condi} and si.cn=0 and si.transfer_cn=0''',as_dict = 1)	
			
			duplicate_row.update(row)
			sum_gross_sales  = sum(d.get('amount') for d in gross_sales) if gross_sales else 0
			duplicate_row.update({'{}'.format(d):sum_gross_sales})
			total+=sum_gross_sales
			if duplicate_row:
				if not final_data.get((row.get('parent_territory'), row.get('territory'))):
					final_data[(row.get('parent_territory'),row.get('territory'))]={}
				final_data[(row.get('parent_territory'),row.get('territory'))].update(duplicate_row)
			final_data[(row.get('parent_territory'),row.get('territory'))].update({'total':total})
		for j in ['quarter_1','quarter_2','quarter_3','quarter_4']:
			final_data[(row.get('parent_territory'),row.get('territory'))].update({'{}_share'.format(j):(final_data[(row.get('parent_territory'),row.get('territory'))].get(j)*100/final_data[(row.get('parent_territory'),row.get('territory'))].get('total'))})
		final_data[(row.get('parent_territory'),row.get('territory'))].update({'difference':(final_data[(row.get('parent_territory'),row.get('territory'))].get('total')-final_data[(row.get('parent_territory'),row.get('territory'))].get('target_amount'))})
		final_data[(row.get('parent_territory'),row.get('territory'))].update({'achievement':(final_data[(row.get('parent_territory'),row.get('territory'))].get('total')*100/final_data[(row.get('parent_territory'),row.get('territory'))].get('target_amount'))})
	# print(list(final_data.values()))
	return list(final_data.values())

def get_columns():
	columns = []
	columns += [
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
		"label": "Quarter 1",
		"fieldname": "quarter_1",
		"fieldtype": "Currency",
		"width": 120,
		"precision":2
		},
		{
		"label": "Quarter 1 Share",
		"fieldname": "quarter_1_share",
		"fieldtype": "Percent",
		"width": 120,
		"precision":2
		},
		{
		"label": "Quarter 2",
		"fieldname": "quarter_2",
		"fieldtype": "Currency",
		"width": 120,
		"precision":2
		},
		{
		"label": "Quarter 2 Share",
		"fieldname": "quarter_2_share",
		"fieldtype": "Percent",
		"width": 120,
		"precision":2
		},
		{
		"label": "Quarter 3",
		"fieldname": "quarter_3",
		"fieldtype": "Currency",
		"width": 120,
		"precision":2
		},
		{
		"label": "Quarter 3 Share",
		"fieldname": "quarter_3_share",
		"fieldtype": "Percent",
		"width": 120,
		"precision":2
		},
		{
		"label": "Quarter 4",
		"fieldname": "quarter_4",
		"fieldtype": "Currency",
		"width": 120,
		"precision":2
		},
		{
		"label": "Quarter 4 Share",
		"fieldname": "quarter_4_share",
		"fieldtype": "Percent",
		"width": 120,
		"precision":2
		},
		{
		"label": "Total",
		"fieldname": "total",
		"fieldtype": "Currency",
		"width": 120,
		"precision":2
		},
		{
		"label": "Target Amount",
		"fieldname": "target_amount",
		"fieldtype": "Currency",
		"width": 120,
		"precision":2
		},
				{
		"label": "Difference",
		"fieldname": "difference",
		"fieldtype": "Currency",
		"width": 120,
		"precision":2
		},
		{
		"label": "Achievement(%)",
		"fieldname": "achievement",
		"fieldtype": "Percent",
		"width": 120,
		"precision":2
		}		
	]
	return columns