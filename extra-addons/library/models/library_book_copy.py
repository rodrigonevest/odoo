from odoo import models, fields, api

class LibraryBookCopy(models.Model):
    #nome do model
    _name = "library.book.copy"
    _inherit = "library.book"
    _description = "Cópia do Livro da Biblioteca"