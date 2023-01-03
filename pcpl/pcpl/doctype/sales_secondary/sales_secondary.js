// cur_frm.fields_dict.executive.get_query = function(doc) {
// 	return {
// 		filters: {
// 			"parent_customer_group": doc.zone
// 		}
// 	}
// };
cur_frm.fields_dict.selling_price_list.get_query = function(doc) {
	return {
		filters: {
			"is_secondary_price_list" : 1
		}
	}
};

cur_frm.fields_dict.secondary_party.get_query = function(doc) {
	return {
		filters: {
			"is_secondary_customer" : 1
		}
	}
};

frappe.ui.form.on('Sales Secondary', {
	onload: function(frm) {
		frm.set_value('posting_date', frappe.datetime.get_today())
	},
	naming_series: function (frm) {
		if (frappe.meta.get_docfield("Sales Secondary", "series_value", frm.doc.name)){
			if (frm.doc.__islocal) {
				frappe.call({
					method: "finbyzerp.api.check_counter_series",
					args: {
						'name': frm.doc.naming_series,
						'company_series': null,
						'date': frm.doc.posting_date,
					},
					callback: function (e) {
						// frm.doc.series_value = e.message;
						
						frm.set_value('series_value', e.message);
					}
				});
				// frm.refresh_field('series_value')
			}
		}
	},
	executive: function(frm){
		frappe.model.get_value("Customer Group",frm.doc.executive,'parent_customer_group',(r)=>{
			if(r.parent_customer_group){
				frm.set_value('zone', r.parent_customer_group)
			}
		})
	},
	secondary_party: function(frm){
		if(!frm.doc.secondary_party){
			frm.set_value('zone', "")
		}
	}
});

frappe.ui.form.on('Sales Secondary Item', {
	
	item_code: function(frm,cdt,cdn){
		var d = locals[cdt][cdn];
		
		if(d.item_code && frm.doc.selling_price_list && frm.doc.secondary_party && frm.doc.posting_date){
			frm.call({
				method: 'pcpl.pcpl.doctype.sales_secondary.sales_secondary.get_price_list_rate_for',
				"args": {
					"item_code": d.item_code,
					"price_list": frm.doc.selling_price_list,
					"customer": frm.doc.secondary_party,
					"uom": d.uom,
					"posting_date":frm.doc.posting_date
				},
				callback: function(r){
					frappe.model.set_value(cdt, cdn, 'rate', r.message);
				}
			});
		}
		frappe.call({
			method: "frappe.client.get_value",
			args: {
				doctype: "Item Price",
				filters: {
					price_list: "MRP",
					item_code: d.item_code
				},
				fieldname: ["price_list_rate"]
			},
			callback: function (r) {
				if (r.message) {
					var item_price = r.message;
					frappe.model.set_value(cdt, cdn, 'mrp', item_price.price_list_rate);
					frm.set_value(cdt, cdn, 'mrp', item_price.price_list_rate)
				}
			}
		});
		
	},
	qty: function (frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn, 'amount', row.qty * row.rate);
	},
	rate: function (frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn, 'amount', row.qty * row.rate);
	}
});