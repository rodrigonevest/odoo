from odoo import api, models, fields
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from odoo.tools.translate import _
from datetime import timedelta

class LibraryBook(models.Model):
    _inherit = 'library.book'
    #_name = 'library.book'
    #manager_remarks = fields.Text('Manager Remarks')
    date_return = fields.Date('Date to return')

    def make_borrowed(self):
        day_to_borrow = self.category_id.max_borrow_days or 10
        self.date_return = fields.Date.today() + timedelta(days=day_to_borrow)
        return super(LibraryBook, self).make_borrowed()

    def make_available(self):
        self.date_return = False
        return super(LibraryBook, self).make_borrowed()

    