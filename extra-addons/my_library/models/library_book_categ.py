from odoo import api, models, fields
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from odoo.tools.translate import _
from datetime import timedelta

class LibraryBookCategory(models.Model):
    _inherit = 'library.book.category'
    max_borrow_days = fields.Integer(
                                    'Maximum borrow days',
                                    help="For how many days book can be borrowed",
                                    default=10)