# Copyright (c) 2023, STPL and contributors
# For license information, please see license.txt

# import frappe


def execute(filters=None):
	columns, data = [], []
	return columns, data


def get_target(filters):
    data = frappe.db.sql(f""" Select  te.name as territory, te.parent_territory , sum(td.target_amount) as target_amount
                            from `tabTerritory` as te
                            left join `tabTarget Detail` as td on td.parent = te.name 
                            Where td.target_amount > 0
                            Group By te.parent_territory 
                            Order By te.parent_territory """, as_dict = True)
	
	p_data = []
	for row in data:
		if row.get("parent_territory"):
			p_data.append(row)

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
        day = list(calendar.monthrange(int(year), month))
        last_day = day[1]

        month_first_date = '{}-{}-1'.format(year , mon_dict.get(filters.get('month')) )
        month_last_date = '{}-{}-{}'.format(year , mon_dict.get(filters.get('month')) , last_day)
        
        from datetime import datetime

        month_first_date = datetime.strptime(month_first_date, '%Y-%m-%d').date()
        month_last_date = datetime.strptime(month_last_date, '%Y-%m-%d').date()
        
        total_week = weeks_between( month_first_date ,month_last_date )
    territory_data = prepare_tarretory_data(filters)
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
    
    if filters.get('base_on') == 'Monthly':
        for row in range(12):
            mon_dic = {}
            import calendar
            day = list(calendar.monthrange(int(year), row + 1))
            last_day = day[1]
            month_first_date = '{}-{}-1'.format(year , row + 1 )
            month_last_date = '{}-{}-{}'.format(year , row + 1 , last_day)
            period_date_ranges.append({'period_start_date':month_first_date , 'period_end_date':month_last_date})

    final_data = {}

	for row in p_data:
        
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
            
