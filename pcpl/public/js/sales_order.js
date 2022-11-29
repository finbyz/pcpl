frappe.ui.form.on("Sales Order", {
    naming_series: function(frm){
        frm.set_query("customer", function() {
			return {
				filters : {
                    "is_secondary_customer": 0
                }
            }
        })
    }
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