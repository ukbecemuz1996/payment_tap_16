# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import pprint

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request

_logger = logging.getLogger(__name__)


class TapController(http.Controller):
    _return_url = "/payment/tap/return"

    @http.route(
        _return_url, type='http', auth='public', methods=['GET','POST'], csrf=False,
        save_session=False
    )
    def tap_return(self, **data):
        """ Process the data returned by Tap after redirection.

        The route is flagged with `save_session=False` to prevent Odoo from assigning a new session
        to the user if they are redirected to this route with a POST request. Indeed, as the session
        cookie is created without a `SameSite` attribute, some browsers that don't implement the
        recommended default `SameSite=Lax` behavior will not include the cookie in the redirection
        request from the payment provider to Odoo. As the redirection to the '/payment/status' page
        will satisfy any specification of the `SameSite` attribute, the session of the user will be
        retrieved and with it the transaction which will be immediately post-processed.

        :param dict data: The feedback data (only `id`) and the transaction reference (`ref`)
                          embedded in the return URL
        """
        if not data:
            return request.redirect('/shop/payment')
        _logger.info("Received Tap return data:\n%s", pprint.pformat(data))
        request.env['payment.transaction'].sudo()._handle_notification_data('tap', data)
        return request.redirect('/payment/status')
