# -*- coding: utf-8 -*-
# from odoo import http


# class ModuleVaovao(http.Controller):
#     @http.route('/module_vaovao/module_vaovao', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/module_vaovao/module_vaovao/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('module_vaovao.listing', {
#             'root': '/module_vaovao/module_vaovao',
#             'objects': http.request.env['module_vaovao.module_vaovao'].search([]),
#         })

#     @http.route('/module_vaovao/module_vaovao/objects/<model("module_vaovao.module_vaovao"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('module_vaovao.object', {
#             'object': obj
#         })

