from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class PayrollWizard(models.TransientModel):
    _name = 'payroll.wizard'
    _description = 'Payroll Payment'

    journal_id = fields.Many2one('account.journal', string="Journal")
    payment_date = fields.Date(string="Payment Date", compute='get_date')
    payslip_line = fields.One2many('payroll.wizard.line', 'payment_id')
#     is_lines_added = fields.Boolean('Is Lines Added?', default =False)

    def create_data(self):
        for rec in self.payslip_line:
            rec.slip_id.conveyance = rec.conveyance
            rec.slip_id.mobile_allowance = rec.mobile_allowance
            rec.slip_id.meal_allowance = rec.meal_allowance

    def write_amount(self):
        for record in self.payslip_line:
            rec = self.env['hr.payslip'].search([('number', '=', record.number)])
            rec.write({
                'amount_to_pay': record.amount_to_pay,
            })


class PayrollWizardLine(models.TransientModel):
    _name = 'payroll.wizard.line'
    _description = 'Payroll Payment Line'

    payment_id = fields.Many2one('payroll.wizard')
    slip_id = fields.Many2one('hr.payslip')
    employee_id = fields.Many2one('hr.employee')
    conveyance = fields.Float('Old Advance')
    mobile_allowance = fields.Float('Current Advance')
    meal_allowance = fields.Float('Absent Days')

