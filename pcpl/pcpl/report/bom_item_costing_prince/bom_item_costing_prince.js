// Copyright (c) 2022, STPL and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["BOM Item Costing Prince"] = {
	"filters": [
		{
			"fieldname":"parent_item_group",
			"label":__("Parent Item Group"),
			"options":"Item Group",
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Item Group', txt, {
				});
			}
		},
	],
	"tree": true,
	"name_field": "item_group",
	"parent_field": "parent_item_group",
	"initial_depth": 1,
	"formatter": function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (row[0].indent == 0) {
			value =`<span style='font-weight: bold;'>${value}</span>`;
		}
		return value;
	},
};
