frappe.ui.form.on("Purchase Order", {
    refresh: function(frm){
        frm.set_query("project", function() {
			return {
				filters : {
                    "company": frm.doc.company,
					"is_active": "Yes"
                }
            }
        })
    }
});