import frappe
from frappe import _

def get_context(context):
    if frappe.session.user == "Guest" or frappe.session.user == "Administrator":
        # For testing, we might want to allow Administrator, 
        # but in production, Guests should be redirected to login.
        if frappe.session.user == "Guest":
            frappe.throw(_("Please login to access the portal"), frappe.PermissionError)

    user = frappe.session.user
    context.user_full_name = frappe.get_value("User", user, "full_name")
    
    # Try to find the Customer linked to this user
    # Logic: User -> Contact (via email) -> Customer (via link)
    customer = None
    contact_name = frappe.get_value("Contact", {"email_id": user}, "name")
    if contact_name:
        customer = frappe.db.get_value("Dynamic Link", 
            {"parent": contact_name, "link_doctype": "Customer"}, "link_name")

    context.customer = customer
    
    # Initialize stats
    context.stats = {
        "orders": 0,
        "invoices": 0,
        "outstanding": 0.0,
        "issues": 0
    }
    
    context.recent_orders = []
    context.recent_invoices = []
    
    if customer:
        # Get Stats
        context.stats["orders"] = frappe.db.count("Sales Order", {"customer": customer})
        context.stats["invoices"] = frappe.db.count("Sales Invoice", {"customer": customer})
        
        # Outstanding amount
        outstanding = frappe.db.get_value("Customer", customer, "outstanding_amount")
        context.stats["outstanding"] = outstanding or 0.0
        
        # Issues
        context.stats["issues"] = frappe.db.count("Issue", {"customer": customer, "status": "Open"})
        
        # Recent Data
        context.recent_orders = frappe.get_all("Sales Order", 
            filters={"customer": customer}, 
            fields=["name", "transaction_date", "grand_total", "status"],
            limit=5, order_by="transaction_date desc")
            
        context.recent_invoices = frappe.get_all("Sales Invoice", 
            filters={"customer": customer}, 
            fields=["name", "posting_date", "grand_total", "status", "outstanding_amount"],
            limit=5, order_by="posting_date desc")

    # Breadcrumbs
    context.parents = [{"name": _("Home"), "route": "/"}]
    context.title = _("Dashboard")
    context.show_sidebar = True
