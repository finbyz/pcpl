# Copyright (c) 2023, STPL and contributors
# For license information, please see license.txt
import frappe
import itertools
from dateutil.relativedelta import relativedelta
from frappe import _
from frappe.utils import getdate
from datetime import datetime


def execute(filters =None):
    columns, data = [], []
    data , columns = get_final_data(filters)
    return columns, data


def get_last_terretory_data(filters = {'year' : '2022-2023' , 'base_on':'Quarterlly' , 'group_by':'Division' , 'quarter':'Quarter 2'}):
    
    data = frappe.db.sql(f''' SELECT te.name as territory , td.target_amount , te.parent_territory , mdp.percentage_allocation , mdp.month, (td.target_amount * mdp.percentage_allocation)/100 as monthly_target
                            From `tabTerritory` as te
                            left join `tabTarget Detail` as td ON td.parent = te.name
                            left join `tabMonthly Distribution Percentage` as mdp ON td.distribution_id = mdp.parent
                            where td.target_amount > 0   ''',as_dict=1)

    for d in data:
        d.update({'{}_target'.format(d.month):d.monthly_target})

    if filters.get('group_by') in ['Division','Zone']:
        data = frappe.db.sql(f""" Select sum(td.target_amount) as target_amount , te.parent_territory as territory
                From `tabTerritory` as te
                left join `tabTarget Detail` as td ON td.parent = te.name
                where te.is_group = 0 and td.target_amount > 0
                Group By te.parent_territory """ , as_dict = 1 )
    
        for row in data:
            parent_territory = frappe.db.get_value("Territory" , row.territory , 'parent_territory')
            if parent_territory:
                row.update({'parent_territory':parent_territory})
        
        new_data = []
        if filters.get('group_by') == 'Zone':
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
    if filters.get("group_by") == 'Division':
        for row in data:
            div_target = frappe.db.sql(f""" Select te.parent_territory , mdp.month , mdp.percentage_allocation ,sum(td.target_amount) as target_amount
                                        From `tabTerritory` as te
                                        left join`tabTarget Detail` as td ON te.name = td.parent 
                                        left join `tabMonthly Distribution Percentage` as mdp on td.distribution_id = mdp.parent
                                        Where te.parent_territory = '{row.territory}' 
                                        group by mdp.month
                                      """,as_dict =1 )
            
            for d in div_target:
                if d.get('percentage_allocation') and d.get('target_amount'):
                    if not month_div.get(d.parent_territory):
                        month_div[d.parent_territory] = {}
                    month_div.get(d.parent_territory).update({'{}_{}'.format(d.month , 'target'):(d.target_amount * d.percentage_allocation)/100})
    
        for row in data:
            if month_div.get(row.territory):
                row.update(month_div.get(row.territory))

    if filters.get('group_by') == 'Zone':
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
        for row in div_target:
            if row.territory not in terr_map_month:
                terri_list.append(row.territory)
                terr_map_month[row.territory] = {}
            if total.get((row.territory,row.month)):
                terr_map_month.get(row.territory).update({'{}_{}'.format(row.month,'target'):(total.get((row.territory,row.month)).get('target_amount') * total.get((row.territory,row.month)).get('percentage_allocation'))/100})
        for row in data:
            if terr_map_month.get(row.get('territory')):
                row.update(terr_map_month.get(row.get('territory')))
    return data

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
    if filters.get('base_on') == 'Monthly' :
        period_date_ranges = []
        year_list=year.split('-')
        for row in range(13):
            import calendar
            # starting form april in fiscal year
            row_3=row+3
            if  row_3>=13:
                year_=year_list[1]
            else:
                year_=year_list[0]
            if row_3>12:
                # for strating month 1 after change year
                reset_row=(row%10)+1
                row_3=reset_row
            day = list(calendar.monthrange(int(year_), row_3))
            last_day = day[1]
            month_first_date = '{}-{}-1'.format(year_ , row_3 )
        
            month_last_date = '{}-{}-{}'.format(year_ , row_3 , last_day)
            period_date_ranges.append({'period_start_date':month_first_date , 'period_end_date':month_last_date})
        period_date_ranges.pop(0)

    return period_date_ranges



def get_final_data(filters):
    period_date_ranges = get_period_date_ranges(filters)
    territory_data = get_last_terretory_data(filters)    
    final_data = {}
    for row in territory_data:
        if filters.get('group_by') == 'Division':
            terr_list = []
            if row.territory not in terr_list:
                terr_list.append(row.territory)
                sub_terr = frappe.db.get_list("Territory" , {'parent_territory':row.territory},pluck='name')
                for d in sub_terr:
                    if d not in terr_list:
                        terr_list.append(d)
                        sub_of_sub = frappe.db.get_list("Territory" , {'parent_territory':d},pluck='name')
                        if sub_of_sub:
                            terr_list += sub_of_sub
            conditions = ''
            conditions += " and si.territory in {} ".format(
                "(" + ", ".join([f'"{l}"' for l in terr_list]) + ")")
        if filters.get('group_by') == 'Zone':
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
            conditions += " and si.territory in {} ".format(
                "(" + ", ".join([f'"{l}"' for l in terr_list]) + ")")
        if filters.get('group_by') == "Sub Division":
            conditions = ""
            conditions += "and si.territory = '{}'".format(row.territory)
        gross_sa = 0
        return_cn = 0
        total_ns = 0
        total_ach = 0
        total_cnp = 0
        for d in period_date_ranges:
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
            gross_sa += sum(d.get('qty') * d.get('rate') for d in gross_sales) if gross_sales else 0
            duplicate_row.update({'{}-to-{}sales_return'.format(d.get('period_start_date') , d.get('period_end_date')):(sum(d.get('qty') * d.get('rate') for d in sales_return)) if sales_return else 0})
            return_cn += sum(d.get('qty') * d.get('rate') for d in sales_return) if sales_return else 0
            duplicate_row.update({'{}-to-{}sales_return_draft'.format(d.get('period_start_date') , d.get('period_end_date')):sum(d.get('qty') * d.get('rate') for d in sales_return_draft) if sales_return_draft else 0})
            NS = (sum(d.get('qty') * d.get('rate') for d in gross_sales) if gross_sales else 0) + (sum(d.get('qty') * d.get('rate') for d in sales_return) if sales_return else 0)
            total_ns += NS
            duplicate_row.update({'{}-to-{}ns'.format(d.get('period_start_date') , d.get('period_end_date')):NS})
            ach = (NS / row.get('target_amount')) if row.get('target_amount') else 0
            total_ach += ach
            duplicate_row.update({'{}-to-{}ach'.format(d.get('period_start_date') , d.get('period_end_date')):ach})
            gs = sum(d.get('qty') * d.get('rate') for d in gross_sales)
            if len(gross_sales) > 0:
                duplicate_row.update({'{}-to-{}cnp'.format(d.get('period_start_date') , d.get('period_end_date')):((sum(d.get('qty') * d.get('rate') for d in sales_return) if sales_return else 0) + (sum(d.get('qty') * d.get('rate') for d in sales_return_draft) if sales_return_draft else 0))/gs if gs != 0 else 0 })
                total_cnp += ((sum(d.get('qty') * d.get('rate') for d in sales_return) if sales_return else 0) + (sum(d.get('qty') * d.get('rate') for d in sales_return_draft) if sales_return_draft else 0))/gs if gs != 0 else 0
            else:
                duplicate_row.update({'{}-to-{}cnp'.format(d.get('period_start_date') , d.get('period_end_date')):0})
            if duplicate_row:
                if not final_data.get((row.get('parent_territory'),row.get('zone') , row.get('territory'))):
                    final_data[(row.get('parent_territory'),row.get('zone'), row.get('territory'))]={}
                final_data[(row.get('parent_territory'),row.get('zone') ,row.get('territory'))].update(duplicate_row)
        final_data[(row.get('parent_territory'),row.get('zone') ,row.get('territory'))].update({'total_gs':gross_sa , 'total_cn':return_cn * (-1), 'total_ns':total_ns , 'total_ach':(total_ns * 100)/row.get('target_amount')  ,'total_cnp':((return_cn * 100)/gross_sa if gross_sa else 0)*(-1) })
        
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
        }
    ]


    if filters.get('base_on') in ['Monthly' , 'Quarterlly']:
        mon_dict = {
        1:'January',2:'February',3:'March',4:'April',5:'May',6:'June',7:'July',8:'August',9:'September',10:'October',11:'November',12:'December'
        }
        from frappe.utils import flt, get_datetime
        for row in period_date_ranges:
            if filters.get('group_by') in ['Sub Division' , 'Division',"Zone"]:
                columns += [
                        {
                        "label": _("{}({})".format(mon_dict.get(get_datetime(row.get('period_start_date')).month) ,'Target')),
                        "fieldname": "{}_{}".format(mon_dict.get(get_datetime(row.get('period_start_date')).month) ,'target'),
                        "fieldtype": "Currency",
                        "options": "currency",
                        "width": 150
                        },
                ]
            columns += [
            
            {
            "label": _("{}({})".format(mon_dict.get(get_datetime(row.get('period_start_date')).month) ,'GS')),
            "fieldname": "{}-to-{}{}".format(row.get('period_start_date') , row.get('period_end_date'),'gross_sales'),
            "fieldtype": "Float",
            "width": 150,
            "precision":2
            },
            {
            "label": _("{}({})".format(mon_dict.get(get_datetime(row.get('period_start_date')).month),'CN')),
            "fieldname": "{}-to-{}{}".format(row.get('period_start_date') , row.get('period_end_date'),'sales_return'),
            "fieldtype": "Float",
            "width": 150,
            "precision":2
            },
            {
            "label": _("{}({})".format(mon_dict.get(get_datetime(row.get('period_start_date')).month),'TCN')),
            "fieldname": "{}-to-{}{}".format(row.get('period_start_date') , row.get('period_end_date'),'sales_return_draft'),
            "fieldtype": "Float",
            "width": 150,
            "precision":2
            },
            {
            "label": _("{}({})".format(mon_dict.get(get_datetime(row.get('period_start_date')).month),'NS')),
            "fieldname": "{}-to-{}{}".format(row.get('period_start_date') , row.get('period_end_date'),'ns'),
            "fieldtype": "Float",
            "width": 150,
            "precision":2
            },
            {
            "label": _("{}({})".format(mon_dict.get(get_datetime(row.get('period_start_date')).month),'ACH%')),
            "fieldname": "{}-to-{}{}".format(row.get('period_start_date') , row.get('period_end_date'),'ach'),
            "fieldtype": "Float",
            "width": 150,
            "precision":2
            },
            {
            "label": _("{}({})".format(mon_dict.get(get_datetime(row.get('period_start_date')).month),'CN%')),
            "fieldname": "{}-to-{}{}".format(row.get('period_start_date') , row.get('period_end_date'),'cnp'),
            "fieldtype": "Float",
            "width": 150,
            "precision":2
            },
        ]


    if filters.get('base_on') == 'Weekly' :
        for row in period_date_ranges:
            columns += [
            {
            "label": _("{}-to-{}{}".format(row.get('period_start_date') , row.get('period_end_date'),'GS')),
            "fieldname": "{}-to-{}{}".format(row.get('period_start_date') , row.get('period_end_date'),'gross_sales'),
            "fieldtype": "Float",
            "width": 200,
            "precision":2
            },
            {
            "label": _("{}-to-{}{}".format(row.get('period_start_date') , row.get('period_end_date'),'CN')),
            "fieldname": "{}-to-{}{}".format(row.get('period_start_date') , row.get('period_end_date'),'sales_return'),
            "fieldtype": "Float",
            "width": 200,
            "precision":2
            },
            {
            "label": _("{}-to-{}{}".format(row.get('period_start_date') , row.get('period_end_date'),'TCN')),
            "fieldname": "{}-to-{}{}".format(row.get('period_start_date') , row.get('period_end_date'),'sales_return_draft'),
            "fieldtype": "Float",
            "width": 200,
            "precision":2
            },
            {
            "label": _("{}-to-{}{}".format(row.get('period_start_date') , row.get('period_end_date'),'NS')),
            "fieldname": "{}-to-{}{}".format(row.get('period_start_date') , row.get('period_end_date'),'ns'),
            "fieldtype": "Float",
            "width": 200,
            "precision":2
            },
            {
            "label": _("{}-to-{}{}".format(row.get('period_start_date') , row.get('period_end_date'),'ACH%')),
            "fieldname": "{}-to-{}{}".format(row.get('period_start_date') , row.get('period_end_date'),'ach'),
            "fieldtype": "Float",
            "width": 200,
            "precision":2
            },
            {
            "label": _("{}-to-{}{}".format(row.get('period_start_date') , row.get('period_end_date'),'CN%')),
            "fieldname": "{}-to-{}{}".format(row.get('period_start_date') , row.get('period_end_date'),'cnp'),
            "fieldtype": "Float",
            "width": 200,
            "precision":2
            },
        ]
    columns += [
        {
            "label": _('Total Gross'),
            "fieldname": 'total_gs',
            "fieldtype": "Float",
            "width": 120,
            "precision":2
        },
        {
            "label": _('Total CN'),
            "fieldname": 'total_cn',
            "fieldtype": "Float",
            "width": 120,
            "precision":2
        },
        {
            "label": _('Total NS'),
            "fieldname": 'total_ns',
            "fieldtype": "Float",
            "width": 120,
            "precision":2
        },
        {
            "label": _('Total ACH'),
            "fieldname": 'total_ach',
            "fieldtype": "Float",
            "width": 120,
            "precision":2
        },
        {
            "label": _('Total CNP'),
            "fieldname": 'total_cnp',
            "fieldtype": "Float",
            "width": 120,
            "precision":2
        },
    ]
    
    

    return list(final_data.values()) , columns

def weeks_between(start_date, end_date):
    from dateutil import rrule
    weeks = rrule.rrule(rrule.WEEKLY, dtstart=start_date, until=end_date)
    return weeks.count()