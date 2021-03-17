# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError


class BranchReport(models.TransientModel):
    _name = 'branch.wizard'
    _description = 'Branch Report'

    date_from = fields.Date(string='Date From', required=True, default=datetime.today())
    date_to = fields.Date(string='Date To', required=True, default=datetime.today())
    branch = fields.Many2one('res.branch', string="Branch", required=True)

    @api.constrains('date_to', 'date_from')
    def date_constrains(self):
        for rec in self:
            if rec.date_to < rec.date_from:
                raise ValidationError(_('Sorry, End Date Must be greater Than Start Date...'))

    def print_pdf_action(self):
        data = {
            'model': 'branch.wizard',
            'ids': self.ids,
            'form': {
                'date_from': self.date_from, 'date_to': self.date_to, 'branch': self.branch,
            },
        }

        # ref `module_name.report_id` as reference.
        return self.env.ref('branch_report.report_branch_id').report_action(self, data=data)

    # branch = fields.Many2one('res.branch', string="Branch")
    # date_from = fields.Date("Date From")
    # date_to = fields.Date("Date To")
    #
    # def print_pdf_action(self):
    #     print('kkkk', self.read()[0])
    #
    #     data = {
    #         'model': 'branch.wizard',
    #         'form': self.read()[0]
    #     }
    #     selected_id = data['form']['branch'][0]
    #     date_from = data['form']['date_from']
    #     date_to = data['form']['date_to']
    #
    #     @api.multi
    #     def get_report(self):
    #         data = {
    #             'model': self._name,
    #             'ids': self.ids,
    #             'form': {
    #                 'date_start': self.date_start, 'date_end': self.date_end,
    #             },
    #         }
    #
    #         # line = self.SaleOrderLine.search([('order_id', '=', self.sale_normal_delivery_charges.id),
    #         total_values = self.env['account.payment'].search([('branch_id.id', '=', selected_id)])
    #
    #     return self.env.ref('branch_report.report_branch_id').report_action(self, data=data)


class InheritAccountPayment(models.Model):
    _inherit = 'account.payment'