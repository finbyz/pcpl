# Copyright (c) 2022, STPL and contributors
# For license information, please see license.txt

import frappe
import itertools
from dateutil.relativedelta import relativedelta
from frappe import _
from frappe.utils import getdate
def execute(filters=None):
    columns, data = [], []
    data,columns  = gross_sales_data(filters )
    return columns, data

# def get_data(filters):
# 	get_target = prepare_tarretory_data()

def get_target():
    data = frappe.db.sql(f""" Select   te.parent_territory , sum(td.target_amount) as target_amount
                            from `tabTerritory` as te
                            left join `tabTarget Detail` as td on td.parent = te.name 
                            
                            Group By te.parent_territory 
                            Order By te.parent_territory """, as_dict = True)
    after_data = []
    for row in data:
        if row.parent_territory:
            zone = frappe.db.get_value('Territory' , row.parent_territory ,  'parent_territory')

            if zone:
                row.update({'zone':zone})
                after_data.append(row)

    return after_data

def prepare_tarretory_data():

    data = get_target()

    from itertools import groupby

    def key_func(k):
        return k['zone']

    INFO = sorted(data, key=key_func)
    target_data = []
    for key, value in groupby(INFO, key_func):
        target_data += list(value)
    return target_data

def gross_sales_data(filters ):
    
    mon_dict = {
        'January':1,'February':2,'March':3,'April':4,'May':5,'June':6,'July':7,'August':8,'September':9,'Octomber':10,'November':11,'December':12
    }

    if filters.get('month'):
        month = mon_dict.get(filters.get('month'))
    import datetime
    
    today = datetime.date.today()

    year = filters.get('year')

    import calendar

    day = list(calendar.monthrange(int(year), month))
    last_day = day[1]

    month_first_date = '{}-{}-1'.format(year , mon_dict.get(filters.get('month')) )
    month_last_date = '{}-{}-{}'.format(year , mon_dict.get(filters.get('month')) , last_day)
    
    from datetime import datetime

    month_first_date = datetime.strptime(month_first_date, '%Y-%m-%d').date()
    month_last_date = datetime.strptime(month_last_date, '%Y-%m-%d').date()
    territory_data = prepare_tarretory_data()
    
    total_week = weeks_between( month_first_date ,month_last_date )
    period_date_ranges = []

    for i in range(1, total_week + 1, 1):
        month_first_date = getdate(month_first_date)
        period_end_date = getdate(month_first_date) + relativedelta(weeks=1, days=-1)
        if period_end_date > getdate(month_last_date):
            period_end_date = getdate(month_last_date)
        period_date_ranges.append({'period_start_date':month_first_date, 'period_end_date':period_end_date})
        month_first_date = period_end_date + relativedelta(days=1)
        if period_end_date == month_last_date:
            break

    final_data = {}

    for row in territory_data:
        final_row={}
        
        conditions = ""
        territory_list = frappe.db.sql(f''' Select name From `tabTerritory` where parent_territory = '{row.parent_territory}' ''',as_dict = 1)
        conditions += " and si.territory in {} ".format(
            "(" + ", ".join([f'"{l.name}"' for l in territory_list]) + ")")
        
        count = 0
        for idx , d in enumerate(period_date_ranges):
            duplicate_row = {}
            date_condi = ""
            date_condi += f" and si.posting_date Between '{d.get('period_start_date')}' and '{d.get('period_end_date')}'"
            gross_sales = frappe.db.sql(f''' SELECT sii.qty , sii.rate , si.territory  
                                            From `tabSales Invoice` as si 
                                            left join `tabSales Invoice Item` as sii ON si.name = sii.parent 
                                            Where si.docstatus = 1  {conditions} {date_condi} ''',as_dict = 1)	
            
            sales_return = frappe.db.sql(f''' SELECT sii.qty , sii.rate , si.territory 
                                            From `tabSales Invoice` as si 
                                            left join `tabSales Invoice Item` as sii ON si.name = sii.parent 
                                            Where si.docstatus = 1 and is_return = 1 {conditions} {date_condi}  ''',as_dict = 1)
            
            sales_return_draft = frappe.db.sql(f''' SELECT sii.qty , sii.rate , si.territory 
                                            From `tabSales Invoice` as si 
                                            left join `tabSales Invoice Item` as sii ON si.name = sii.parent 
                                            Where si.status = 'Draft' and si.docstatus = 1 and is_return = 1 {conditions} {date_condi}  ''',as_dict = 1)
            

            duplicate_row.update(row)
            duplicate_row.update({'{}-to-{}gross_sales'.format(d.get('period_start_date') , d.get('period_end_date')):sum(d.get('qty') * d.get('rate') for d in gross_sales) if gross_sales else 0, 'week' : '{}-to-{}'.format(d.get('period_start_date') , d.get('period_end_date'))})

            duplicate_row.update({'{}-to-{}sales_return'.format(d.get('period_start_date') , d.get('period_end_date')):sum(d.get('qty') * d.get('rate') for d in sales_return) if sales_return else 0})
            
            duplicate_row.update({'{}-to-{}sales_return_draft'.format(d.get('period_start_date') , d.get('period_end_date')):sum(d.get('qty') * d.get('rate') for d in sales_return_draft) if sales_return_draft else 0})
            duplicate_row.update({'{}-to-{}ns'.format(d.get('period_start_date') , d.get('period_end_date')):(sum(d.get('qty') * d.get('rate') for d in gross_sales) if gross_sales else 0) - sum(d.get('qty') * d.get('rate') for d in sales_return) if sales_return else 0})
            duplicate_row.update({'{}-to-{}ach'.format(d.get('period_start_date') , d.get('period_end_date')):(((sum(d.get('qty') * d.get('rate') for d in gross_sales) if gross_sales else 0) - sum(d.get('qty') * d.get('rate') for d in sales_return) if sales_return else 0)/row.target_amount) if row.get('target_amount') else 0})
    
       

            if duplicate_row:
                if not final_data.get((row.get('parent_territory'),row.get('zone'))):
                    final_data[(row.get('parent_territory'),row.get('zone'))]={}


                final_data[(row.get('parent_territory'),row.get('zone'))].update(duplicate_row)
    
    columns=[
        {
				"label": "Zone",
				"fieldname": "zone",
				"fieldtype": "Data",
				"width": 150
				},
                {
				"label": "Target Amount",
				"fieldname": "target_amount",
				"fieldtype": "Data",
				"width": 150
				},
                {
				"label": "Parent Territory",
				"fieldname": "parent_territory",
				"fieldtype": "Data",
				"width": 150
				},
    ]
    # print(period_date_ranges)
    for row in period_date_ranges:
        columns += [
        {
        "label": _("{}-to-{}{}".format(row.get('period_start_date') , row.get('period_end_date'),'GS')),
        "fieldname": "{}-to-{}{}".format(row.get('period_start_date') , row.get('period_end_date'),'gross_sales'),
        "fieldtype": "Data",
        "width": 200
        },
        {
        "label": _("{}-to-{}{}".format(row.get('period_start_date') , row.get('period_end_date'),'CN')),
        "fieldname": "{}-to-{}{}".format(row.get('period_start_date') , row.get('period_end_date'),'sales_return'),
        "fieldtype": "Data",
        "width": 200
        },
        {
        "label": _("{}-to-{}<br>{}".format(row.get('period_start_date') , row.get('period_end_date'),'TCN')),
        "fieldname": "{}-to-{}{}".format(row.get('period_start_date') , row.get('period_end_date'),'sales_return_draft'),
        "fieldtype": "Data",
        "width": 200
        },
        {
        "label": _("{}-to-{}{}".format(row.get('period_start_date') , row.get('period_end_date'),'NS')),
        "fieldname": "{}-to-{}{}".format(row.get('period_start_date') , row.get('period_end_date'),'ns'),
        "fieldtype": "Data",
        "width": 200
        },
        {
        "label": _("{}-to-{}{}".format(row.get('period_start_date') , row.get('period_end_date'),'ACH%')),
        "fieldname": "{}-to-{}{}".format(row.get('period_start_date') , row.get('period_end_date'),'ach'),
        "fieldtype": "Data",
        "width": 200
        },
    ]
    return list(final_data.values()) , columns      
    # return columns


def weeks_between(start_date, end_date):
    from dateutil import rrule
    weeks = rrule.rrule(rrule.WEEKLY, dtstart=start_date, until=end_date)
    return weeks.count()




