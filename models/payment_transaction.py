from odoo.addons.payment_tap.controllers.main import TapController
import logging
import pprint
import phonenumbers
from odoo import _, models
from werkzeug import urls
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _get_specific_rendering_values(self, processing_values):
        """ Override of payment to return Paypal-specific rendering values.

        Note: self.ensure_one() from `_get_processing_values`

        :param dict processing_values: The generic and specific processing values of the transaction
        :return: The dict of acquirer-specific processing values
        :rtype: dict
        """
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'tap':
            return res

        payload = self._tap_prepare_payment_request_payload()
        payment_data = self.provider_id._tap_make_request(data=payload)

        token = payment_data["token"]
        self.reference = token
        api_url = "https://checkout.payments.tap.company/"
        _logger.debug(api_url)

        return {'api_url': api_url, 'mode': 'page', 'token': token}

    def _tap_prepare_payment_request_payload(self):
        """ Create the payload for the payment request based on the transaction values.

        :return: The request payload
        :rtype: dict
        """
        user_lang = self.env.context.get('lang')
        phone = phonenumbers.parse(self.partner_phone)
        base_url = self.provider_id.get_base_url()
        redirect_url = urls.url_join(base_url, TapController._return_url)
        return {
            "gateway": {
                "publicKey": self.provider_id.tap_public_key,
                "merchantId": self.provider_id.tap_merchant_id,
                # "merchantId": None,
                "contactInfo": True,
                "customerCards": True,
                "language": "en",
                "notifications": "standard",
                "onLoad": None,
                "backgroundImg": None,
                "saveCardOption": True,
                "supportedCurrencies": "all",
                "supportedPaymentMethods": "all",
                "labels": {
                    "cardNumber": "Card Number",
                    "expirationDate": " Exp Date",
                    "cvv": "CVV",
                    "cardHolder": "Holder Name",
                    "actionButton": "Pay"
                },
                "style": {
                    "base": {
                        "color": "#535353",
                        "lineHeight": "18px",
                        "fontFamily": "sans-serif",
                        "fontSmoothing": "antialiased",
                        "fontSize": "16px",
                        "::placeholder": {
                            "color": "rgba(0, 0, 0, 0.26)",
                            "fontSize": "15px"
                        }
                    },
                    "invalid": {
                        "color": "red",
                        "iconColor": "#fa755a "
                    }
                }
            },
            "customer": {
                "first_name": self.partner_name,
                "middle_name": None,
                "last_name": self.partner_name,
                "email": self.partner_email,
                "phone": {
                    "country_code": phone.country_code,
                    "number": phone.national_number
                }
            },
            "order": {
                "amount": f"{self.amount:.2f}",
                "qtys": 0,
                "currency": "KWD",
                "items": []
            },
            "transaction": {
                "mode": "charge",
                "charge": {
                    "saveCard": False,
                    "threeDSecure": True,
                    "description": "Description",
                    "statement_descriptor": "Sample",
                    "reference": {
                        "transaction": "txn_0001",
                        "order": "ord_0001"
                    },
                    "metadata": {},
                    "receipt": {
                        "email": False,
                        "sms": True
                    },
                    "redirect": redirect_url,
                    "post": None
                },
                "authorize": {
                    "saveCard": False,
                    "threeDSecure": True,
                    "description": "Test Description",
                    "statement_descriptor": "Sample",
                    "reference": {
                        "transaction": "txn_0001",
                        "order": "ord_0001"
                    },
                    "metadata": {},
                    "receipt": {
                        "email": False,
                        "sms": True
                    },
                    "redirect": redirect_url,
                    "post": None
                }
            }
        }

    def _process_notification_data(self, data):
        """ Override of payment to process the transaction based on Mollie data.

        Note: self.ensure_one()

        :param dict data: The feedback data sent by the provider
        :return: None
        """
        self.ensure_one()

        super()._process_notification_data(data)
        if self.provider_code != 'tap':
            return

        payment_data = self.provider_id._tap_check_response(data.get("tap_id"))
        payment_status = payment_data['response']['code']

        if payment_status == '200':
            self._set_pending()
        elif payment_status == '001':
            self._set_authorized()
        elif payment_status == '000':
            self._set_done()
        else:
            self._set_canceled(
                "Tap: " + _("Canceled payment with status: %s", payment_data['response']['message']))

    def _get_tx_from_notification_data(self, provider_code, data):
        """ Override of payment to find the transaction based on Mollie data.

        :param str provider: The provider of the acquirer that handled the transaction
        :param dict data: The feedback data sent by the provider
        :return: The transaction if found
        :rtype: recordset of `payment.transaction`
        :raise: ValidationError if the data match no transaction
        """
        tx = super()._get_tx_from_notification_data(provider_code, data)
        if provider_code != 'tap':
            return tx

        tx = self.search([('reference', '=', data.get('token')),
                         ('provider_code', '=', 'tap')])
        if not tx:
            raise ValidationError(
                "Tap: " +
                _("No transaction found matching reference %s.", data.get('token'))
            )
        return tx
