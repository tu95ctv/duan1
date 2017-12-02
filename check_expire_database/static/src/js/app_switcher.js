odoo.define('oc_base.app_swither', function(require) {
    var AppSwither = require('web_enterprise.AppSwitcher');

    AppSwither.include({
        enterprise_expiration_check: function() {
            console.log('+++++ remove check date database +++++');
        },

        enterprise_show_panel: function(options) {
            console.log('+++++ remove check date database +++++');  
        },

        enterprise_hide_panel: function(ev) {
            console.log('+++++ remove check date database +++++');  
        },

        enterprise_code_submit: function(ev) {
            console.log('+++++ remove check date database +++++');  
        },

        enterprise_buy: function(ev) {
            console.log('+++++ remove check date database +++++');  
        },

        enterprise_upsell: function(ev) {
            console.log('+++++ remove check date database +++++');  
        },

    })

})