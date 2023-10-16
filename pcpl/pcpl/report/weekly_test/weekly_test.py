# Copyright (c) 2023, STPL and contributors
# For license information, please see license.txt

# import frappe


def execute(filters=None):
	columns, data = [], []
	return columns, data


def get_period_date_ranges(filters):
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
				
	return period_date_ranges


# def get_sub_division_wise_data(filters = {'year' : '2023-2024' , 'base_on':'Monthly' , 'group_by':'Zone' ,'select_month':['April']}):

# 	data = frappe.db.sql(f''' SELECT te.name as territory , td.target_amount , te.parent_territory 
# 							left join `tabTarget Detail` as td ON td.parent = te.name and td.fiscal_year = '{filters.get('year')}'"
# 							where td.target_amount > 0  ''',as_dict=1)
#     monthly_distribution_data = frappe.db.sql(f""" Select   """)