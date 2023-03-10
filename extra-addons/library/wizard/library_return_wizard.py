from odoo import models, fields, api


class LibraryReturnWizard(models.TransientModel):
    _name = 'library.return.wizard'
    borrower_id = fields.Many2one('res.partner', string='Member')
    book_ids = fields.Many2many('library.book', string='Books')


    #faz o retorno do livro
    def books_returns(self):
        loanModal = self.env['library.book.rent']
        for rec in self:
            loans = loanModal.search(
                                    [('state', '=', 'ongoing'),
                                    ('book_id', 'in', rec.book_ids.ids),
                                    ('borrower_id', '=', rec.borrower_id.id)]
                                    )
            for loan in loans:
                loan.book_return()
                

    #retorna a lista de livros por usuario com o método compute
    @api.depends('borrower_id')
    def onchange_member(self):
        rentModel = self.env['library.book.rent']
        books_on_rent = rentModel.search(
                                        [('state', '=', 'ongoing'),
                                        ('borrower_id', '=', self.borrower_id.id)]
                                        )
        book_ids = fields.Many2many('library.book',
                                    string='Books',
                                    compute="onchange_member",
                                    readonly=False)
        
    """
    teste1
    @api.onchange('borrower_id')
    def onchange_member(self):
        rentModel = self.env['library.book.rent']
        books_on_rent = rentModel.search(
                                        [('state', '=', 'ongoing'),
                                        ('borrower_id', '=', self.borrower_id.id)]
                                        )
        self.book_ids = books_on_rent.mapped('book_id')

        teste2
      @api.onchange('member_id')
    def onchange_member(self):
        rentModel = self.env['library.book.rent']
        books_on_rent = rentModel.search(
        [('state', '=', 'ongoing'),
        ('borrower_id', '=', self.borrower_id.id)]
        )
        self.book_ids = books_on_rent.mapped('book_id')
        result = {
                'domain': {'book_ids': [
                ('id', 'in', self.book_ids.ids)]
                }
                }
        late_domain = [
                        ('id', 'in', books_on_rent.ids),
                        ('expected_return_date', '<', fields.Date.today())
                        ]
        late_books = loans.search(late_domain)
        if late_books:
            message = ('Warn the member that the following '
                        'books are late:\n')
            titles = late_books.mapped('book_id.name')
            result['warning'] = {'title': 'Late books',
                'message': message + '\n'.join(titles)
            }
        return result
    """