"""Demo HR records for the Afintrix theme.

Phase 2 restyles the HR screens, and a screen with no rows cannot be judged. This
seeds a small, believable set of employees, attendance, leave, payroll and
recruitment records on the demo company so those screens can be reviewed.

It is demo data, not fixtures: nothing in the theme depends on it, and it is safe
to delete. Run it with

    bench --site <site> execute afintrix_theme.demo.hr_demo.run

Records are created only when missing, so the command can be run twice.
"""

import frappe
from frappe.utils import add_days, add_months, getdate, nowdate

COMPANY = "Afintrix (Demo)"
HOLIDAY_LIST = "Afintrix Holidays"

PEOPLE = [
	("Pristia", "Candra", "Female", "UI/UX Designer", "Research & Development", "Active"),
	("Hanna", "Baptista", "Female", "Graphic Designer", "Marketing", "Active"),
	("Miracle", "Geidt", "Female", "Accountant", "Accounts", "Active"),
	("Rayna", "Torff", "Female", "Project Manager", "Management", "Active"),
	("Giana", "Lipshutz", "Female", "Consultant", "Research & Development", "Active"),
	("James", "George", "Male", "Analyst", "Accounts", "Active"),
	("Jordyn", "George", "Male", "Software Developer", "Research & Development", "Active"),
	("Skylar", "Herwitz", "Male", "Business Analyst", "Sales", "Active"),
	("Marcus", "Vaccaro", "Male", "Sales Manager", "Sales", "Suspended"),
	("Alena", "Dorwart", "Female", "HR Manager", "Human Resources", "Left"),
]


def _department(short_name):
	name = f"{short_name} - AD"
	return name if frappe.db.exists("Department", name) else None


def _designation(title):
	if not frappe.db.exists("Designation", title):
		frappe.get_doc({"doctype": "Designation", "designation_name": title}).insert(
			ignore_permissions=True
		)
	return title


def holiday_list():
	if frappe.db.exists("Holiday List", HOLIDAY_LIST):
		return HOLIDAY_LIST

	start = getdate(f"{getdate(nowdate()).year}-01-01")
	end = getdate(f"{getdate(nowdate()).year}-12-31")
	doc = frappe.get_doc(
		{
			"doctype": "Holiday List",
			"holiday_list_name": HOLIDAY_LIST,
			"from_date": start,
			"to_date": end,
		}
	)
	doc.weekly_off = "Friday"
	doc.get_weekly_off_dates()
	doc.insert(ignore_permissions=True)
	return HOLIDAY_LIST


def assign_holiday_list():
	"""v17 links holidays through Holiday List Assignment, not Employee.holiday_list."""
	existing = frappe.db.exists(
		"Holiday List Assignment",
		{"assigned_to": COMPANY, "applicable_for": "Company", "docstatus": 1},
	)
	if existing:
		return existing

	doc = frappe.get_doc(
		{
			"doctype": "Holiday List Assignment",
			"holiday_list": holiday_list(),
			"applicable_for": "Company",
			"assigned_to": COMPANY,
			"from_date": getdate(f"{getdate(nowdate()).year}-01-01"),
		}
	)
	doc.insert(ignore_permissions=True)
	doc.submit()
	return doc.name


def employees():
	created = []
	for first, last, gender, designation, department, status in PEOPLE:
		existing = frappe.db.get_value(
			"Employee", {"employee_name": f"{first} {last}", "company": COMPANY}
		)
		if existing:
			created.append(existing)
			continue

		doc = frappe.get_doc(
			{
				"doctype": "Employee",
				"first_name": first,
				"last_name": last,
				"gender": gender,
				"date_of_birth": add_months(nowdate(), -12 * 30),
				"date_of_joining": add_months(nowdate(), -18),
				"company": COMPANY,
				"status": status,
				"designation": _designation(designation),
				"department": _department(department),
				"personal_email": f"{first.lower()}@afintrix.test",
				"cell_number": "0891 8298 493",
			}
		)
		if status == "Left":
			doc.relieving_date = add_days(nowdate(), -20)
			doc.reason_for_leaving = "Moved on"
		doc.insert(ignore_permissions=True)
		created.append(doc.name)
	return created


def attendance(employee_names, days=20):
	statuses = ["Present"] * 7 + ["Half Day", "On Leave", "Absent"]
	made = 0
	for index, employee in enumerate(employee_names[:6]):
		for day in range(1, days + 1):
			date = add_days(nowdate(), -day)
			if getdate(date).weekday() == 4:  # the demo holiday list is off on Friday
				continue
			if frappe.db.exists("Attendance", {"employee": employee, "attendance_date": date}):
				continue
			doc = frappe.get_doc(
				{
					"doctype": "Attendance",
					"employee": employee,
					"attendance_date": date,
					"status": statuses[(index + day) % len(statuses)],
					"company": COMPANY,
				}
			)
			doc.insert(ignore_permissions=True)
			doc.submit()
			made += 1
	return made


def leave(employee_names):
	made = 0
	year_start = getdate(f"{getdate(nowdate()).year}-01-01")
	year_end = getdate(f"{getdate(nowdate()).year}-12-31")

	for index, employee in enumerate(employee_names[:5]):
		leave_type = ["Casual Leave", "Sick Leave", "Privilege Leave"][index % 3]

		if not frappe.db.exists(
			"Leave Allocation",
			{"employee": employee, "leave_type": leave_type, "docstatus": 1},
		):
			allocation = frappe.get_doc(
				{
					"doctype": "Leave Allocation",
					"employee": employee,
					"leave_type": leave_type,
					"from_date": year_start,
					"to_date": year_end,
					"new_leaves_allocated": 12,
					"company": COMPANY,
				}
			)
			allocation.insert(ignore_permissions=True)
			allocation.submit()

		from_date = add_days(nowdate(), 3 + index * 5)
		if frappe.db.exists("Leave Application", {"employee": employee, "from_date": from_date}):
			continue

		application = frappe.get_doc(
			{
				"doctype": "Leave Application",
				"employee": employee,
				"leave_type": leave_type,
				"from_date": from_date,
				"to_date": add_days(from_date, 1),
				"description": "Demo leave request for the Afintrix theme.",
				"company": COMPANY,
				"posting_date": nowdate(),
				"leave_approver": "Administrator",
				"status": "Open" if index % 2 else "Approved",
			}
		)
		application.insert(ignore_permissions=True)
		if application.status == "Approved":
			application.submit()
		made += 1
	return made


def recruitment():
	openings = [
		("Senior Frontend Developer", "Research & Development", 2),
		("Financial Analyst", "Accounts", 1),
		("Talent Acquisition Specialist", "Human Resources", 1),
	]
	made = {"openings": 0, "applicants": 0}

	for title, department, vacancies in openings:
		designation = _designation(title)
		if frappe.db.exists("Job Opening", {"job_title": title, "company": COMPANY}):
			continue
		frappe.get_doc(
			{
				"doctype": "Job Opening",
				"job_title": title,
				"designation": designation,
				"department": _department(department),
				"company": COMPANY,
				"status": "Open",
				"vacancies": vacancies,
				"description": "Demo job opening for the Afintrix theme.",
			}
		).insert(ignore_permissions=True)
		made["openings"] += 1

	applicants = [
		("Ellis Bergson", "Senior Frontend Developer", "Open"),
		("Kaiya Vetrovs", "Senior Frontend Developer", "Replied"),
		("Cheyenne Bator", "Senior Frontend Developer", "Hold"),
		("Zaire Ekstrom", "Financial Analyst", "Open"),
		("Alfredo Aminoff", "Financial Analyst", "Accepted"),
		("Cristofer Bator", "Talent Acquisition Specialist", "Rejected"),
		("Justin Lipshutz", "Talent Acquisition Specialist", "Replied"),
	]
	for name, title, status in applicants:
		email = name.lower().replace(" ", ".") + "@example.com"
		if frappe.db.exists("Job Applicant", {"email_id": email}):
			continue
		opening = frappe.db.get_value("Job Opening", {"job_title": title, "company": COMPANY})
		frappe.get_doc(
			{
				"doctype": "Job Applicant",
				"applicant_name": name,
				"email_id": email,
				"job_title": opening,
				"designation": _designation(title),
				"status": status,
			}
		).insert(ignore_permissions=True)
		made["applicants"] += 1
	return made


def payroll(employee_names):
	"""Salary structure, assignments and one month of slips."""
	if not frappe.db.exists("Salary Component", "Basic"):
		frappe.get_doc(
			{
				"doctype": "Salary Component",
				"salary_component": "Basic",
				"type": "Earning",
				"salary_component_abbr": "B",
			}
		).insert(ignore_permissions=True)

	if not frappe.db.exists("Salary Component", "Income Tax"):
		frappe.get_doc(
			{
				"doctype": "Salary Component",
				"salary_component": "Income Tax",
				"type": "Deduction",
				"salary_component_abbr": "IT",
				"variable_based_on_taxable_salary": 0,
			}
		).insert(ignore_permissions=True)

	structure_name = "Afintrix Monthly"
	if not frappe.db.exists("Salary Structure", structure_name):
		structure = frappe.get_doc(
			{
				"doctype": "Salary Structure",
				"name": structure_name,
				"__newname": structure_name,
				"company": COMPANY,
				"payroll_frequency": "Monthly",
				"is_active": "Yes",
				"currency": frappe.db.get_value("Company", COMPANY, "default_currency"),
				"earnings": [
					{"salary_component": "Basic", "amount": 60000, "abbr": "B"}
				],
				"deductions": [
					{"salary_component": "Income Tax", "amount": 4500, "abbr": "IT"}
				],
			}
		)
		structure.insert(ignore_permissions=True)
		structure.submit()

	made = 0
	start = getdate(add_months(nowdate(), -1)).replace(day=1)
	for employee in employee_names[:6]:
		if frappe.db.get_value("Employee", employee, "status") != "Active":
			continue

		if not frappe.db.exists(
			"Salary Structure Assignment", {"employee": employee, "docstatus": 1}
		):
			assignment = frappe.get_doc(
				{
					"doctype": "Salary Structure Assignment",
					"employee": employee,
					"salary_structure": structure_name,
					# the assignment has to sit inside an active fiscal year
					"from_date": start,
					"company": COMPANY,
					"base": 60000,
				}
			)
			assignment.insert(ignore_permissions=True)
			assignment.submit()

		if frappe.db.exists("Salary Slip", {"employee": employee, "start_date": start}):
			continue

		slip = frappe.get_doc(
			{
				"doctype": "Salary Slip",
				"employee": employee,
				"salary_structure": structure_name,
				"start_date": start,
				"posting_date": nowdate(),
				"exchange_rate": 1,
				"company": COMPANY,
			}
		)
		slip.insert(ignore_permissions=True)
		slip.submit()
		made += 1
	return made


def run():
	frappe.set_user("Administrator")
	frappe.flags.in_import = True
	holiday_list()
	assign_holiday_list()
	names = employees()
	result = {
		"employees": len(names),
		"attendance": attendance(names),
		"leave": leave(names),
		"recruitment": recruitment(),
	}
	try:
		result["salary_slips"] = payroll(names)
	except Exception as exc:  # payroll setup is the most fragile part of the seed
		result["salary_slips"] = f"skipped: {exc}"
	frappe.db.commit()
	print(result)
	return result
