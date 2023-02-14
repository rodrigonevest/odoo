from odoo import http
from odoo.http import request


class Main(http.Controller):

     # controlador que sirva a lista de livros
    @http.route('/books', type='http', auth="user", website=True)
    def library_books(self):
        return request.render(
            'library.books', {
                'books': request.env['library.book'].sudo().search([]),
            })

    @http.route('/books/<model("library.book"):book>', type='http', auth="user", website=True)
    def library_book_detail(self, book):
        return request.render(
            'library.book_detail', {
                                    'book': book,
                                    })
    
    @http.route('/library/books', type='json',auth='none')
    #função para servir as mesmas informações no formato JSON
    def books_json(self):
        records = request.env['library.book'].sudo().search([])
        return records.read(['name'])

    @http.route('/library/books', type='http', auth='none')
    def books(self):
        books = request.env['library.book'].sudo().search([])
        html_result = '<html><body><ul>'
        
        for book in books:
            html_result += "<li> %s </li>" % book.name
        html_result += '</ul></body></html>'
        return html_result
    
    #caminho que mostre todos os livros 
    @http.route('/library/all-books', type='http', auth='none')       
    def all_books(self):
        books = request.env['library.book'].sudo().search([])
        html_result = '<html><body><ul>'
        for book in books:
            html_result += "<li> %s </li>" % book.name
        html_result += '</ul></body></html>'
        return html_result
    
    #caminho que mostre todos os livros e indique quais foram escritos pelo atual usuário
    @http.route('/library/all-books/mark-mine', type='http', auth='public')
    def all_books_mark_mine(self):
        books = request.env['library.book'].sudo().search([])
        html_result = '<html><body><ul>'
        for book in books:
            if request.env.user.partner_id.id in book.author_ids.ids:
                html_result += "<li> <b>%s</b> </li>" % book.name
            else:
                html_result += "<li> %s </li>" % book.name
        html_result += '</ul></body></html>'
        return html_result

    #caminho que mostre os livros do usuário atual    
    @http.route('/library/all-books/mine', type='http', auth='user')
    def all_books_mine(self):
        books = request.env['library.book'].search([
                    ('author_ids', 'in', request.env.user.partner_id.ids), ])
        html_result = '<html><body><ul>'
        for book in books:
            html_result += "<li> %s </li>" % book.name
        html_result += '</ul></body></html>'
        return html_result

    @http.route('/library/book_details', type='http', auth='none')
    def book_details(self, book_id):
        record = request.env['library.book'].sudo().browse(int(book_id))
        return u'<html><body><h1>%s</h1>Authors: %s' % (record.name, u', '.join(record.author_ids.mapped('name')) or 'none', )

    @http.route('/demo_page', type='http', auth='none')
    def books(self):
        image_url = '/library/static/src/image/odoo.png'
        html_result = """<html>
                            <body>
                                <img src="%s"/>
                            </body>
                        </html>""" % image_url
        return html_result

   
   