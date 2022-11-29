# Copyright (c) 2022, STPL and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns, data = [], []

	columns = get_columns(filters)
	data = get_data(columns, filters)

	return columns, data

def get_columns(filters):
	return [
		{"label": _("Item Code"), "fieldname": "Item Code", "fieldtype": "Link", "options": "Item", "width": 200},
		{"label": _("Description"), "fieldname": "Description", "fieldtype": "Data", "width": 300},
		{"label": _("BOM Qty"), "fieldname": "BOM Qty", "fieldtype": "Float", "width": 100},
		{"label": _("UOM"), "fieldname": "UOM", "fieldtype": "Data", "width": 50},
		{"label": _("Required Qty"), "fieldname": "Required", "fieldtype": "Float", "width": 100},
		{"label": _("In Stock Qty"), "fieldname": "In Stock Qty", "fieldtype": "Float", "width": 100},
		{"label": _("Short Qty"), "fieldname": "Short Qty", "fieldtype": "Float", "width": 120}
	]
def get_data(columns, filters):

	qty_to_produce = 0
	name = ''
	if filters.get('qty_to_produce'):
		qty_to_produce = filters.get('qty_to_produce')
	if filters.get('name'):
		name = filters.get('name')
	
	return frappe.db.sql(f"""
		SELECT
			bom_item.item_code as 'Item Code',
			bom_item.description as 'Description',
			bom_item.stock_qty as 'BOM Qty',
			bom_item.uom as 'UOM',
			(bom_item.stock_qty * {qty_to_produce} / bom.quantity) as Required,
			ifnull(sum(ledger.actual_qty), 0) as 'In Stock Qty',
			ifnull(sum(ledger.actual_qty), 0) - (
				bom_item.stock_qty * {qty_to_produce} / bom.quantity
			) as 'Short Qty'
		FROM
			`tabBOM` AS bom
			INNER JOIN `tabBOM Item` AS bom_item ON bom.name = bom_item.parent
			LEFT JOIN `tabBin` AS ledger ON bom_item.item_code = ledger.item_code
		WHERE
			bom_item.parenttype = 'BOM'
			and bom.name = '{name}'
			and bom.docstatus < 2
			and bom.is_default = 1
		GROUP BY
			bom_item.item_code
	""", as_dict = 1)
	