frappe.ui.form.on("Sales Order", {
    naming_series: function(frm){
        frm.set_query("customer", function() {
			return {
				filters : {
                    "is_secondary_customer": 0
                }
            }
        })
    },
	tax_category:function(frm){
		if(frm.doc.tax_category && !frm.doc.taxes_and_charges){
			frappe.call({
				method: "pcpl.api.get_sales_tax_template",
				args: {
					"tax_category": frm.doc.tax_category,
					"company": frm.doc.company
				},
				callback: function(r) {
					frm.set_value("taxes_and_charges", r.message)
				}
			});
		}
	},
	before_save: function(frm){
		frm.doc.items.forEach((item) => {
            frappe.model.set_value(item.doctype, item.name, "discount_percentage", frm.doc.discount);
			let effective_item_rate = item.price_list_rate;
			let item_rate = item.rate;
			if (in_list(["Sales Order", "Quotation"], item.parenttype) && item.blanket_order_rate) {
				effective_item_rate = item.blanket_order_rate;
			}
			if (item.margin_type == "Percentage") {
				item.rate_with_margin = flt(effective_item_rate)
					+ flt(effective_item_rate) * ( flt(item.margin_rate_or_amount) / 100);
			} else {
				item.rate_with_margin = flt(effective_item_rate) + flt(item.margin_rate_or_amount);
			}
			item.base_rate_with_margin = flt(item.rate_with_margin) * flt(frm.doc.conversion_rate);

			item_rate = flt(item.rate_with_margin , precision("rate", item));

			if (item.discount_percentage) {
				item.discount_amount = flt(item.rate_with_margin) * flt(item.discount_percentage) / 100;
			}

			if (item.discount_amount) {
				item_rate = flt((item.rate_with_margin) - (item.discount_amount), precision('rate', item));
				item.discount_percentage = 100 * flt(item.discount_amount) / flt(item.rate_with_margin);
			}

			frappe.model.set_value(item.doctype, item.name, "rate", item_rate);
        });
	},
	discount:function(frm){
        frm.doc.items.forEach((d) => {
            frappe.model.set_value(d.doctype, d.name, "discount_percentage", frm.doc.discount)
        });
        
    },
});
cur_frm.fields_dict.contact_person_2.get_query = function(doc) {
	return {
		filters: {
			"link_doctype":"Customer",
			"link_name":doc.customer
		}
	}
};


// cur_frm.fields_dict.customer.get_query = function(doc) {
// 	return {
// 		filters: {
// 			"is_secondary_customer": 0
// 		}
// 	}
// };
// cur_frm.set_query('customer', function() {
// 	return {
// 		filters: {
// 			"is_secondary_customer" : 0
// 		}
// 	};
// });
// frappe.ui.form.on("Sales Order", "refresh", function(frm) {
//     cur_frm.set_query("customer", function() {
//         return {
//             "filters": {
//                 "is_secondary_customer": 0
//             }
//         };
//     });
// });