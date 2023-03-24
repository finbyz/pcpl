# Copyright (c) 2023, STPL and contributors
# For license information, please see license.txt
import frappe
import itertools
from dateutil.relativedelta import relativedelta
from frappe import _
from frappe.utils import getdate
from datetime import datetime


def execute(filters = {'year':'2022-2023' , 'base_on':'Monthly' , 'group_by':'Zone'}):
    columns, data = [], []
    data , columns = get_final_data(filters)
    return columns, data


def get_last_terretory_data(filters):

    data = frappe.db.sql(f''' SELECT te.name as territory , td.target_amount , te.parent_territory , mdp.percentage_allocation , mdp.month, (td.target_amount * mdp.percentage_allocation)/100 as monthly_target
                            From `tabTerritory` as te
                            left join `tabTarget Detail` as td ON td.parent = te.name
                            left join `tabMonthly Distribution Percentage` as mdp ON td.distribution_id = mdp.parent
                            where td.target_amount > 0
                             Order by
case
when mdp.month ='April' then 13
when mdp.month ='May' then 14
when mdp.month ='June' then 15
when mdp.month ='July' then 16
when mdp.month ='August' then 17
when mdp.month ='September' then 18
when mdp.month ='October' then 19
when mdp.month ='November' then 20
when mdp.month ='December' then 21
when mdp.month ='January' then 22
when mdp.month ='February' then 23
when mdp.month ='March' then 24
else
  mdp.month
end''',as_dict=1)
    total_monthly_target=0
    month_list_=[]
    # for d in data:
    #     if d.month not in month_list_:
    #         month_list_.append(d.month)
          
    #         total_monthly_target+=d.monthly_target
         
    #     d.update({'{}_target'.format(d.month):total_monthly_target})
    temp=[]
    temp_1=[]
    mo={}
    for d in data:
        if d.territory in mo.keys():
            if d.month not in mo[d.territory][0]:
                mo[d.territory].append([d.month,d.monthly_target])
               
        else:
            mo[d.territory]=[[d.month,d.monthly_target]]
            total_monthly_target=0
  
    
    for row in data:
        total_monthly_target=0
        for i in mo[row.territory]:
            total_monthly_target+=i[1]
            row.update({'{}_target'.format(i[0]):total_monthly_target})

            
        


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
                                          Order by
case
when mdp.month ='April' then 13
when mdp.month ='May' then 14
when mdp.month ='June' then 15
when mdp.month ='July' then 16
when mdp.month ='August' then 17
when mdp.month ='September' then 18
when mdp.month ='October' then 19
when mdp.month ='November' then 20
when mdp.month ='December' then 21
when mdp.month ='January' then 22
when mdp.month ='February' then 23
when mdp.month ='March' then 24
else
  mdp.month
end """,as_dict =1 )
            month_target=0
            for d in div_target:
                if d.get('percentage_allocation') and d.get('target_amount'):
                    if not month_div.get(d.parent_territory):
                        month_div[d.parent_territory] = {}
                   
                    month_target=month_target+((d.target_amount * d.percentage_allocation)/100)
                        
                    month_div.get(d.parent_territory).update({'{}_{}'.format(d.month , 'target'):month_target})
                   
                
        for row in data:
            if month_div.get(row.territory):
                row.update(month_div.get(row.territory))
    
    if filters.get('group_by') == 'Zone':
        zone_target=0
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
                                            Order by
case
when mdp.month ='April' then 13
when mdp.month ='May' then 14
when mdp.month ='June' then 15
when mdp.month ='July' then 16
when mdp.month ='August' then 17
when mdp.month ='September' then 18
when mdp.month ='October' then 19
when mdp.month ='November' then 20
when mdp.month ='December' then 21
when mdp.month ='January' then 22
when mdp.month ='February' then 23
when mdp.month ='March' then 24
else
  mdp.month
end
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
        zon_tar=0
        terr_month_list=[]
        terr_list=[]
        for row in div_target:
            if row.territory not in terr_map_month:
                terri_list.append(row.territory)
                terr_map_month[row.territory] = {}
            if total.get((row.territory,row.month)):
                if [row.territory,row.month] not in terr_month_list:
                    if row.territory not in terr_list: 
                        zon_tar=0
                        terr_list.append(row.territory)
                    terr_month_list.append( [row.territory,row.month])
                    zon_tar+=((total.get((row.territory,row.month)).get('target_amount') * total.get((row.territory,row.month)).get('percentage_allocation'))/100)
                    terr_map_month.get(row.territory).update({'{}_{}'.format(row.month,'target'):zon_tar})
        for row in data:
            if terr_map_month.get(row.get('territory')):
                row.update(terr_map_month.get(row.get('territory')))


    return data
    

def get_period_date_ranges(filters):
    mon_dict = {
        'January':1,'February':2,'March':3,'April':4,'May':5,'June':6,'July':7,'August':8,'September':9,'Octomber':10,'November':11,'December':12
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
            print(j)
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
            
         

            duplicate_row.update(row)
      
            sales_return_total = sum(d.get('qty') * d.get('rate') for d in sales_return) if sales_return else 0
            sum_gross_sales  = sum(d.get('qty') * d.get('rate') for d in gross_sales) if gross_sales else 0
            NS = (sum_gross_sales)+(sales_return_total)
            total_ns += NS
            duplicate_row.update({'{}-to-{}ns'.format(d.get('period_start_date') , d.get('period_end_date')):total_ns})
            mon_dict = {1:'January',2:'February',3:'March',4:'April',5:'May',6:'June',7:'July',8:'August',9:'September',10:'Octomber',11:'November',12:'December'}
            from frappe.utils import flt, get_datetime
            # ach = (NS / row.get('target_amount')) if row.get('target_amount') else 0
            t='{}_target'.format(mon_dict.get(get_datetime(d.get('period_start_date')).month))
            ach = (total_ns/row.get(t)) if row.get(t) else 0
            # total_ach += ach
            duplicate_row.update({'{}-to-{}ach'.format(d.get('period_start_date') , d.get('period_end_date')):ach})
          
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
        },
        
    ]

    if filters.get('base_on') == 'Monthly':
        mon_dict = {
        1:'January',2:'February',3:'March',4:'April',5:'May',6:'June',7:'July',8:'August',9:'September',10:'Octomber',11:'November',12:'December'
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
          
        ]
    

    return list(final_data.values()) , columns

def weeks_between(start_date, end_date):
    from dateutil import rrule
    weeks = rrule.rrule(rrule.WEEKLY, dtstart=start_date, until=end_date)
    return weeks.count()