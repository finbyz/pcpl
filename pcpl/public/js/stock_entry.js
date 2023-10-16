frappe.ui.form.on("Stock Entry", {
    refresh(frm){
        frm.fields_dict.bom_no.get_query = function(frm){
            return{
                filters: {
                    "docstatus" : 1,
                    "is_default": 1
                }
            }
        }
    }
})
