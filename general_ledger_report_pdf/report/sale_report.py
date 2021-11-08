# -*- coding: utf-8 -*-
from odoo import api, models


class SaleReportCustom(models.AbstractModel):
    _name = 'report.general_ledger_report_pdf.report_general_document'

    def get_ledgers(self):
        model = self.env.context.get('active_model')
        rec_model = self.env[model].browse(self.env.context.get('active_id'))
        ledgers = self.env['account.move.line'].search([('date', '>=', rec_model.date_from),
                                                       ('date', '<=', rec_model.date_to), ('move_id.state', '=', 'posted'),
                                                       ('account_id', '=', rec_model.account_id.id)], order="date asc")
        return ledgers

    def get_opening_bal(self):
        model = self.env.context.get('active_model')
        rec_model = self.env[model].browse(self.env.context.get('active_id'))
        open_bal = self.env['account.move.line'].search(
            [('account_id', '=', rec_model.account_id.id), ('date', '<', rec_model.date_from),
             ('move_id.state', '=', 'posted')])
        bal = 0
        for rec in open_bal:
            bal = bal + rec.balance
        return bal

    def get_closing_bal(self):
        model = self.env.context.get('active_model')
        rec_model = self.env[model].browse(self.env.context.get('active_id'))
        open_bal = self.env['account.move.line'].search(
            [('account_id', '=', rec_model.account_id.id), ('date', '>=', rec_model.date_from), ('date', '<=', rec_model.date_to),
             ('move_id.state', '=', 'posted')])
        bal = 0
        for rec in open_bal:
            bal = bal + rec.balance
        return bal

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        rec_model = self.env[model].browse(self.env.context.get('active_id'))
        return {
            'doc_ids': self.ids,
            'doc_model': 'general_ledger_report_pdf.general.ledger.wizard',
            'date_from': rec_model.date_from,
            'date_to': rec_model.date_to,
            'account': rec_model.account_id.name,
            'ledgers': self.get_ledgers(),
            'opening': self.get_opening_bal(),
            'closing': self.get_closing_bal() + self.get_opening_bal(),
        }
