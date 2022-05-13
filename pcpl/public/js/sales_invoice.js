cur_frm.fields_dict.income_account.get_query = function(doc) {
	return {
		filters:{
			'parent_account': "Direct Income - PC",
			'company': doc.company
		}
	}
};