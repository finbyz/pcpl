# Copyright (c) 2022, STPL and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt


def execute(filters=None):
	columns,data = get_columns(filters),get_data(filters)
	return columns, data

def get_columns(filters):
	return [
		{"label": ("BOM"), "fieldname": "bom", "fieldtype": "Link", "options": "BOM", "width": 200},
		{"label": ("Parent Item Group"), "fieldname": "parent_item_group", "fieldtype": "Link", "options": "Item Group", "width": 200},
		{"label": ("Finish Item Name"), "fieldname": "finish_item_name", "fieldtype": "Data", "width": 200},
		{"label": ("BOM Item"), "fieldname": "bom_item", "fieldtype": "Link", "options": "Item", "width": 200},
		{"label": ("Total Valuation AMT Per PCS"), "fieldname": "Value_per_pcs", "fieldtype": "Currency", "width": 200},
		{"label": ("UOM"), "fieldname": "uom", "fieldtype": "Data", "width": 200},
		{"label": ("Valuation Rate"), "fieldname": "valuation_rate", "fieldtype": "Currency", "width": 200},
		{"label": ("Last Purchase Rate"), "fieldname": "last_purchase_rate", "fieldtype": "Currency", "width": 200},
		{"label": ("Quantity"), "fieldname": "quantity", "fieldtype": "Float", "width": 200},
	]


def get_data(filters):
	conditions=""
	if filters.get("parent_item_group"):
		conditions=" and "
		range_cond=""
		parent_item_group=frappe.db.get_all("Item Group",{'name':['in',filters.get("parent_item_group")]},['lft','rgt'])
		for each in parent_item_group:
			if range_cond:
				range_cond+=" or "
			range_cond+= f" (`tabItem Group`.`lft` >= {each.lft} and `tabItem Group`.`rgt` <= {each.rgt} ) "
		conditions+=range_cond

	
	data_map={}

	data = frappe.db.sql(f"""
	Select

		`tabBOM`.`name` as bom,

		bmi.`parent_item_group` as parent_item_group,


		`tabBOM`.`item_name` as finish_item_name,

		`tabBOM Item`.`item_code` as bom_item,
		
		`tabBOM Item`.`uom` as uom,

		bti.`valuation_rate` as valuation_rate,
		
		bti.`last_purchase_rate` as last_purchase_rate,

		`tabBOM Item`.`qty` as quantity,
		
		(bti.`valuation_rate` * `tabBOM Item`.`qty` / `tabBOM`.`quantity`) as Value_per_pcs
		
	From

		`tabItem` as bmi, `tabBOM`, `tabBOM Item`, `tabItem` as bti,`tabItem Group`

	Where

		`tabBOM Item`.`parent` = `tabBOM`.`name` 

		and `tabBOM`.`item` = bmi.item_code
		and  bmi.`parent_item_group` = `tabItem Group`.name

		and `tabBOM Item`.`item_code` = bti.item_code

		and `tabBOM`.docstatus < 2

		and `tabBOM`.is_default = 1 {conditions}

	order by 
		`tabBOM`.`name` desc""",as_dict=1)

	for each in data:
		if not data_map.get(each.bom):
			data_map[each.bom]={"total":0.0,"items":[],"parent_item_group":"","finish_item_name":""}

		data_map[each.bom]["items"].append(each)
		data_map[each.bom]["total"]+=flt(each.Value_per_pcs)
		data_map[each.bom]["parent_item_group"]=str(each.parent_item_group)
		data_map[each.bom]["finish_item_name"]=str(each.finish_item_name)

	final_data=[]
	for key in data_map.keys():
		final_data.append({"bom":key,"Value_per_pcs":data_map[key]["total"],'indent':0,"finish_item_name":data_map[key]["finish_item_name"],"parent_item_group":data_map[key]["parent_item_group"]})
		for each in data_map[key]["items"]:
			each.update({'indent':1})
			final_data.append(each)
	
	return final_data