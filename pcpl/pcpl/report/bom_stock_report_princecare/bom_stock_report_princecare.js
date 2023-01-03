// Copyright (c) 2022, STPL and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["BOM Stock Report Princecare"] = {
	"filters": [
		{
			"fieldname":"name",
			"lable":__("BOM"),
			"fieldtype":"Link",
			"options":"BOM",
			"reqd": 1,
			"get_query": () =>{
				return {
					filters: { "is_active": 1 , "is_default":1}
				}
			}
		},
		{
			"fieldname":"qty_to_produce",
			"lable":__("Qty to Produce"),
			"fieldtype":"Float",
			"reqd": 1
		}
	],
	"formatter": function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (column.fieldname == "Short Qty" && data && data['Short Qty'] > 0) {
			value =`<span style='color:green; font-weight: bold;'>${value}</span>`;
		}
		else if (in_list(["Short Qty", "Item Code"],column.fieldname) && data && data['Short Qty'] < 0) {
			value =`<style>span>a{color : red;}</style><span style='color:red; font-weight: bold;'>${value}</span>`;
		}
		return value;
	},
};