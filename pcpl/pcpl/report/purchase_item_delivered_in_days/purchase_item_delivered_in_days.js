// Copyright (c) 2022, STPL and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Purchase Item Delivered in Days"] = {
	"filters": [
		{
			"fieldname":"purchase_order",
			"label": __("Purchase Order"),
			"fieldtype": "Link",
			"options": "Purchase Order"
		},
		{
			"fieldname":"purchase_receipt",
			"label": __("Purchase Receipt"),
			"fieldtype": "Link",
			"options": "Purchase Receipt"
		},
	]
};
