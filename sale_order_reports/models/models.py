# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResCompanyInh(models.Model):
    _inherit = 'res.company'

    cs = fields.Char('CS')


class SaleOrderInh(models.Model):
    _inherit = 'sale.order'

    def get_mobile(self, user):
        employee = self.env['hr.employee'].search([('user_id', '=', user.id)], limit=1)
        if employee:
            return employee.mobile_phone
        else:
            return ''
