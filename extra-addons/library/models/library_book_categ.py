from odoo import models, fields, api
from odoo.exceptions import ValidationError

class BookCategory(models.Model):
    _name = 'library.book.category'
    _parent_store = True
    _parent_name = "parent_id" # optional if field is 'parent_id'
    name = fields.Char('Categoria')
    parent_path = fields.Char(index=True)
    parent_id = fields.Many2one(
        'library.book.category',
        string='Categoria Parental',
        ondelete='restrict',
        index=True)
    child_ids = fields.One2many('library.book.category',
                                 'parent_id',
                                string='Categorias Infantis')
    
    #verificação impedindo relações de loop
    @api.constrains('parent_id')
    def _check_hierarchy(self):
        if not self._check_recursion():
            raise models.ValidationError('Erro! Você não pode criar categorias recursivas.')