from datetime import datetime
from pytz import timezone

from odoo import models, fields, api
from odoo.exceptions import UserError


class HrPayslipInh(models.Model):
    _inherit = 'hr.payslip'

    conveyance = fields.Float('Old Advance')
    mobile_allowance = fields.Float('Current Advance')
    meal_allowance = fields.Float('Absent Days')
    balance = fields.Float('Balance', compute='compute_balance')

    def compute_balance(self):
        for rec in self:
            rec.balance = rec.employee_id.user_id.partner_id.credit - rec.employee_id.user_id.partner_id.debit

    def action_compute_deductions(self):
        for rec in self:
            print(rec.number)

            val = {
                'Conveyance': rec.conveyance
            }
            vals_list = []
            category = self.env['hr.salary.rule.category'].search([('code', '=', 'DED')])
            oad = self.env['hr.salary.rule'].search([('code', '=', 'OAD')])
            vals_list.append([0, 0, {
                'name': 'Old Advance',
                'code': 'OAD',
                'sequence': 101,
                'category_id': category.id,
                'salary_rule_id': oad.id,
                'amount': rec.conveyance,
                'total': rec.conveyance,
                'quantity': 1,
            }])

            cad = self.env['hr.salary.rule'].search([('code', '=', 'CAD')])
            vals_list.append([0, 0, {
                'name': 'Current Advance',
                'code': 'CAD',
                'category_id': category.id,
                'sequence': 101,
                'salary_rule_id': cad.id,
                'amount': rec.mobile_allowance,
                'total': rec.mobile_allowance,
                'quantity': 1,
            }])
            ads = self.env['hr.salary.rule'].search([('code', '=', 'ADS')])
            vals_list.append([0, 0, {
                'name': 'Absent Days',
                'code': 'ADS',
                'sequence': 101,
                'category_id': category.id,
                'salary_rule_id': ads.id,
                'amount': rec.meal_allowance,
                'total': rec.meal_allowance,
                'quantity': 1,
            }])
            rec.line_ids = vals_list
            total = rec.meal_allowance + rec.mobile_allowance + rec.conveyance
            for line in rec.line_ids:
                if line.code == 'NET':
                    line.amount = line.amount - total


class HrEmployeeInh(models.Model):
    _inherit = 'hr.employee'

    wage = fields.Float('Wage', compute='_compute_wage')

    def _compute_wage(self):
        for rec in self:
            contract = self.env['hr.contract'].search([('employee_id', '=', rec.id)], limit=1)
            if contract:
                rec.wage = contract.wage
            else:
                rec.wage = 0
