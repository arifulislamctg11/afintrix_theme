import frappe
from frappe.core.doctype.navbar_settings.navbar_settings import get_app_logo


ICON_MAP = [
    (["home", "dashboard"], "home"),
    (["buy", "purchase", "procurement"], "check-list-3"),
    (["sell", "sale", "crm"], "briefcase"),
    (["stock", "inventory"], "clipboard"),
    (["asset"], "document-report"),
    (["acc", "finance", "pay", "tax"], "document-list"),
    (["manuf", "work", "build"], "cog"),
    (["qual", "check"], "check-all"),
    (["proj", "task"], "document-list"),
    (["supp", "help", "ticket"], "chat-bubble"),
    (["user", "hr", "employee", "payroll", "people"], "person"),
    (["web", "portal"], "laptop"),
    (["set", "setup", "tool", "config"], "cog"),
    (["integ", "api"], "grid-3"),
]


def resolve_icon(title_or_name, custom_icon=None):
    invalid_icons = [
        "archive",
        "line-md:archive",
        "shopping-cart",
        "line-md:shopping-cart",
    ]

    if custom_icon and str(custom_icon).strip() not in invalid_icons:
        icon_str = str(custom_icon).strip()

        if icon_str.startswith("line-md:"):
            return icon_str[8:]

        return icon_str

    val = (title_or_name or "").lower()

    for keywords, icon_name in ICON_MAP:
        for kw in keywords:
            if kw in val:
                return icon_name

    return "grid-3"


@frappe.whitelist()
def get_desktop_pages():

    try:
        theme_settings = frappe.get_cached_doc("Theme Settings")
        workspace_orders = theme_settings.get("workspace_order") or []
    except Exception:
        workspace_orders = []

    # ---------------------------------------------------------
    # CUSTOM WORKSPACE ORDER
    # ---------------------------------------------------------

    if workspace_orders:

        menu_items = []
        groups_map = {}

        sorted_orders = sorted(
            workspace_orders,
            key=lambda x: int(x.idx or 0)
        )

        for row in sorted_orders:

            if not row.workspace:
                continue

            ws_name = row.workspace

            ws_title = (
                row.workspace_label
                or frappe.db.get_value(
                    "Workspace",
                    ws_name,
                    "title"
                )
                or ws_name
            )

            custom_icon = (
                row.icon
                or frappe.db.get_value(
                    "Workspace",
                    ws_name,
                    "custom_animated_icon"
                )
            )

            ws_icon = resolve_icon(
                ws_title,
                custom_icon
            )

            ws_route = ws_name.lower().replace(" ", "-")

            item_data = {
                "name": ws_name,
                "title": ws_title,
                "route": f"/app/{ws_route}",
                "icon_name": ws_icon,
            }

            group_name = (
                row.workspace_group or ""
            ).strip()

            if group_name:

                if group_name in groups_map:

                    groups_map[group_name][
                        "sub_items"
                    ].append(item_data)

                else:

                    group_item = {
                        "is_group": True,
                        "group_name": group_name,
                        "group_slug": group_name.lower().replace(
                            " ",
                            "-"
                        ),
                        "group_icon": resolve_icon(
                            group_name
                        ),
                        "sub_items": [item_data],
                    }

                    groups_map[group_name] = group_item
                    menu_items.append(group_item)

            else:

                menu_items.append({
                    "is_group": False,
                    "name": ws_name,
                    "title": ws_title,
                    "route": f"/app/{ws_route}",
                    "icon_name": ws_icon,
                })

        return {
            "custom_menu": True,
            "items_list": menu_items,
        }

    # ---------------------------------------------------------
    # FALLBACK
    # ---------------------------------------------------------

    workspaces = frappe.get_all(
        "Workspace",
        filters={
            "is_hidden": 0,
        },
        fields=[
            "name",
            "title",
            "parent_page",
            "sequence_id",
            "icon",
        ],
        order_by="sequence_id asc, title asc",
    )

    parent_pages = [
        ws for ws in workspaces
        if not ws.get("parent_page")
    ]

    for row in parent_pages:

        custom_icon = frappe.db.get_value(
            "Workspace",
            row.get("name"),
            "custom_animated_icon"
        )

        row["custom_animated_icon"] = custom_icon

        row["icon_name"] = resolve_icon(
            row.get("title") or row.get("name"),
            custom_icon
        )

        children = [
            ws
            for ws in workspaces
            if ws.get("parent_page") == row.get("name")
        ]

        for child in children:

            child_custom = frappe.db.get_value(
                "Workspace",
                child.get("name"),
                "custom_animated_icon"
            )

            child["custom_animated_icon"] = child_custom

            child["icon_name"] = resolve_icon(
                child.get("title") or child.get("name"),
                child_custom
            )

        row["child_workspace"] = children

    return {
        "custom_menu": False,
        "pages": parent_pages,
    }


def boot_session(bootinfo):

    try:

        theme_settings = frappe.get_cached_doc(
            "Theme Settings"
        )

        bootinfo.sidebar_logo = (
            theme_settings.get("sidebar_logo")
            or "/files/dr-codex-logo.png"
        )

        bootinfo.theme_settings = (
            theme_settings.as_dict()
        )

    except Exception:

        bootinfo.sidebar_logo = (
            "/files/dr-codex-logo.png"
        )


# ---------------------------------------------------------------------------
# Afintrix desk sidebar (Frappe v16) — see public/js/afintrix_sidebar.js
# ---------------------------------------------------------------------------

DEFAULT_HELP_URL = "https://docs.erpnext.com/"


def _slugify(value):
    return (value or "").strip().lower().replace(" ", "-").replace("&", "and")


def _menu_from_desktop_pages():
    """Normalise get_desktop_pages() into a single shape the template can loop over."""
    data = get_desktop_pages() or {}
    menu = []

    if data.get("custom_menu"):
        for item in data.get("items_list") or []:
            if item.get("is_group"):
                menu.append(
                    {
                        "is_group": True,
                        "slug": item.get("group_slug") or _slugify(item.get("group_name")),
                        "title": item.get("group_name"),
                        "icon": item.get("group_icon"),
                        "children": [
                            {"title": sub.get("title"), "route": sub.get("route")}
                            for sub in item.get("sub_items") or []
                        ],
                    }
                )
            else:
                menu.append(
                    {
                        "is_group": False,
                        "slug": _slugify(item.get("name")),
                        "title": item.get("title"),
                        "icon": item.get("icon_name"),
                        "route": item.get("route"),
                    }
                )
        return menu

    for page in data.get("pages") or []:
        children = page.get("child_workspace") or []
        route = "/app/" + _slugify(page.get("name"))

        if children:
            menu.append(
                {
                    "is_group": True,
                    "slug": _slugify(page.get("name")),
                    "title": page.get("title") or page.get("name"),
                    "icon": page.get("icon_name"),
                    "children": [
                        {
                            "title": child.get("title") or child.get("name"),
                            "route": "/app/" + _slugify(child.get("name")),
                        }
                        for child in children
                    ],
                }
            )
        else:
            menu.append(
                {
                    "is_group": False,
                    "slug": _slugify(page.get("name")),
                    "title": page.get("title") or page.get("name"),
                    "icon": page.get("icon_name"),
                    "route": route,
                }
            )

    return menu


def _pop_primary_action(menu, label=None):
    """The green pill at the top of the mockup: the Home workspace, or the first item."""
    primary = None

    for index, item in enumerate(menu):
        if item.get("is_group"):
            continue
        if _slugify(item.get("title")) in ("home", "dashboard"):
            primary = menu.pop(index)
            break

    if primary is None:
        for index, item in enumerate(menu):
            if not item.get("is_group"):
                primary = menu.pop(index)
                break

    if primary is None:
        return None

    return {
        "title": label or primary.get("title"),
        "route": primary.get("route"),
    }


def _user_initials(full_name, email):
    source = (full_name or email or "").strip()
    parts = [p for p in source.replace(".", " ").replace("@", " ").split(" ") if p]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()


def get_sidebar_context():
    try:
        theme_settings = frappe.get_cached_doc("Theme Settings")
    except Exception:
        theme_settings = frappe._dict()

    menu = _menu_from_desktop_pages()
    primary_action = _pop_primary_action(menu, theme_settings.get("sidebar_text"))

    app_logo = (
        theme_settings.get("sidebar_logo")
        or frappe.get_website_settings("app_logo")
        or get_app_logo()
        or "/assets/frappe/images/frappe-framework-logo.svg"
    )

    brand_title = (
        theme_settings.get("title")
        or frappe.get_website_settings("app_name")
        or frappe.get_system_settings("app_name")
        or "Afintrix"
    )

    full_name = frappe.utils.get_fullname(frappe.session.user)

    return {
        "menu": menu,
        "primary_action": primary_action,
        "app_logo": app_logo,
        "brand_title": brand_title,
        "theme_settings": theme_settings,
        "help_url": frappe.conf.get("afintrix_help_url") or DEFAULT_HELP_URL,
        "user_fullname": full_name,
        "user_email": frappe.db.get_value("User", frappe.session.user, "email")
        or frappe.session.user,
        "user_abbr": _user_initials(full_name, frappe.session.user),
    }


@frappe.whitelist()
def get_sidebar_html():
    """Server-rendered Afintrix sidebar, injected into the desk by afintrix_sidebar.js."""
    context = get_sidebar_context()
    return frappe.render_template(
        "afintrix_theme/templates/includes/afintrix/sidebar.html", context
    )
