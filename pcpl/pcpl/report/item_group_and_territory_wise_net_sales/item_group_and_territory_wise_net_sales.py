# Copyright (c) 2023, Finbyz Tech. Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, getdate

def execute(filters):
	data = get_data(filters)
	return data

def get_data(filters):
	columns=[
		{ "label": _("Item Group"),"fieldname": "item_group","fieldtype": "Link", "options" : "Item Group", "width": 300}
	]

	condition = ''
	if filters.get('parent_devision'):
		condition = f"and parent_territory = '{filters.get('parent_devision')}'"

	terr = frappe.db.sql(f"""
			SELECT Distinct name, lft, rgt from `tabTerritory` where is_secondary_=0 and territory_type = '{filters.get('territory_type')}' {condition}
		""", as_dict =1)

	terr_dict = {}
	for row in terr:
		columns.append(
			{ "label": _(f"{row.name} Amount"),"fieldname": f"{row.name}_amount","fieldtype": "Currency", "width": 100,"precision":3})
		columns.append(
			{ "label": _(f"{row.name} Share"),"fieldname": f"{row.name}_share","fieldtype": "Percent","width": 100}
		)
		terr_dict.update({row.name : [row.lft, row.rgt]})

	bet_dates = get_period_date_ranges(filters.get("period"), filters.get("fiscal_year"))

	qtr_dict = {
		"Quarter1" : 0,
		"Quarter2" : 1,
		"Quarter3" : 2,
		"Quarter4" : 3
	}
	if filters.get('period') and filters.get('quarter'):
		between_date = bet_dates[qtr_dict[filters.get('quarter')]]
	elif filters.get('period'):
		between_date = bet_dates[0]

	data = frappe.db.sql(f"""
		SELECT 
			sii.item_group, sii.net_amount as amount, si.territory
		FROM
			`tabSales Invoice` as si
		JOIN 
			`tabSales Invoice Item` as sii on sii.parent = si.name
		WHERE
			si.docstatus = 1 and si.posting_date between '{between_date[0]}' and '{between_date[1]}'
	""", as_dict =1)

	new_data = {}

	total_amount = {}
	for row in data:
		if row.item_group:
			lft, rgt = frappe.db.get_value("Territory", row.territory, ['lft', 'rgt'])
			for ter in terr_dict:
				if flt(lft) >= flt(terr_dict[ter][0]) and flt(rgt) <= flt(terr_dict[ter][1]):
					if total_amount.get(ter):
						total_amount[ter] += row.amount
					else:
						total_amount.update({ter : row.amount})
					if new_data.get(row.item_group):
						if new_data[row.item_group].get(ter):
							new_data[row.item_group][ter][f"{ter}_amount"] += row.amount
						else:
							new_data[row.item_group].update({ter : {'item_group' : row.item_group, f"{ter}_amount" : row.amount}})
					else:
						new_data.update({row.item_group : {ter : {'item_group' : row.item_group, f"{ter}_amount" : row.amount}}})
	final_data = []
	final_dict = {}
	if new_data:
		for row in new_data:
			final_dict.update({row: {}})
			for gr in new_data[row]:
				if flt(new_data[row][gr][f"{gr}_amount"]) > 0:
					new_data[row][gr].update({f"{gr}_share" : (flt(new_data[row][gr][f"{gr}_amount"]) * 100) / flt(total_amount[gr])})
				else:
					new_data[row][gr].update({f"{gr}_share" :0})
				if (flt(new_data[row][gr][f"{gr}_amount"]))!=0 :
					new_data[row][gr].update({f"{gr}_amount" : (flt(new_data[row][gr][f"{gr}_amount"])) / 100000})
				final_dict[row].update(new_data[row][gr])

	for row in final_dict:
		final_data.append(final_dict[row])
	
	return columns, final_data


@frappe.whitelist(allow_guest=True)
def get_period_date_ranges(period, fiscal_year=None, year_start_date=None):
	from dateutil.relativedelta import relativedelta

	if not year_start_date:
		year_start_date, year_end_date = frappe.get_cached_value(
			"Fiscal Year", fiscal_year, ["year_start_date", "year_end_date"]
		)

	increment = {"Monthly": 1, "Quarterly": 3, "Half-Yearly": 6, "Yearly": 12}.get(period)

	period_date_ranges = []
	for i in range(1, 13, increment):
		period_end_date = getdate(year_start_date) + relativedelta(months=increment, days=-1)
		if period_end_date > getdate(year_end_date):
			period_end_date = year_end_date
		period_date_ranges.append([year_start_date, period_end_date])
		year_start_date = period_end_date + relativedelta(days=1)
		if period_end_date == year_end_date:
			break

	return period_date_ranges



	