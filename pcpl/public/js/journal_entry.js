cur_frm.fields_dict.accounts.grid.get_field("party").get_query = function(doc,cdt,cdn) {
	let d = locals[cdt][cdn];
	 if (d.party_type == "Employee"){
        return {
            filters: {
                "status" : "Active"
            }
        }
	 }
};