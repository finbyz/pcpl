import frappe
from erpnext.controllers.queries import get_fields, get_filters_cond, get_match_cond
import json
import re
from typing import TypedDict

from typing_extensions import NotRequired  # not required in 3.11+
from frappe.desk.search import LinkSearchResults, build_for_autosuggest


# Backward compatbility
from frappe import _, is_whitelisted
from frappe.database.schema import SPECIAL_CHAR_PATTERN
from frappe.model.db_query import get_order_by
from frappe.permissions import has_permission
from frappe.utils import cint, cstr, unique
from frappe.utils.data import make_filter_tuple

def sanitize_searchfield(searchfield: str):
    if not searchfield:
        return

    if SPECIAL_CHAR_PATTERN.search(searchfield):
        frappe.throw(_("Invalid Search Field {0}").format(searchfield), frappe.DataError)

def relevance_sorter(key, query, as_dict):
    value = _(key.name if as_dict else key[0])
    return (cstr(value).casefold().startswith(query.casefold()) is not True, value)

def get_std_fields_list(meta, key):
    # get additional search fields
    sflist = ["name"]

    if meta.title_field and meta.title_field not in sflist:
        sflist.append(meta.title_field)

    if key not in sflist:
        sflist.append(key)

    if meta.search_fields:
        for d in meta.search_fields.split(","):
            if d.strip() not in sflist:
                sflist.append(d.strip())

    return sflist

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_delivery_notes_to_be_billed(doctype, txt, searchfield, start, page_len, filters, as_dict):
    fields = get_fields("Delivery Note", ["name", "customer", "posting_date"])

    return frappe.db.sql(
        """
        select %(fields)s
        from `tabDelivery Note`
        where `tabDelivery Note`.`%(key)s` like %(txt)s and
            `tabDelivery Note`.docstatus = 1
            and status not in ("Stopped", "Closed") %(fcond)s
            and (
                (`tabDelivery Note`.is_return = 0)
                or (`tabDelivery Note`.grand_total = 0)
                or (
                    `tabDelivery Note`.is_return = 1
                    and return_against in (select name from `tabDelivery Note`)
                )
            )
            %(mcond)s order by `tabDelivery Note`.`%(key)s` asc limit %(start)s, %(page_len)s
    """
        % {
            "fields": ", ".join(["`tabDelivery Note`.{0}".format(f) for f in fields]),
            "key": searchfield,
            "fcond": get_filters_cond(doctype, filters, []),
            "mcond": get_match_cond(doctype),
            "start": start,
            "page_len": page_len,
            "txt": "%(txt)s",
        },
        {"txt": ("%%%s%%" % txt)},
        as_dict=as_dict,
    )

@frappe.whitelist()
def get_sales_tax_template(tax_category, company):
    return frappe.db.get_value("Sales Taxes and Charges Template", {'tax_category' : tax_category, 'company': company, 'disabled': 0}, 'name')

def set_sales_taxes_and_charges(self, method):
    if self.tax_category and not self.taxes_and_charges:
        self.taxes_and_charges = get_sales_tax_template(self.tax_category, self.company)

def check_user_limit(self , method):
    # if self.user_type == 'Employee Self Service':
    # 	count_user = frappe.db.sql(""" Select count(name) as user From `tabUser` Where user_type = "Employee Self Service" and enabled = 1 """,as_dict = 1)
    # 	if count_user[0].get('user') > 14:
    # 		frappe.throw("Your User Limit of Employee Self Service Is 14 <br>You can Disable Or Enable Other User Or Purchase New User<br>Contact Your Service Provider")
    # if self.user_type == "System User":
    count_user = frappe.db.sql(""" Select count(name) as user From `tabUser` Where  enabled = 1 """,as_dict = 1)
    if count_user[0].get('user') > 45:
        # frappe.throw(str(count_user[0].get('user') + 1))
        frappe.throw("Your User Limit of System User Is 45 <br>You can Disable Or Enable Other User Or Purchase New User<br>Contact Your Service Provider")

from frappe.utils import flt

def update_discounted_price(self, method):
    for item in self.items:
        effective_item_rate = item.price_list_rate
        item_rate = item.rate
        if item.margin_type == "Percentage":
            item.rate_with_margin = flt(effective_item_rate) + flt(effective_item_rate) * ( flt(item.margin_rate_or_amount) / 100)
        else:
            item.rate_with_margin = flt(effective_item_rate) + flt(item.margin_rate_or_amount)
        
        item.base_rate_with_margin = flt(item.rate_with_margin) * flt(self.conversion_rate)

        item_rate = flt(item.rate_with_margin , 4)

        if item.discount_percentage:
            item.discount_amount = flt(item.rate_with_margin) * flt(item.discount_percentage) / 100

        if item.discount_amount:
            item_rate = flt((item.rate_with_margin) - (item.discount_amount), 4)
            item.discount_percentage = 100 * flt(item.discount_amount) / flt(item.rate_with_margin)

        item.rate = item_rate

@frappe.whitelist()
def search_link(
	doctype: str,
	txt: str,
	query: str | None = None,
	filters: str | dict | list | None = None,
	page_length: int = 10,
	searchfield: str | None = None,
	reference_doctype: str | None = None,
	ignore_user_permissions: bool = False,
) -> list[LinkSearchResults]:
	results = search_widget(
		doctype,
		txt.strip(),
		query,
		searchfield=searchfield,
		page_length=page_length,
		filters=filters,
		reference_doctype=reference_doctype,
		ignore_user_permissions=ignore_user_permissions,
	)
	return build_for_autosuggest(results, doctype=doctype)

@frappe.whitelist()
def search_widget(
    doctype: str,
    txt: str,
    query: str | None = None,
    searchfield: str | None = None,
    start: int = 0,
    page_length: int = 10,
    filters: str | None | dict | list = None,
    filter_fields=None,
    as_dict: bool = False,
    reference_doctype: str | None = None,
    ignore_user_permissions: bool = False,
):
    start = cint(start)
    if isinstance(filters, str):
        filters = json.loads(filters)


    if searchfield:
        sanitize_searchfield(searchfield)

    if not searchfield:
        searchfield = "name"

    standard_queries = frappe.get_hooks().standard_queries or {}

    if not query and doctype in standard_queries:
        query = standard_queries[doctype][-1]

    if query:  # Query = custom search query i.e. python function
        try:
            is_whitelisted(frappe.get_attr(query))
            return frappe.call(
                query,
                doctype,
                txt,
                searchfield,
                start,
                page_length,
                filters,
                as_dict=as_dict,
                reference_doctype=reference_doctype,
            )
        except (frappe.PermissionError, frappe.AppNotInstalledError, ImportError):
            if frappe.local.conf.developer_mode:
                raise
            else:
                frappe.respond_as_web_page(
                    title="Invalid Method",
                    html="Method not found",
                    indicator_color="red",
                    http_status_code=404,
                )
                return []

    meta = frappe.get_meta(doctype)

    if isinstance(filters, dict):
        filters_items = filters.items()
        filters = []
        for key, value in filters_items:
            filters.append(make_filter_tuple(doctype, key, value))

    if filters is None:
        filters = []
    or_filters = []

    # build from doctype
    if txt:
        field_types = {
            "Data",
            "Text",
            "Small Text",
            "Long Text",
            "Link",
            "Select",
            "Read Only",
            "Text Editor",
        }
        search_fields = ["name"]
        if meta.title_field:
            search_fields.append(meta.title_field)

        if meta.search_fields:
            search_fields.extend(meta.get_search_fields())

        for f in search_fields:
            fmeta = meta.get_field(f.strip())
            if not meta.translated_doctype and (f == "name" or (fmeta and fmeta.fieldtype in field_types)):
                or_filters.append([doctype, f.strip(), "like", f"%{txt}%"])

    if meta.get("fields", {"fieldname": "enabled", "fieldtype": "Check"}):
        filters.append([doctype, "enabled", "=", 1])
    if meta.get("fields", {"fieldname": "disabled", "fieldtype": "Check"}):
        filters.append([doctype, "disabled", "!=", 1])

    # format a list of fields combining search fields and filter fields
    fields = get_std_fields_list(meta, searchfield or "name")
    if filter_fields:
        fields = list(set(fields + json.loads(filter_fields)))
    formatted_fields = [f"`tab{meta.name}`.`{f.strip()}`" for f in fields]

    # Insert title field query after name
    if meta.show_title_field_in_link:
        formatted_fields.insert(1, f"`tab{meta.name}`.{meta.title_field} as `label`")

    order_by_based_on_meta = get_order_by(doctype, meta)
    # `idx` is number of times a document is referred, check link_count.py
    order_by = f"`tab{doctype}`.idx desc, {order_by_based_on_meta}"

    if not meta.translated_doctype:
        _txt = frappe.db.escape((txt or "").replace("%", "").replace("@", "").replace("(", "").replace(")", ""))
        # locate returns 0 if string is not found, convert 0 to null and then sort null to end in order by
        _relevance = f"(1 / nullif(locate({_txt}, `tab{doctype}`.`name`), 0))"
        formatted_fields.append(f"""{_relevance} as `_relevance`""")
        # Since we are sorting by alias postgres needs to know number of column we are sorting
        if frappe.db.db_type == "mariadb":
            order_by = f"ifnull(_relevance, -9999) desc, {order_by}"
        elif frappe.db.db_type == "postgres":
            # Since we are sorting by alias postgres needs to know number of column we are sorting
            order_by = f"{len(formatted_fields)} desc nulls last, {order_by}"

    ignore_permissions = doctype == "DocType" or (
        cint(ignore_user_permissions)
        and has_permission(
            doctype,
            ptype="select" if frappe.only_has_select_perm(doctype) else "read",
            parent_doctype=reference_doctype,
        )
    )

    values = frappe.get_list(
        doctype,
        filters=filters,
        fields=formatted_fields,
        or_filters=or_filters,
        limit_start=start,
        limit_page_length=None if meta.translated_doctype else page_length,
        order_by=order_by,
        ignore_permissions=ignore_permissions,
        reference_doctype=reference_doctype,
        as_list=not as_dict,
        strict=False,
    )
    if meta.translated_doctype:
        # Filtering the values array so that query is included in very element
        values = (
            result
            for result in values
            if any(
                re.search(f"{re.escape(txt)}.*", _(cstr(value)) or "", re.IGNORECASE)
                for value in (result.values() if as_dict else result)
            )
        )

    # Sorting the values array so that relevant results always come first
    # This will first bring elements on top in which query is a prefix of element
    # Then it will bring the rest of the elements and sort them in lexicographical order
    values = sorted(values, key=lambda x: relevance_sorter(x, txt, as_dict))

    # remove _relevance from results
    if not meta.translated_doctype:
        if as_dict:
            for r in values:
                r.pop("_relevance", None)
        else:
            values = [r[:-1] for r in values]

    return values