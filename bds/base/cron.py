# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
import time
from threading import current_thread

class Cron(models.Model):

    _inherit = "ir.cron"
    _logger = logging.getLogger(_inherit)
    @api.model
    def worker(self):
        print 'current_thread',current_thread().name
        logging.debug('Starting')
        time.sleep(1)
        logging.debug('Exiting')