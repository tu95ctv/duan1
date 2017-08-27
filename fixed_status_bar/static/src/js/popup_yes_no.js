odoo.define('popup_yes_no', function(require) {
    'use strict';
    var ListView = require('web.DataModel');
    ListView.include({
        call_button: function(method, args) {
            if (method =="action_cancel") {
                var user_confirm = confirm('Bạn có muốn hủy nó không')
            }else {
                var user_confirm = true
            }
            if (!user_confirm){
                // do bat buoc phai tra ve session,nen cheatcode thay action_cancel bang read
                arguments[0] = 'read';
            }
            var self = this;
            return this._super.apply(this, arguments);
        },
    })
});