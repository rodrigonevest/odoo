from odoo import api, models, fields
from odoo.exceptions import ValidationError
from datetime import timedelta

class LibraryBook(models.Model):

    _name = 'library.book'
    _description = 'Library Book'
    _order = 'date_release desc, name'    
    _sql_constraints = [('name_uniq', 'UNIQUE (name)','O título do livro deve ser único.'),
                ('positive_page', 'CHECK(pages>0)', 'O número de páginas deve ser positivo')]
    
    name = fields.Char('Título', required=True)
    category_id = fields.Many2one('library.book.category')
    #short_name = fields.Char('Título Curto',required=True)
    #date_release = fields.Date('Data de Lançamento')
    author_ids = fields.Many2many('res.partner',string='Autor(s)')
    short_name = fields.Char('Título Curto', translate=True, index=True)
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
    publisher_id = fields.Many2one('res.partner', string='Publisher',
        # optional:
        ondelete='set null',
        context={},
        domain=[],
        )
    publisher_city = fields.Char(
        'Cidade do Editor',
        related='publisher_id.city',
        readonly=True)
    author_ids = fields.Many2many('res.partner', string='Autor(s)')
    
    category_id = fields.Many2one('library.book.category')

    age_days = fields.Float(
        string='Dias Desde o Lançamento',
        compute='_compute_age',
        inverse='_inverse_age',
        search='_search_age',
        store=False, # optional
        compute_sudo=True # optional
        )
    #método auxiliar para construir dinamicamente uma lista de alvos selecionáveis
    @api.model
    def _referencable_models(self):
        models = self.env['ir.model'].search([('field_id.name', '=', 'message_ids')])
        return [(x.model, x.name) for x in models]

    #adicionar o campo de referência e usar a função anterior para fornecer uma lista de modelos selecionáveis
    ref_doc_id = fields.Reference(
        selection='_referencable_models',
        string='Reference Document')
    

    #Para adicionar o método e implementar a lógica para escrever no campo calculado
    def _inverse_age(self):
        today = fields.Date.today()
        for book in self.filtered('date_release'):
            d = today - timedelta(days=book.age_days)
            book.date_release = d

    #lógica que permitirá a busca no campo computado, 
    def _search_age(self, operator, value):
        today = fields.Date.today()
        value_days = timedelta(days=value)
        value_date = today - value_days
        # convert the operator:
        # book with age > value have a date < value_date
        operator_map = {
            '>': '<', '>=': '<=',
            '<': '>', '<=': '>=',
            }
        new_op = operator_map.get(operator, operator)
        return [('date_release', new_op, value_date)]

    #lógica de calculo
    @api.depends('date_release')
    def _compute_age(self):
        today = fields.Date.today()
        for book in self:
            if book.date_release:
                    delta = today - book.date_release
                    book.age_days = delta.days
            else:
                book.age_days = 0


    @api.constrains('date_release')
    def _check_release_date(self):
        for record in self:
            if record.date_release and record.date_release > fields.Date.today():
                raise models.ValidationError('Release date must be in the past')

class ResPartner(models.Model):
    _inherit = 'res.partner'
    published_book_ids = fields.One2many(
        'library.book', 'publisher_id',
        string='Published Books')
    authored_book_ids = fields.Many2many(
        'library.book',
        string='Livros Autorizados',
        #relation='library_book_res_partner_rel', #optional
        )
    count_books = fields.Integer( 'Número de livros de autoria',
    compute='_compute_count_books' )

    #calcular a contagem de livros
    @api.depends('authored_book_ids')
    def _compute_count_books(self):
        for r in self:
            r.count_books = len(r.authored_book_ids)

class LibraryMember(models.Model):
    _name = 'library.member'
    _inherits = {'res.partner': 'partner_id'}
    partner_id = fields.Many2one(
        'res.partner',
        ondelete='cascade')
    date_start = fields.Date('Membro Desde')
    date_end = fields.Date('Data de Finalização')
    member_number = fields.Char()
    date_of_birth = fields.Date('Data de nascimento')

class BaseArchive(models.AbstractModel):
    
    _name = 'base.archive'
    active = fields.Boolean(default=True)
    
    def do_archive(self):
        for record in self:
            record.active = not record.active