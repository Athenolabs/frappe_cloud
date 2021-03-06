# -*- coding: utf-8 -*-
# Copyright (c) 2017, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import throw, _
from frappe.model.document import Document

class CloudEmployee(Document):
	pass


@frappe.whitelist()
def add_employee(user, company):
	comp = frappe.get_value("Cloud Employee", {"user": user}, "company")
	if comp:
		if comp != company:
			throw(_("User in in another company {0}").format(comp))
		return True

	if not frappe.get_value("Cloud Company", {"name": company, "admin": frappe.session.user}):
		throw(_("You not the admin of company {0}").format(company))

	doc = frappe.get_doc({
		"doctype": "Cloud Employee",
		"user": user,
		"company": company
	})
	doc.insert(ignore_permissions=True)
	frappe.db.commit()

	return _("Employee has ben added")


@frappe.whitelist()
def delete_employee(user, company):
	if not frappe.get_value("Cloud Company", {"name": company, "admin": frappe.session.user}):
		throw(_("You not the admin of company {0}").format(company))

	frappe.delete_doc("Cloud Employee", user, ignore_permissions=True)

	return _("Employee has been deleted")


def query_employee(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql("""select distinct employee.name, concat_ws(' ', user.first_name, user.middle_name, user.last_name) 
		from `tabCloud Employee` employee, `tabUser` user 
		where employee.company = %s and employee.name = user.name
		and employee.%s like %s order by employee.name limit %s, %s""" %
		("%s", searchfield, "%s", "%s", "%s"),
		(filters["company"], "%%%s%%" % txt, start, page_len), as_list=1)