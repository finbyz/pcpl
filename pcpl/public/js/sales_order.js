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