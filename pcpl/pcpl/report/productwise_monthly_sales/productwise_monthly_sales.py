# Copyright (c) 2023, Finbyz Tech. Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, getdate, get_datetime


def execute(filters={'fiscal_year':'2022-2023','territory_type':'Zone','territory':'A Zone'}):
	data = get_data(filters)
	return data

def get_data(filters):
	columns=[
		{ "label": _("Item Group"),"fieldname": "item_group","fieldtype": "Link", "options" : "Item Group", "width": 350}
	]
	mon_dict = {1:'January',2:'February',3:'March',4:'April',5:'May',6:'June',7:'July',8:'August',9:'September',10:'October',11:'November',12:'December'}
	bet_dates = get_period_date_ranges("Monthly", filters.get("fiscal_year"))
	for i in range(len(bet_dates)):
		columns.append(
			{ "label": _(f"{mon_dict.get(get_datetime(bet_dates[i][0]).month) }"),"fieldname": f"{bet_dates[i][0]}","fieldtype": "Currency", "width": 100})
	columns+=[
		{ "label": _("Total"),"fieldname": "total","fieldtype": "Currency", "width": 110}]
	lft,rgt = frappe.db.get_value("Item Group",'10000 Finish goods (F)',['lft','rgt'])
	lft_allopathic,rgt_allopathic = frappe.db.get_value("Item Group",'1604 Allopathic  (F) Prolific',['lft','rgt'])
	item_group_list = frappe.db.get_all('Item Group',{'lft': ['>=',lft],'rgt':['<=',rgt]},pluck="name")
	allopathic_item_group_list = frappe.db.get_all('Item Group',{'lft': ['>=',lft_allopathic],'rgt':['<=',rgt_allopathic]},pluck="name")
	item_group_list+=allopathic_item_group_list # add allopatthics list becuase of add those item_group that parent is '1604 Allopathic  (F) Prolific'
	conditions = ''
	conditions += " and sii.item_group in {} ".format(
		"(" + ", ".join([f'"{l}"' for l in item_group_list]) + ")")
	con = ""
	if filters.get('territory'):
		terr_lft,terr_rgt=frappe.db.get_value("Territory",filters.get('territory'),['lft','rgt'])
		terr_list = frappe.db.get_all('Territory',{'lft': ['>=',terr_lft],'rgt':['<=',terr_rgt]})
		con += " and si.territory in {} ".format(
			"(" + ", ".join([f'"{l.name}"' for l in terr_list]) + ")")

	final_data = {}
	for i in range(len(bet_dates)):
		between_date = bet_dates[i]
		print(str(between_date[0]))
		data = frappe.db.sql(f"""
			SELECT 
				sii.item_group, sum(sii.qty * sii.price_list_rate) as '{between_date[0]}'
			FROM
				`tabSales Invoice` as si
			JOIN 
				`tabSales Invoice Item` as sii on sii.parent = si.name
			WHERE
				si.docstatus = 1  and si.is_return = 0 {conditions}{con} and si.posting_date between '{between_date[0]}' and '{between_date[1]}'
			Group By
				sii.item_group
		""", as_dict =1)
		for row in data:
			if not final_data.get(row.get('item_group')):
				final_data[row.get('item_group')]={}
			final_data[row.get('item_group')].update(row)

			if not final_data.get(row.get('item_group')).get('total'):
				final_data.get(row.get('item_group')).update({'total':0})
			final_data.get(row.get("item_group")).update({"total":row.get(str(between_date[0])) + final_data.get(row.get('item_group')).get('total') })
	return columns, list(final_data.values())


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



	