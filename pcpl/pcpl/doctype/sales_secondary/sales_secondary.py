# Copyright (c) 2022, STPL and contributors
# For license information, please see license.txt

# import frappe

import json

import frappe
from frappe.model.document import Document

class SalesSecondary(Document):
    def validate(self):
        total_amount = 0.0
        for item in self.items:
            total_amount += item.amount
        self.total_amount = total_amount
        if not self.items:
            frappe.throw("Please Add Item Details")

@frappe.whitelist()
def get_price_list_rate_for(item_code,price_list,uom,posting_date):
    if uom == None or not uom:
        frappe.throw("Define Uom in Items {}".format(item_code))
    item_price_args = {
        "item_code": item_code,
        "price_list": price_list,   
        "uom": uom,
        "posting_date": posting_date
    }
    price_list_rate = get_item_price(item_price_args, item_code)
    
    if price_list_rate:
        return price_list_rate[0][1]
    else:
        return 0

@frappe.whitelist()
def get_item_price(args, item_code):
    args["item_code"] = item_code

    conditions = """where item_code=%(item_code)s
        and price_list=%(price_list)s
        and ifnull(uom, '') in ('', %(uom)s)"""

    if args.get("posting_date"):
        conditions += """ and %(posting_date)s between
            ifnull(valid_from, '2000-01-01') and ifnull(valid_upto, '2500-12-31')"""

    return frappe.db.sql(
        """ select name, price_list_rate
        from `tabItem Price` {conditions}
        order by valid_from desc, uom desc """.format(
            conditions=conditions
        ),
        args,
    )

@frappe.whitelist()
def get_mrp_price( item_code, price_list, posting_date):
    conditions = ''
    spl_cond = ''
    if posting_date and price_list:
        conditions += f""" and ip.item_code='{item_code}'
        and '{posting_date}' between ifnull(ip.valid_from, '2000-01-01') and ifnull(ip.valid_upto, '2500-12-31')"""

        spl_cond = f"and spl.price_list = '{price_list}'"

    return frappe.db.sql(
        f""" select ip.name, ip.price_list_rate, spl.price_list
        from `tabItem Price` as ip
        left JOIN `tabSelect Price List` as spl on spl.parent = ip.name {spl_cond}
        where
            ip.price_list='MRP'
        {conditions}
        order by ip.valid_from desc, ip.uom desc """
        , as_dict =1)


@frappe.whitelist()
def get_price_list_mrp_for(item_code,price_list,posting_date):
    item_mrp_args = {
        "item_code": item_code,
        "price_list": price_list,
        "posting_date": posting_date
    }
    price_list_mrp = get_mrp_price(item_code, price_list, posting_date)
    
    if price_list_mrp:
        for row in price_list_mrp:
            if row.price_list and price_list and row.price_list == price_list:
                return row

        return price_list_mrp[0]
    # return price_list_mrp[0][1]

