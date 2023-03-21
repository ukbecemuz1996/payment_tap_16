import logging
import requests
from odoo import _, api, fields, models, service
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class PaymentAcquirer(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('tap', 'Tap')], ondelete={'tap': 'set default'})
    

    tap_public_key = fields.Char(
        string="Publishable Key",
        help="The key solely used to identify the account with Tap",
        required_if_provider="tap",
        groups="base.group_system")

    tap_secret_key = fields.Char(
        string="Secret Key", required_if_provider="tap", groups="base.group_system")

    tap_merchant_id = fields.Char(
        string="Merchant ID", required_if_provider="tap", groups="base.group_system")

    # def _get_default_payment_method_id(self):
    #     self.ensure_one()
    #     if self.provider != 'tap':
    #         return super()._get_default_payment_method_id()
    #     return self.env.ref('payment_tap.payment_method_tap').id

    def _tap_make_request(self, data=None, method='POST'):
        """ Make a request at tap endpoint.

        Note: self.ensure_one()

        :param str endpoint: The endpoint to be reached by the request
        :param dict data: The payload of the request
        :param str method: The HTTP method of the request
        :return The JSON-formatted content of the response
        :rtype: dict
        :raise: ValidationError if an HTTP error occurs
        """
        self.ensure_one()

        url = 'https://checkout.payments.tap.company/api/generate'

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        try:
            response = requests.request(
                method, url, json=data, headers=headers, timeout=60)
            response.raise_for_status()
        except requests.exceptions.RequestException:
            _logger.exception(
                "Unable to communicate with Tap Payment Gateway: %s", url)
            raise ValidationError(
                "Tap: " + _("Could not establish the connection to the API."))
        return response.json()

    def _tap_check_response(self, tap_id):
        """ Make a request at tap endpoint.

        Note: self.ensure_one()

        :param str endpoint: The endpoint to be reached by the request
        :param dict data: The payload of the request
        :param str method: The HTTP method of the request
        :return The JSON-formatted content of the response
        :rtype: dict
        :raise: ValidationError if an HTTP error occurs
        """
        self.ensure_one()

        url = 'https://api.tap.company/v2/charges/{tap_id}'.format(
            tap_id=tap_id)

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Bearer {secret_key}".format(secret_key=self.tap_secret_key)
        }

        try:
            response = requests.request(
                "GET", url, headers=headers, timeout=60)
            response.raise_for_status()
        except requests.exceptions.RequestException:
            _logger.exception(
                "Unable to communicate with Tap Payment Gateway: %s", url)
            raise ValidationError(
                "Tap: " + _("Could not establish the connection to the API."))
        return response.json()

    def _get_redirect_form_view(self, is_validation=False):
        """ Return the view of the template used to render the redirect form.

        For an acquirer to return a different view depending on whether the operation is a
        validation, it must override this method and return the appropriate view.

        Note: self.ensure_one()

        :param bool is_validation: Whether the operation is a validation
        :return: The redirect form template
        :rtype: record of `ir.ui.view`
        """
        self.ensure_one()
        domain = [('name', '=', 'tap_redirect_form')]
        model = self.env['ir.ui.view'].search(domain, limit=1)
        return model
