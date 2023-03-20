/* global Stripe */
odoo.define('payment_stripe.payment_form', require => {
    'use strict';

    const core = require('web.core');
    const ajax = require('web.ajax');

    const checkoutForm = require('payment.checkout_form');
    const manageForm = require('payment.manage_form');

    const stripeMixin = {

        /**
         * Redirect the customer to Stripe hosted payment page.
         *
         * @override method from payment.payment_form_mixin
         * @private
         * @param {string} provider - The provider of the payment option's acquirer
         * @param {number} paymentOptionId - The id of the payment option handling the transaction
         * @param {object} processingValues - The processing values of the transaction
         * @return {undefined}
         */
        _processRedirectPayment: function (provider, paymentOptionId, processingValues) {
            if (provider !== 'tap') {
                return this._super(...arguments);
            }

            // const tap_public_key = processingValues['tap_public_key'];
            // const tap_merchant_id = processingValues['tap_merchant_id'];
            // console.log("okba", tap_public_key, tap_merchant_id);
            

            // goSell.openPaymentPage();   
        },

    };

    checkoutForm.include(stripeMixin);
    manageForm.include(stripeMixin);

});
