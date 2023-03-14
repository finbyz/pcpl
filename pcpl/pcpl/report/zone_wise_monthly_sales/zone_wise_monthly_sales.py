# Copyright (c) 2023, STPL and contributors
# For license information, please see license.txt

# import frappe

def execute(filters={"month":"February" , "year":'2022-2023'  , "base_on":"Weekly" , "group_by":"Zone"}):
    columns, data = [], []
    data,columns  = gross_sales_data(filters )
    return columns, data

def get_target(filters):
    data = frappe.db.sql(f""" Select   te.name , td.target_amount
                            from `tabTerritory` as te
                            left join `tabTarget Detail` as td on td.parent = te.name 
                            Where (te.name Like '%Zone%' OR te.name Like '%zone%')
                           """, as_dict = True)