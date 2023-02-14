from odoo import api, models, fields
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from odoo.tools.translate import _
from datetime import timedelta
import logging
from odoo.tests.common import Form
import email
import datetime


class LibraryBook(models.Model):

    _name = 'library.book'
    #_inherit = 'base.archive'
    #manager_remarks = fields.Text('Manager Remarks')
    _description = 'Library Book'
    _order = 'date_release desc, name'    
    _sql_constraints = [('name_uniq', 'UNIQUE (name)','O título do livro deve ser único.'),
                ('positive_page', 'CHECK(pages>0)', 'O número de páginas deve ser positivo')]
    image = fields.Binary(attachment=True)
    html_description = fields.Html()
    name = fields.Char('Título', required=True)
    category_id = fields.Many2one('library.book.category')
    #short_name = fields.Char('Título Curto',required=True)
    #date_release = fields.Date('Data de Lançamento')
    author_ids = fields.Many2many('res.partner',string='Autor(s)')
    isbn = fields.Char('ISBN')
    short_name = fields.Char('Título Curto', translate=True, index=True)
    notes = fields.Text('Notas Internas')
    state = fields.Selection(
        [('draft', 'Não Disponível'),
        ('available', 'Disponível'),
        ('borrowed', 'Emprestado'),
        ('lost', 'Perdido')],
        'Status', default="available")
    description = fields.Html('Descrição',sanitize=True, strip_style=False)
    cover = fields.Binary('Capa de livro')
    out_of_print = fields.Boolean('Fora de impressão?')
    date_release = fields.Date('Data de Lançamento', groups='my_library.group_release_dates')
    active = fields.Boolean('Active', default=True)
    date_updated = fields.Datetime('Última Atualização')
    pages = fields.Integer('Número de páginas')
    reader_rating = fields.Float('Avaliação média do leitor',
                                    digits=(14, 4), # Optional precision decimals,
    )
    cost_price = fields.Float('Book Cost')
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
    
    
    category_id = fields.Many2one('library.book.category')

    age_days = fields.Float(
        string='Dias Desde o Lançamento',
        compute='_compute_age',
        inverse='_inverse_age',
        search='_search_age',
        store=False, # optional
        compute_sudo=True # optional
        )
    old_edition = fields.Many2one('library.book', string='Old Edition')
    
    #contar o número de pedidos de aluguel de um livro
    rent_count = fields.Integer(compute="_compute_rent_count")
    def _compute_rent_count(self):
        BookRent = self.env['library.book.rent']
        for book in self:
            book.rent_count = BookRent.search_count(
                                [('book_id', '=', book.id)]
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

    #método auxiliar para verificar se uma transição de estado é permitida
    @api.model
    def is_allowed_transition(self, old_state, new_state):
        allowed = [('draft', 'available'),
                    ('available', 'borrowed'),
                    ('borrowed', 'available'),
                    ('available', 'lost'),
                    ('borrowed', 'lost'),
                    ('lost', 'available'),
                    ('available','draft')]
        return (old_state, new_state) in allowed

    #método para alterar o estado de alguns livros para um novo estado que é passado como um argumento
    def change_state(self, new_state):
        for book in self:
            if book.is_allowed_transition(book.state, new_state):
                book.state = new_state
            else:
                msg = _('Moving from %s to %s is not allowed') % (book.state, new_state)
                raise UserError(msg)

    #método para alterar o estado do livro chamando o método change_state
    def make_available(self):
        self.change_state('available')

    def make_borrowed(self):
        self.change_state('borrowed')
        
        
    def make_lost(self):
        self.change_state('lost')
    
    def make_draft(self):
        self.change_state('draft')

    #método de erro
    def post_to_webservice(self, data):
        try:
            req = requests.post('http://my-test-service.com',
            data=data, timeout=10)
            content = req.json()
        except IOError:
            error_msg = _("Something went wrong during data submission")
            raise UserError(error_msg)
        return content

    # método chamado get_all_library_members
    def log_all_library_members(self):
        # Este é um conjunto de registros vazio do modelo library.member
        library_member_model = self.env['library.member']
        all_members = library_member_model.search([])
        print("ALL MEMBERS:", all_members)
        return True

    #atualizar o campo date_updated de um livro
    def change_release_date(self):
        self.ensure_one()
        self.date_release = fields.Date.today()

    #Procurando por registros
    def find_book(self):
        domain = [
                '|',
                '&', ('name', 'ilike', 'Book Name'),
                ('category_id.name', 'ilike', 'Category Name'),
                '&', ('name', 'ilike', 'Book Name 2'),
                ('category_id.name', 'ilike', 'Category Name 2')
                ]
        books = self.search(domain)

    def find_partner(self):
        PartnerObj = self.env['res.partner']
        domain = [
                '&', ('name', 'ilike', 'Parth Gajjar'),
                ('company_id.name', '=', 'Odoo')
                ]
        partner = PartnerObj.search(domain)  


    #filtrar registros
    @api.model
    def books_with_multiple_authors(self, all_books):
        return all_books.filter(lambda b: len(b.author_ids) > 1)
    
    #método para recuperar os nomes dos autores do conjunto de registros de livros, passado como argumento
    @api.model
    def get_author_names(self, books):
        return books.mapped('author_ids.name')

    #Classificando conjuntos de registros já existente
    @api.model
    def sort_books_by_date(self, books):
        return books.sorted(key='date_release')
    
    #evitar que usuários que não são membros do grupo bibliotecário modifiquem o valor de manager_remarks
    #@api.model
    #def create(self, values):
        #if not self.user_has_groups('my_library.acl_book_librarian'):
          #  if 'manager_remarks' in values:
         #       raise UserError(
        #                        'You are not allowed to modify '
       #                         'manager_remarks'
      #                          )
     #   return super(LibraryBook, self).create(values)
    #def write(self, values):
        #if not self.user_has_groups('my_library.acl_book_librarian'):
            #if 'manager_remarks' in values:
            #    raise UserError(
           #                     'You are not allowed to modify '
          #                      'manager_remarks'
         #                       )
        #return super(LibraryBook, self).write(values)

    #pesquisar um livro por título, autor ou ISBN
    def name_get(self):
        result = []
        for book in self:
            authors = book.author_ids.mapped('name')
            name = '%s (%s)' % (book.name, ', '.join(authors))
            result.append((book.id, name))
            return result
    
    #pesquisar no modulo libray.book pelo autor, título ou ISBN
    @api.model
    def _name_search(self, name='', args=None,
        operator='ilike',
        limit=100, name_get_uid=None):
        args = [] if args is None else args.copy()
        if not(name == '' and operator == 'ilike'):
            args += ['|', '|',
                    ('name', operator, name),
                    ('isbn', operator, name),
                    ('author_ids.name', operator, name)
                    ]
        return super(LibraryBook, self)._name_search(
                                                    name=name, args=args, operator=operator,
                                                    limit=limit, name_get_uid=name_get_uid)

    #extrair resultados agrupados
    @api.model
    def _get_average_cost(self):
        grouped_result = self.read_group(
                                        [('cost_price', "!=", False)], # Domain
                                        ['category_id', 'cost_price:avg'], # Fields to ccess
                                        ['category_id'] # group_by
                                    )
        return grouped_result

    #permitir que usuários normais emprestem livros
    def book_rent(self):
        self.ensure_one()    
        if self.state != 'available':
            raise UserError(_('Book is not available for renting'))
        

    #informações sobre o número médio de dias que um usuário mantém um determinado livro
    def average_book_occupation(self):
        self.flush()
        sql_query = """
                    SELECT lb.name, avg((EXTRACT(epoch from age(return_date, rent_date)) / 86400))::int
                    FROM library_book_rent AS lbr
                    JOIN library_book as lb ON lb.id = lbr.book_id
                    WHERE lbr.state = 'returned'
                    GROUP BY lb.name;"""
        self.env.cr.execute(sql_query)
        result = self.env.cr.fetchall()
        logging.info("Average book occupation: %s", result)

    #método de retono dos livros
    def return_all_books(self):
        self.ensure_one()
        wizard = self.env['library.return.wizard']
        wizard.create({
                      'borrower_id': self.env.user.partner_id.id}).books_returns()

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
        ondelete='cascade',
        delegate=True)
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

