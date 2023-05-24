# Copyright (c) 2023, STPL and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns, data = [], []
	data = get_data(filters)
	columns = get_column(filters)
	return columns, data

def get_prepare_data(filters):
	lft,rgt=frappe.db.get_value("Territory",{'is_group':1,'is_secondary_':1,'territory_type':None},['lft','rgt'])
	data = frappe.db.sql(f""" Select sum(td.target_amount) as target_amount , te.parent_territory as territory
			From `tabTerritory` as te
			left join `tabTarget Detail` as td ON td.parent = te.name
			where  td.target_amount > 0 and te.lft>={lft} and te.rgt={rgt}
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
			zone_dict.update({'target_amount':new_dict[row.parent_territory] , 'territory':row.parent_territory , 'parent_territory':frappe.db.get_value('Territory' , row.parent_territory , 'parent_territory')})
			new_data.append(zone_dict)
	data = new_data
	month_div = {}
	div_target = []
	for row in data:
		tare_data_list = frappe.db.get_list('Territory' , {'parent_territory':row.get('territory')} , pluck = 'name')
		for d in tare_data_list:
			div_target += frappe.db.sql(f""" Select te.parent_territory , mdp.month , mdp.percentage_allocation ,sum(td.target_amount) as target_amount
										From `tabTerritory` as te
										left join`tabTarget Detail` as td ON te.name = td.parent 
										left join `tabMonthly Distribution Percentage` as mdp on td.distribution_id = mdp.parent
										Where te.parent_territory = '{d}'
										group by mdp.month
									""",as_dict =1 )
	perr_terr = []
	total = {}
	for row in div_target:
		row.update({'territory':frappe.db.get_value("Territory",row.get('parent_territory') , 'parent_territory')})            
		perr_terr.append(row.get('territory'))
		
	from itertools import groupby
	def key_func(k):
		return k['territory']

	# sort INFO data by 'company' key.
	INFO = sorted(div_target, key=key_func)

	for key, value in groupby(INFO, key_func):
		target = 0
		
		for d in list(value):
			if d.get('percentage_allocation') and d.get('target_amount'):
				if not total.get((key , d.month)):
					total[key , d.month] = {'month':d.month ,'percentage_allocation':d.percentage_allocation , 'target_amount':d.target_amount }
				elif total.get((key , d.month)).get('target_amount'):
					total.get((key , d.month)).update({'target_amount':total.get((key , d.month)).get('target_amount')+d.target_amount })
	terri_list = []
	terr_map_month = {}
	for row in data:
		if terr_map_month.get(row.get('territory')):
			row.update(terr_map_month.get(row.get('territory')))
	return data

def get_range(filters):
	year_range = filters.get('year')
	year_ = year_range.split('-')
	first_date = '{}-4-1'.format(year_[0] )
	last_date = '{}-3-31'.format(year_[1] )
	return first_date , last_date

def get_data(filters):
	final_data =[]
	data = get_prepare_data(filters)
	for row in data:
		gross_sa = 0
		return_cn = 0
		total_ns = 0
		total_ach = 0
		total_cnp = 0
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
		conditions += " si.territory in {} ".format(
			"(" + ", ".join([f'"{l}"' for l in terr_list]) + ")")
		# print(conditions)
		first_date , last_date = get_range(filters)
		date_condi = ""
		date_condi += f" and si.posting_date Between '{first_date}' and '{last_date}'"
		gross_sales = frappe.db.sql(f''' SELECT sii.qty , sii.rate , si.territory  
										From `tabSales Secondary` as si 
										left join `tabSales Secondary Item` as sii ON si.name = sii.parent 
										Where  {conditions} {date_condi} ''',as_dict = 1)	
		sales_return = frappe.db.sql(f''' SELECT sii.qty , sii.rate , si.territory 
										From `tabSales Secondary` as si 
										left join `tabSales Secondary Item` as sii ON si.name = sii.parent 
										Where {conditions} and si.cn = 1 {date_condi}  ''',as_dict = 1)
		
		sales_return_draft = frappe.db.sql(f''' SELECT sii.qty , sii.rate , si.territory 
										From `tabSales Secondary` as si 
										left join `tabSales Secondary Item` as sii ON si.name = sii.parent 
										Where {conditions} and si.transfer_cn = 1 {date_condi}  ''',as_dict = 1)
		duplicate_row = {}
		duplicate_row.update(row)
		sum_gross_sales  = sum(d.get('qty') * d.get('rate') for d in gross_sales) if gross_sales else 0
		duplicate_row.update({'gross_sales':sum_gross_sales})
		gross_sa += sum_gross_sales
		sales_return_total = sum(d.get('qty') * d.get('rate') for d in sales_return) if sales_return else 0
		duplicate_row.update({'sales_return_total':sales_return_total})
		return_cn += sales_return_total
		total_sales_return_draft = sum(d.get('qty') * d.get('rate') for d in sales_return_draft) if sales_return_draft else 0
		duplicate_row.update({'total_sales_return_draft':total_sales_return_draft})
		NS = (sum_gross_sales) + (sales_return_total)
		total_ns += NS
		duplicate_row.update({'net_sales':NS})
		ach = (NS*100 / row.get('target_amount')) if row.get('target_amount') else 0
		total_ach += ach
		duplicate_row.update({'achivement':ach})
		gs = sum_gross_sales
		print(gs , sales_return_total)
		if len(gross_sales) > 0:
			duplicate_row.update({'cn_percentage':((((sales_return_total *-1) + (total_sales_return_draft))/gs)* 100) if gs != 0 else 0 })
		else:
			duplicate_row.update({'cn_percentage':0})
		final_data.append(duplicate_row)
	return final_data
def get_column(filters):
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
		"label": "Target Amount",
		"fieldname": "target_amount",
		"fieldtype": "Float",
		"width": 150
		},
		{
		"label": "Gross Sales",
		"fieldname": "gross_sales",
		"fieldtype": "Float",
		"width": 150,
		'precision':2
		},
		{
		"label": "Sales Return",
		"fieldname": "sales_return_total",
		"fieldtype": "Float",
		"width": 150,
		'precision':2
		},
		{
		"label": "Sales Return in Draft",
		"fieldname": "total_sales_return_draft",
		"fieldtype": "Float",
		"width": 150,
		'precision':2
		},
		{
		"label": "Net Sales",
		"fieldname": "net_sales",
		"fieldtype": "Float",
		"width": 150,
		'precision':2
		},
		{
		"label": "Achivement",
		"fieldname": "achivement",
		"fieldtype": "Float",
		"width": 150,
		'precision':2
		},
		{
		"label": "CN per",
		"fieldname": "cn_percentage",
		"fieldtype": "Float",
		"width": 150,
		'precision':2
		}
	]
	return columns