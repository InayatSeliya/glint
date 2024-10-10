// share_transaction_list.js
frappe.listview_settings['Share Transaction'] = {
    onload: function(listview) {
        // Adding the Cancel button
        listview.page.add_action_item(__('Cancel'), function() {
            listview.call_for_selected_items('glint.share_managment.doctype.share_transaction.share_transaction.cancel_documents');
        }, true);

        // Adding the Submit button
        listview.page.add_action_item(__('Submit'), function() {
            listview.call_for_selected_items('glint.share_managment.doctype.share_transaction.share_transaction.submit_documents');
        }, true);
    }
};