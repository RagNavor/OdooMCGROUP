# -*- coding: utf-8 -*-
from odoo import models, fields, api

class AcademicContract(models.Model):
    _name = 'academic.contract'
    _description = 'Contrato Académico'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    name = fields.Char(string='Referencia del Contrato', required=True, copy=False, default=lambda self: self.env['ir.sequence'].next_by_code('academic.contract.sequence') or '/')
    student_id = fields.Many2one(
        'res.partner',
        string='Estudiante',
        required=True,
        domain=[('is_student', '=', True)] 
    )
    contract_date = fields.Date(string='Fecha del Contrato', default=fields.Date.today())
    start_date = fields.Date(string='Fecha de Inicio', required=True)
    end_date = fields.Date(string='Fecha de Fin', required=True)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmado'),
        ('done', 'Finalizado'),
        ('cancelled', 'Cancelado'),
    ], string='Estado', default='draft', tracking=True) 


    contract_line_ids = fields.One2many(
        'academic.contract.line', 
        'contract_id', 
        string='Líneas del Contrato'
    )

   
    total_cost = fields.Monetary(
        string='Costo Total',
        compute='_compute_total_cost', 
        store=True,
        currency_field='company_currency_id'
    )
    company_currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
        string="Moneda",
        readonly=True
    )
    company_id = fields.Many2one(
        'res.company',
        string="Compañía",
        default=lambda self: self.env.company
    )

   
    payment_id = fields.Many2one(
        'account.payment',
        string='Pago Asociado',
        readonly=True, 
        copy=False
    )
    payment_status = fields.Selection([
        ('pending', 'Pendiente'),
        ('paid', 'Pagado'),
        ('partial', 'Parcialmente Pagado'),
        ('overdue', 'Vencido'),
    ], string='Estado de Pago', compute='_compute_payment_status', store=True)


    
    @api.depends('contract_line_ids.cost') 
    def _compute_total_cost(self):
        for contract in self:
            contract.total_cost = sum(line.cost for line in contract.contract_line_ids)

    
    @api.depends('payment_id.state', 'payment_id.amount', 'total_cost')
    def _compute_payment_status(self):
        for contract in self:
            if not contract.payment_id:
                contract.payment_status = 'pending'
            elif contract.payment_id.state == 'posted' and contract.payment_id.amount >= contract.total_cost:
                contract.payment_status = 'paid'
            elif contract.payment_id.state == 'posted' and contract.payment_id.amount < contract.total_cost:
                contract.payment_status = 'partial'
            else:
                contract.payment_status = 'pending' # O un estado para 'draft'/'cancel' del pago si lo consideras

    
    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('academic.contract.sequence') or '/'
        return super(AcademicContract, self).create(vals)