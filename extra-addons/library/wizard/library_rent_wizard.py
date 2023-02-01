from odoo import models, fields, api

class LibraryRentWizard(models.TransientModel):
    _name = 'library.rent.wizard'
    borrower_id = fields.Many2one('res.partner', string='Borrower')
    book_ids = fields.Many2many('library.book', string='Books')

    

    def add_book_rents(self):
        rentModel = self.env['library.book.rent']
        for wiz in self:
            for book in wiz.book_ids:
                rentModel.create({
                                'borrower_id': wiz.borrower_id.id,
                                'book_id': book.id
                                })
        borrowers = self.mapped('borrower_id')
        action = borrowers.get_formview_action()
        if len(borrowers.ids) > 1:
            action['domain'] = [('id', 'in', tuple(borrowers.ids))]
            action['view_mode'] = 'tree,form'
        return action
    
    def _default_member(self):
        if self.context.get('active_model') == 'res.partner':
            return self.context.get('active_id', False)


    def books_returns(self):
        loanModal = self.env['library.book.rent']
        for rec in self:
            loans = loanModal .search(
                                    [('state', '=', 'ongoing'),
                                    ('book_id', 'in', rec.book_ids.ids),
                                    ('borrower_id', '=', rec.borrower_id.id)]
                                    )
            for loan in loans:
                loan.book_return()

    