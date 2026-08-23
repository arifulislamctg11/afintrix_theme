/**
 * Naidapa Portal Theme — Client-side Enhancements
 * Matches the desk's KI-Admin design language on all portal/web pages.
 */
(function () {
    "use strict";

    const NaidapaPortal = {
        init: function () {
            this.addBodyClass();
            this.enhanceSidebar();
            this.enhanceAccountPage();
            this.enhanceNavbar();
            this.enhanceLists();
        },

        /**
         * Add a marker class to body so CSS can scope portal-specific rules
         */
        addBodyClass: function () {
            document.body.classList.add('naidapa-portal-active');
        },

        /**
         * Enhance the sidebar with icons and better active states
         */
        enhanceSidebar: function () {
            const sidebarItems = document.querySelectorAll('.web-sidebar .sidebar-item a');

            // Icon map: match sidebar label text to an iconify icon
            const iconMap = {
                'home': 'home',
                'addresses': 'map-pin',
                'address': 'map-pin',
                'newsletter': 'email',
                'my account': 'account',
                'orders': 'document-list',
                'order': 'document-list',
                'invoices': 'receipt',
                'invoice': 'receipt',
                'shipments': 'speed-small',
                'issues': 'alert-circle',
                'issue': 'alert-circle',
                'tickets': 'chat',
                'ticket': 'chat',
                'projects': 'briefcase',
                'project': 'briefcase',
                'timesheets': 'watch',
                'timesheet': 'watch',
                'stock movement': 'arrows-horizontal',
                'stock': 'arrows-horizontal',
                'ops dashboard': 'dashboard',
                'service dashboard': 'dashboard',
                'dashboard': 'dashboard',
                'settings': 'cog',
                'profile': 'account',
                'update profile': 'edit',
                'payment': 'coin',
                'payments': 'coin',
                'quotations': 'text-box',
                'quotation': 'text-box',
                'supplier quotation': 'text-box',
                'material request': 'document-list',
                'quality': 'check-all',
                'calendar': 'calendar',
                'wishlist': 'heart',
                'cart': 'buy',
            };

            sidebarItems.forEach(function (link) {
                const text = (link.textContent || '').trim().toLowerCase();

                // Find matching icon
                let iconName = null;
                for (const [key, icon] of Object.entries(iconMap)) {
                    if (text === key || text.includes(key)) {
                        iconName = icon;
                        break;
                    }
                }

                // Only add icon if we found a match and no icon is already present
                if (iconName && !link.querySelector('.np-sidebar-icon')) {
                    const iconEl = document.createElement('iconify-icon');
                    iconEl.setAttribute('icon', 'line-md:' + iconName);
                    iconEl.setAttribute('width', '18');
                    iconEl.setAttribute('height', '18');
                    iconEl.classList.add('np-sidebar-icon');
                    iconEl.style.marginRight = '10px';
                    iconEl.style.flexShrink = '0';
                    link.insertBefore(iconEl, link.firstChild);
                }
            });
        },

        /**
         * Enhance the My Account page with better card borders
         */
        enhanceAccountPage: function () {
            const accountRows = document.querySelectorAll('.account-info > .col');
            const borderColors = [
                'var(--np-primary)',           // First row: teal
                '#10b981',                      // Second row: emerald
                '#0d6b59',                      // Third row: dark teal
                '#6366f1',                      // Fourth row: indigo
            ];

            accountRows.forEach(function (row, index) {
                if (index > 0) {
                    row.style.borderLeft = '4px solid ' + (borderColors[index] || borderColors[0]);
                }
            });
        },

        /**
         * Style the navbar to match desk theme
         */
        enhanceNavbar: function () {
            const navbar = document.querySelector('.navbar');
            if (!navbar) return;

            // Add navbar brand icon if none exists (matches desk DrCodeX branding)
            const brand = navbar.querySelector('.navbar-brand');
            if (brand && !brand.querySelector('img') && !brand.querySelector('.np-brand-icon')) {
                const brandIcon = document.createElement('span');
                brandIcon.classList.add('np-brand-icon');
                brandIcon.style.cssText = 'display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;background:var(--np-primary);color:#fff;border-radius:6px;font-weight:800;font-size:14px;margin-right:8px;';
                brandIcon.textContent = brand.textContent.trim().charAt(0);
                // Don't insert if there's already an image
                if (!brand.querySelector('img')) {
                    brand.insertBefore(brandIcon, brand.firstChild);
                }
            }
        },

        /**
         * Enhance list pages (orders, invoices, etc.)
         */
        enhanceLists: function () {
            // Add hover effects to list items
            document.querySelectorAll('.list-row, .result').forEach(function (item) {
                item.style.transition = 'var(--np-transition)';
            });
        }
    };

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () {
            NaidapaPortal.init();
        });
    } else {
        NaidapaPortal.init();
    }

    // Also run on frappe.ready if available
    if (window.frappe && frappe.ready) {
        frappe.ready(function () {
            NaidapaPortal.init();
        });
    }
})();
