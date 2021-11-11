from datetime import datetime
from pytz import timezone

from odoo import models, fields, api
from odoo.exceptions import UserError


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
