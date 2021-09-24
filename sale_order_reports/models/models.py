# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResCompanyInh(models.Model):
    _inherit = 'res.company'

    cs = fields.Char('CS')
