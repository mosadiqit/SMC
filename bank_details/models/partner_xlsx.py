import xlsxwriter

from odoo import models


class PartnerXlsx(models.AbstractModel):
    _name = 'report.bank_details.report_partner_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        # workbook = xlsxwriter.Workbook("file.xlsx")

        format0 = workbook.add_format({'font_size': 14, 'align': 'vcenter', 'bold': True})
        format1 = workbook.add_format({'font_size': 12, 'align': 'vcenter', 'bold': True})
        format2 = workbook.add_format({'font_size': 10, 'align': 'vcenter', })
        # sheet = workbook.add_worksheet('Partner Info')
        sheet = workbook.add_worksheet()

        sheet.set_column(3, 3, 35)
        sheet.set_column(3, 4, 15)
        sheet.set_column(3, 5, 15)
        sheet.set_column(3, 6, 14)
        sheet.set_column(3, 7, 25)
        sheet.set_column(3, 8, 10)
        sheet.set_column(3, 9, 15)

        sheet.write(3, 3, 'Name', format1)
        sheet.write(3, 4, 'Balance', format1)
        sheet.write(3, 5, 'Mobile', format1)
        sheet.write(3, 6, 'Email', format1)
        sheet.write(3, 7, 'Salesperson', format1)
        sheet.write(3, 8, 'City', format1)
        sheet.write(3, 9, 'Country', format1)
        i = 4
        for rec in partners:
            sheet.write(i, 3, rec.name, format2)
            sheet.write(i, 4, rec.partner_balance, format2)
            sheet.write(i, 5, rec.phone, format2)
            sheet.write(i, 6, rec.email, format2)
            sheet.write(i, 7, rec.user_id.name, format2)
            sheet.write(i, 8, rec.city, format2)
            sheet.write(i, 9, rec.country_id.name, format2)
            i = i + 1


