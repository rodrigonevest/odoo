from odoo import models, fields, api
from odoo.exceptions import ValidationError

class LibraryBook(models.Model):

    _name = 'library.book'
    _description = 'Library Book'
    _order = 'date_release desc, name'
    _rec_name = 'short_name'
    _inherit = 'res.partner'
    _sql_constraints = [('name_uniq', 'UNIQUE (name)','O título do livro deve ser único.'),
                ('positive_page', 'CHECK(pages>0)', 'O número de páginas deve ser positivo')]
    name = fields.Char('Título', required=True)
    #short_name = fields.Char('Título Curto',required=True)
    #date_release = fields.Date('Data de Lançamento')
    author_ids = fields.Many2many('res.partner',string='Autor(s)')
    short_name = fields.Char('Short Title', translate=True, index=True)
    notes = fields.Text('Notas Internas')
    state = fields.Selection(
        [('draft', 'Não Disponível'),
        ('available', 'Disponível'),
        ('lost', 'Perdida')],
        'State', default="draft")
    description = fields.Html('Descrição',sanitize=True, strip_style=False)
    cover = fields.Binary('Capa de livro')
    out_of_print = fields.Boolean('Fora de impressão?')
    date_release = fields.Date('Data de Lançamento')
    date_updated = fields.Datetime('Última Atualização')
    active = fields.Boolean('Ativo', default=True)
    pages = fields.Integer('Número de páginas',
                            goups = 'base.group_user',
                            states={'lost':[{'readonly', True}]},
                            help = 'Contagem total de páginas do livro', company_dependent=False)
    reader_rating = fields.Float('Avaliação média do leitor',
                                    digits=(14, 4), # Optional precision decimals,
    )
    cost_price = fields.Float('Book Cost', digits='Book Price')
    currency_id = fields.Many2one('res.currency', string='Moeda')
    retail_price = fields.Monetary('Prreço Varejo',# optional: currency_field='currency_id',
    )
    publisher_id = fields.Many2one(
        'res.partner', string='Publisher',
        # optional:
        ondelete='set null',
        context={},
        domain=[],
        )
    authored_book_ids = fields.Many2many(
        'library.book',
        string='Authored Books',
        # relation='library_book_res_partner_rel' #optional
        )
    @api.constrains('date_release')
    def _check_release_date(self):
        for record in self:
            if record.date_release and record.date_release > fields.Date.today():
                raise models.ValidationError('Release date must be in the past')