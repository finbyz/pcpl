# Copyright (c) 2023, STPL and contributors
# For license information, please see license.txt
import frappe
from dateutil.relativedelta import relativedelta
from frappe import _
from datetime import datetime
from frappe.utils import (flt,getdate,today,)


def execute(filters = {'year' : '2023-2024' , 'base_on':'Monthly' , 'group_by':'Zone' ,'select_month':['April'],'item_group':['1305 PC Inhaler (F)','1301 Baby Care Rub (F)']}):
	if filters.get('base_on') == 'Monthly' and not filters.get('select_month'):
		frappe.throw('Please Select Month in Filter ')
	if filters.get('base_on') == 'Weekly' and not filters.get('month'):
		frappe.throw('Please Select Month in Filter ')
	columns, data = [], []
	data , columns = get_final_data(filters)
	return columns, data

def get_last_terretory_data(filters ):
	conditions = ""
	if filters.get('year'):
		conditions += f" and td.fiscal_year = '{filters.get('year')}'"
	
	data = frappe.db.sql(f''' SELECT te.name as territory , te.parent_territory 
							From `tabTerritory` as te
							left join `tabTarget Detail` as td ON td.parent = te.name 
							where td.target_amount > 0 and  is_secondary_ = 0 {conditions}''',as_dict=1)
	

	if filters.get('group_by') in ['Division','Zone']:
		conditions = ""
		if filters.get('year'):
			conditions += f" and td.fiscal_year = '{filters.get('year')}'"
		data = frappe.db.sql(f""" Select  te.parent_territory as territory
				From `tabTerritory` as te
				left join `tabTarget Detail` as td ON td.parent = te.name
				where te.is_group = 0 and td.target_amount > 0 and is_secondary_ = 0  {conditions}
				Group By te.parent_territory """ , as_dict = 1 )
		for row in data:
			parent_territory,lft,rgt = frappe.db.get_value("Territory" , row.territory ,['parent_territory','lft','rgt'])
			if parent_territory:
				row.update({'parent_territory':parent_territory,'lft':lft,'rgt':rgt})
		
		new_data = []
		if filters.get('group_by') == 'Zone':

			perr_terr = []
			for row in data:
				zone_dict = {}
				if row.get('parent_territory') not in perr_terr:
					perr_terr.append(row.get('parent_territory'))
					parent_territory,lft,rgt = frappe.db.get_value("Territory" , row.parent_territory ,['parent_territory','lft','rgt'])
					if parent_territory not in ['All Territories','India']:
						zone_dict.update({'territory':row.parent_territory , 'parent_territory':parent_territory,'lft':lft,'rgt':rgt})
						new_data.append(zone_dict)
			data = new_data
			
	return data
def get_period_date_ranges(filters= {'year' : '2023-2024' , 'base_on':'Date Range' , 'group_by':'Divison' ,'start_date':'01-05-2023','end_date':'01-06-2023'}):
	mon_dict = {
		'January':1,'February':2,'March':3,'April':4,'May':5,'June':6,'July':7,'August':8,'September':9,'October':10,'November':11,'December':12
	}

	if filters.get('month'):
		month = mon_dict.get(filters.get('month'))
	import datetime
	
	today = datetime.date.today()

	year = filters.get('year')

	import calendar
	
	if filters.get('month'):
		year_list=year.split('-')
		if month in [1,2,3] :
			year_ = year_list[1]
		else:
			year_ = year_list[0]
		day = list(calendar.monthrange(int(year_), month))
		last_day = day[1]

		month_first_date = '{}-{}-1'.format(year_ , mon_dict.get(filters.get('month')) )
		month_last_date = '{}-{}-{}'.format(year_ , mon_dict.get(filters.get('month')) , last_day)
		
		from datetime import datetime

		month_first_date = datetime.strptime(month_first_date, '%Y-%m-%d').date()
		month_last_date = datetime.strptime(month_last_date, '%Y-%m-%d').date()
		if not (filters.get('from_date') and filters.get('to_date')):
			total_week = weeks_between( month_first_date ,month_last_date )
		else:
			month_first_date = datetime.strptime(filters.get('from_date'), '%Y-%m-%d').date()
			month_last_date = datetime.strptime(filters.get('to_date'), '%Y-%m-%d').date()
			total_week = weeks_between( month_first_date, month_last_date)
	period_date_ranges = []
	
	if filters.get('base_on') == 'Weekly':
		for i in range(1, total_week + 1, 1):
			month_first_date = getdate(month_first_date)
			period_end_date = getdate(month_first_date) + relativedelta(weeks=1, days=-1)
			if period_end_date > getdate(month_last_date):
				period_end_date = getdate(month_last_date)
			period_date_ranges.append({'period_start_date':month_first_date, 'period_end_date':period_end_date})
			month_first_date = period_end_date + relativedelta(days=1)
			if period_end_date == month_last_date:
				break
	
	if filters.get('base_on') =='Quarterlly':
		period_date_ranges = []
		year_list=year.split('-')
		doc = frappe.get_doc("Monthly Distribution" , str(filters.get('quarter')))
		quarter_mon = []
		for row in doc.get('percentages'):
			quarter_mon.append(row.month)
			if row.month in ['January','February' , 'March']:
				year__ = year_list[1]
			else:
				year__ = year_list[0]
		for row in range(len(doc.percentages)):
			day = list(calendar.monthrange(int(year__), mon_dict.get(quarter_mon[row])))
			last_day = day[1]
			month_first_date = '{}-{}-1'.format(year__ , mon_dict.get(quarter_mon[row]) )
		
			month_last_date = '{}-{}-{}'.format(year__ , mon_dict.get(quarter_mon[row]) , last_day)
			period_date_ranges.append({'period_start_date':month_first_date , 'period_end_date':month_last_date})


	if filters.get('base_on') == 'Monthly' and filters.get('select_month'):
		quarter_mon = []
		period_date_ranges = []
		year = str(filters.get('year'))
		year_list=year.split('-')
		mon_dict = {
				'January':1,'February':2,'March':3,'April':4,'May':5,'June':6,'July':7,'August':8,'September':9,'October':10,'November':11,'December':12
			}
		import calendar
		for j ,row  in enumerate(filters.get('select_month')):
			quarter_mon.append(row)
			if row in ['January','February' , 'March']:

				year__ = year_list[1]
			else:
				year__ = year_list[0]
			day = list(calendar.monthrange(int(year__), mon_dict.get(row)))
			last_day = day[1]
			month_first_date = '{}-{}-1'.format(year__ , mon_dict.get(row) )

			month_last_date = '{}-{}-{}'.format(year__ , mon_dict.get(row) , last_day)
			period_date_ranges.append({'period_start_date':month_first_date , 'period_end_date':month_last_date})
	if filters.get('base_on')=="Date Range":
		if filters.get('start_date') and filters.get('end_date'):
			period_date_ranges.append({'period_start_date':filters.get('start_date') , 'period_end_date':filters.get('end_date')})
				
	return period_date_ranges

def get_final_data(filters):
	period_date_ranges = get_period_date_ranges(filters)
	territory_data = get_last_terretory_data(filters)    
	final_data = {}
	columns=[]
	for l in filters.get("item_group"): 
		con=""
		con += " and sii.item_group = '{}' ".format(l)
		for row in territory_data:
			if filters.get('group_by') in ['Division','Zone']:
				terr_list = frappe.db.get_all('Territory',{'lft': ['>=', row.get('lft')],'rgt':['<=',row.get('rgt')]})
				conditions = ''
				conditions += " and si.territory in {} ".format(
					"(" + ", ".join([f'"{l.name}"' for l in terr_list]) + ")")
			
			if filters.get('group_by') == "Sub Division":
				conditions = ""
				conditions += "and si.territory = '{}'".format(row.territory)
			gross_sa = 0
			gross_ps = 0

			for d in period_date_ranges:
				
				mon_dict = {
				1:'January',2:'February',3:'March',4:'April',5:'May',6:'June',7:'July',8:'August',9:'September',10:'October',11:'November',12:'December'
				}
				from frappe.utils import flt, get_datetime
				duplicate_row = {}
				if not filters.get("item_group"):
					frappe.throw("Please select the Item Group")
				

				date_condi = ''
				date_condi += f' and si.posting_date >= "{d.get("period_start_date")}" and si.posting_date <="{d.get("period_end_date")}"'
				gross_sales = frappe.db.sql(f''' SELECT sii.qty , sii.price_list_rate , si.territory 
												From `tabSales Invoice` as si 
												left join `tabSales Invoice Item` as sii ON si.name = sii.parent 
												Where si.docstatus = 1 and si.is_return = 0 {conditions} {date_condi} {con} ''',as_dict = 1)
				date_condi = ""
				date_condi += f" and si.transaction_date >= '{d.get('period_start_date')}' and si.transaction_date <='{d.get('period_end_date')}'"
				pending_sales = frappe.db.sql(f''' SELECT sii.qty , sii.price_list_rate , si.territory ,(sii.qty - sii.delivered_qty) AS pending_qty
												From `tabSales Order` as si 
												left join `tabSales Order Item` as sii ON si.name = sii.parent 
												Where si.docstatus = 1  {conditions} {date_condi} {con} ''',as_dict = 1)	
				
				
				duplicate_row.update(row)
				sum_gross_sales  = sum(d.get('qty') * d.get('price_list_rate') for d in gross_sales) if gross_sales else 0


				duplicate_row.update({'{}-to-{}gross_sales{}'.format(d.get('period_start_date') , d.get('period_end_date'),l):sum_gross_sales, 'week' : '{}-to-{}'.format(d.get('period_start_date') , d.get('period_end_date'))})
				sum_pending_sales  = sum(d.get('pending_qty') * d.get('price_list_rate') for d in pending_sales) if pending_sales else 0
				duplicate_row.update({'{}-to-{}pending_sales{}'.format(d.get('period_start_date') , d.get('period_end_date'),l):sum_pending_sales, 'week' : '{}-to-{}'.format(d.get('period_start_date') , d.get('period_end_date'))})


				Total = (sum_gross_sales) + (sum_pending_sales)
				duplicate_row.update({'{}-to-{}total{}'.format(d.get('period_start_date') , d.get('period_end_date'),l):Total})
				if duplicate_row:
					if not final_data.get((row.get('parent_territory'),row.get('zone') , row.get('territory'))):
						final_data[(row.get('parent_territory'),row.get('zone'), row.get('territory'))]={}
					final_data[(row.get('parent_territory'),row.get('zone') ,row.get('territory'))].update(duplicate_row)



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
		}
		]

		if filters.get('base_on') in ['Monthly' , 'Quarterlly']:
			mon_dict = {1:'January',2:'February',3:'March',4:'April',5:'May',6:'June',7:'July',8:'August',9:'September',10:'October',11:'November',12:'December'}
			from frappe.utils import flt, get_datetime
			for row in period_date_ranges:
				for i in filters.get("item_group"):

					columns += [
			
			{
			"label": _("{}({})({})".format(i ,mon_dict.get(get_datetime(row.get('period_start_date')).month),'GS')),
			"fieldname": "{}-to-{}{}{}".format(row.get('period_start_date') , row.get('period_end_date'),'gross_sales',i),
			"fieldtype": "Float",
			"width": 150,
			"precision":2
			},
			{
			"label": _("{}({})({})".format(i,mon_dict.get(get_datetime(row.get('period_start_date')).month),'PS')),
			"fieldname": "{}-to-{}{}{}".format(row.get('period_start_date') , row.get('period_end_date'),'pending_sales',i),
			"fieldtype": "Float",
			"width": 150,
			"precision":2
			},
			 {
			"label": _("{}({})({})".format(i,mon_dict.get(get_datetime(row.get('period_start_date')).month),'Total')),
			"fieldname": "{}-to-{}{}{}".format(row.get('period_start_date') , row.get('period_end_date'),'total',i),
			"fieldtype": "Float",
			"width": 150,
			"precision":2
			}
			 ]
				
		if filters.get('base_on')=='Date Range':
			for row in period_date_ranges:

				for i in filters.get('item_group'):
					columns +=[
					{
						"label":_("{}({})".format(i,'GS')),
						"fieldname": "{}-to-{}{}{}".format(row.get('period_start_date') , row.get('period_end_date'),'gross_sales',i),
						"fieldtype": "Float",
						"width": 200,
						"precision":2
					},
					{
						"label":_("{}({})".format(i,'PS')),
						"fieldname": "{}-to-{}{}{}".format(row.get('period_start_date') , row.get('period_end_date'),'pending_sales',i),
						"fieldtype": "Float",
						"width": 200,
						"precision":2
					},
					{
						"label":_("{}({})".format(i,'Total')),
						"fieldname": "{}-to-{}{}{}".format(row.get('period_start_date') , row.get('period_end_date'),'total',i),
						"fieldtype": "Float",
						"width": 200,
						"precision":2
					}
				]

		if filters.get('base_on') == 'Weekly' :

			for row in period_date_ranges:
				for i in filters.get('item_group'):
					columns += [
				{
				"label": _("({}){}-to-{}{}".format(i,row.get('period_start_date') , row.get('period_end_date'),'GS')),
				"fieldname": "{}-to-{}{}{}".format(row.get('period_start_date') , row.get('period_end_date'),'gross_sales',i),
				"fieldtype": "Float",
				"width": 200,
				"precision":2
				},
				{
				"label": _("({}){}-to-{}{}".format(i,row.get('period_start_date') , row.get('period_end_date'),'PS')),
				"fieldname": "{}-to-{}{}{}".format(row.get('period_start_date') , row.get('period_end_date'),'pending_sales',i),
				"fieldtype": "Float",
				"width": 150,
				"precision":2
				},
				{
				"label": _("({}){}-to-{}{}".format(i,row.get('period_start_date') , row.get('period_end_date'),'Total')),
				"fieldname": "{}-to-{}{}{}".format(row.get('period_start_date') , row.get('period_end_date'),'total',i),
				"fieldtype": "Float",
				"width": 150,
				"precision":2
				}
				]
	return list(final_data.values()) , columns

def weeks_between(start_date, end_date):
	from dateutil import rrule
	weeks = rrule.rrule(rrule.WEEKLY, dtstart=start_date, until=end_date)
	return weeks.count()
		