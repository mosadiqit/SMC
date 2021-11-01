# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HelpdeskTicketInh(models.Model):
    _inherit = 'helpdesk.ticket'

    date = fields.Date('Date')
    received_via = fields.Many2one('hr.employee')
    sale_agent = fields.Many2one('hr.employee', string="Sale Agent")
    contact = fields.Char('Contact')
    address = fields.Char('Address')
    product_id = fields.Many2one('product.product')
    warranty = fields.Selection([('in', 'In Warranty'),
                                       ('out', 'Out Warranty'),
                                       ('nr', 'NR')], 'Warranty')
    problem = fields.Char('Problem')
    serial_no = fields.Char('Serial No')
    amount = fields.Float('Service Changes')
    article_no = fields.Char('Article No', related='product_id.article_no')

    confirmation = fields.Selection([('resolved', 'Resolved'),
                                 ('unresolved', 'Unresolved')], 'Client Confirmation')
    seq_no = fields.Char('Helpdesk', required=True, copy=False, readonly=True,
                       index=True, default=lambda self: _('New'))

    @api.model
    def create(self, vals):
        if vals.get('seq_no', _('New')) == _('New'):
            vals['seq_no'] = self.env['ir.sequence'].next_by_code('helpdesk.ticket.sequence') or _('New')
        result = super(HelpdeskTicketInh, self).create(vals)
        return result
