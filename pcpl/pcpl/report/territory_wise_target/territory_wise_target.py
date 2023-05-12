# Copyright (c) 2023, Finbyz Tech. Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt

def execute(filters=None):
	columns, data = [], []
	columns = get_cols(filters)
	data  = get_data(filters)
	return columns, data

def get_cols(filters):
	columns = [
		{
			"fieldname": "territory",
			"label": ("Territory"),
			"fieldtype": "Link",
			"options":"Territory",
			"width": 100
		},
		{
			"fieldname": "parent_territory",
			"label": ("Parent Territory"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "old_parent",
			"label": ("Old Parent Territory"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label":"Target Amount",
			"fieldname":("target_amount"),
			"fieldtype":"Int",
			"width": 100
		},
		{
			"fieldname":"distribution_id",
			"label":("Quater"),
			"fieldtype":"Link",
			"options":"Monthly Distribution",
			"width": 100
		},
		{
			"fieldname":"fiscal_year",
			"label":("Fiscal Year"),
			"fieldtype":"Data",
			"width": 100
		}
		
		
	]
	return columns
def get_data(filters):
	conditions=""
	if filters.get("parent_territory"):
		conditions += f"where te.parent_territory='{filters.get('parent_territory')}'"
	
	
	data = frappe.db.sql(f''' SELECT te.name as territory , te.parent_territory ,te.territory_type, te.old_parent
						From `tabTerritory` as te
						{conditions}
						''',as_dict=1)

	final_data=[]
	for row in data:
		lft,rgt=frappe.db.get_value("Territory",row.get('territory'),['lft','rgt'])
		l1=frappe.db.sql(f"""
						select te.name as territory , te.parent_territory, '{row.old_parent}' as old_parent, td.target_amount as target_amount ,td.fiscal_year, td.distribution_id
						From `tabTerritory` as te
						left join`tabTarget Detail` as td ON te.name = td.parent 
						where td.target_amount > 0 and te.lft >= '{lft}' and te.rgt <= '{rgt}' and td.fiscal_year = '{filters.get("fiscal_year")}'
						""",as_dict=1)
		# print(l1)
		
		for row1 in l1:
			if row1 not in final_data:
				final_data.append(row1)

	# print(l1)

	return final_data