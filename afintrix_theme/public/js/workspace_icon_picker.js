/**
 * Afintrix Theme — Workspace Icon Picker
 * Adds an interactive icon selection dialog to the 'custom_animated_icon' field.
 */
frappe.ui.form.on("Workspace", {
    refresh: function(frm) {
        NaidapaIconPicker.setup(frm);
    },
    onload: function(frm) {
        NaidapaIconPicker.setup(frm);
    }
});

const NaidapaIconPicker = {
    setup: function(frm) {
        const field = frm.fields_dict.custom_animated_icon;
        if (!field) return;

        // Ensure we don't add multiple buttons
        if (field.$wrapper.find('.btn-icon-picker').length) return;

        // Add a helper button next to the label or in the input group
        const $btn = $(`<button class="btn btn-xs btn-default btn-icon-picker" style="margin-left: 10px; margin-top: -2px;">
            <iconify-icon icon="line-md:search" width="14" style="vertical-align: middle;"></iconify-icon>
            <span style="vertical-align: middle; margin-left: 4px;">Choose Icon</span>
        </button>`);

        field.$label_area.append($btn);

        $btn.on('click', (e) => {
            e.preventDefault();
            this.show_dialog(frm);
        });

        // Also trigger on double click of the input
        if (field.$input) {
            field.$input.on('dblclick', () => {
                this.show_dialog(frm);
            });
            
            // Add a placeholder/hint if empty
            if (!frm.doc.custom_animated_icon) {
                field.$input.attr('placeholder', 'e.g. text-box-multiple (Double-click to browse)');
            }
        }
    },

    show_dialog: function(frm) {
        const icons = [
            'home', 'account', 'document-list', 'receipt', 'alert-circle', 'chat', 
            'briefcase', 'watch', 'arrows-horizontal', 'dashboard', 'cog', 'edit', 
            'coin', 'text-box', 'calendar', 'heart', 'buy', 'map-pin', 'email', 
            'speed-small', 'check-all', 'search', 'plus', 'minus', 'close', 
            'menu', 'settings', 'folder', 'image', 'video', 'music', 'printer', 
            'cloud', 'download', 'upload', 'lock', 'unlock', 'key', 'bell', 'star',
            'document-code', 'grid-3', 'hash', 'link', 'list', 'navigation', 
            'phone', 'play', 'rss', 'share', 'shopping-cart', 'sun', 'moon',
            'text-box-multiple', 'text-box-plus', 'text-box-remove', 'user-plus',
            'external-link', 'filter', 'flag', 'info', 'mail', 'message', 'more-horizontal',
            'notification', 'paper-plane', 'refresh', 'shield', 'trash', 'user'
        ];

        const d = new frappe.ui.Dialog({
            title: __('Select Animated Icon'),
            fields: [
                {
                    label: __('Search Icons'),
                    fieldname: 'search',
                    fieldtype: 'Data'
                },
                {
                    label: __('Icons'),
                    fieldname: 'icon_grid',
                    fieldtype: 'HTML'
                }
            ]
        });

        const render_grid = (filter = '') => {
            let html = `<div class="icon-grid" style="display:grid; grid-template-columns: repeat(auto-fill, minmax(80px, 1fr)); gap: 12px; max-height: 450px; overflow-y: auto; padding: 15px;">`;
            
            icons.filter(i => i.includes(filter.toLowerCase())).forEach(icon => {
                html += `
                    <div class="icon-item text-center" data-icon="${icon}" style="padding: 10px; border: 1px solid var(--border-color); border-radius: 8px; cursor:pointer; transition: all 0.2s; background: var(--bg-color);">
                        <iconify-icon icon="line-md:${icon}" width="28" height="28"></iconify-icon>
                        <div style="font-size: 11px; margin-top: 8px; color: var(--text-muted); overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${icon}</div>
                    </div>
                `;
            });
            
            html += `</div>`;
            d.get_field('icon_grid').$wrapper.html(html);

            // Add hover effects and click event
            d.get_field('icon_grid').$wrapper.find('.icon-item').on('mouseenter', function() {
                $(this).css({'background-color': 'var(--fg-hover-color)', 'border-color': 'var(--primary-color)', 'transform': 'scale(1.05)'});
            }).on('mouseleave', function() {
                $(this).css({'background-color': 'var(--bg-color)', 'border-color': 'var(--border-color)', 'transform': 'scale(1)'});
            }).on('click', function() {
                const selectedIcon = $(this).attr('data-icon');
                frm.set_value('custom_animated_icon', selectedIcon);
                d.hide();
            });
        };

        d.fields_dict.search.$input.on('input', (e) => {
            render_grid(e.target.value);
        });

        d.show();
        render_grid();
    }
};

