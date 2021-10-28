# -*- coding: utf-8 -*-
from odoo import api, models


class SaleReportCustom(models.AbstractModel):
    _name = 'report.general_ledger_report_pdf.report_general_document'

    def get_ledgers(self):
        model = self.env.context.get('active_model')
        rec_model = self.env[model].browse(self.env.context.get('active_id'))
        ledgers = self.env['account.move.line'].search([('date', '>=', rec_model.date_from.date()),
                                                       ('date', '<=', rec_model.date_to.date()), ('move_id.state', '=', 'posted'),
                                                       ('account_id', '=', rec_model.account_id.id)], order="date asc")
        return ledgers

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        rec_model = self.env[model].browse(self.env.context.get('active_id'))
        return {
            'doc_ids': self.ids,
            'doc_model': 'general_ledger_report_pdf.general.ledger.wizard',
            'date_from': rec_model.date_from.date(),
            'date_to': rec_model.date_to.date(),
            'account': rec_model.account_id.name,
            'ledgers': self.get_ledgers(),
        }
