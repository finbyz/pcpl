frappe.query_reports["Finish Below Reorder Level"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company")
		},
		// {
		// 	"fieldname":"warehouse",
		// 	"label": __("Warehouse"),
		// 	"fieldtype": "Link",
		// 	"options": "Warehouse",
		// 	"default": "Finish Goods - PC"
		// },
		{
			"fieldname":"item_code",
			"label": __("Item"),
			"fieldtype": "Link",
			"options": "Item",
			"get_query": function() {
				return {
					query: "erpnext.controllers.queries.item_query"
				}
			}
		}, 
		{
			"fieldname":"parent_item_group",
			"label": __("Parent Item Group"),
			"fieldtype": "Link",
			"options": "Item Group",
			"get_query": function() {
				return {
					"doctype": "Item Group",
					"filters": {
						"old_parent":["in", "10000 Finish goods (F)"],
					}
				}
			}
		},
		{
			"fieldname":"item_group",
			"label": __("Item Group"),
			"fieldtype": "Link",
			"options": "Item Group",
			"get_query": function() {
				return {
					"doctype": "Item Group",
					"filters": {
						"parent_item_group":["in",["10009 Old Finish (F)","10008 Special Pack (F)","10007 TP (F)","10006 Trading (F)","10005 Lozenges (F)","10004 Group D Winter Products (F)","10003 Group C Monsoon Products (F)","10002 Group B Summer Products (F)","10001 Group A All Season (F)"]],
					}
				}
			}
		}
	]
};