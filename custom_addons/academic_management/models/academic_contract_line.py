from odoo import models, fields, api

class AcademicContractLine(models.Model):
    _name = 'academic.contract.line'
    _description = 'Línea de Contrato Académico'

    contract_id = fields.Many2one(
        'academic.contract',
        string='Contrato',
        required=True,
        ondelete='cascade', 
        index=True
    )
    student_id = fields.Many2one(
        'res.partner',
        string='Estudiante',
        related='contract_id.student_id', 
        readonly=True, 
        store=True 
    )
    subject_id = fields.Many2one(
        'academic.subject',
        string='Materia',
        required=True,
        # Aquí es donde aplicaremos el dominio dinámico. Por ahora lo dejamos sin él.
        domain="[('id', 'in', allowed_subject_ids)]" 
    )
    professor_id = fields.Many2one(
        'res.partner',
        string='Profesor Asignado',
        required=True,
        
        domain="[('id', 'in', allowed_professor_ids)]" 
    )
    cost = fields.Monetary(
        string='Costo de Materia',
        required=True,
        default=0.0,
        currency_field='company_currency_id' # Moneda asociada
    )
    company_currency_id = fields.Many2one(
        'res.currency',
        related='contract_id.company_currency_id',
        string="Moneda",
        readonly=True
    )

    # Campos relacionales inversos para el dominio dinámico (los usaremos más adelante)
    allowed_subject_ids = fields.Many2many(
        'academic.subject', 
        compute='_compute_allowed_subjects')
    allowed_professor_ids = fields.Many2many(
        'res.partner', 
        compute='_compute_allowed_professors')
    

    @api.depends('student_id')
    def _compute_allowed_subjects(self):
        for line in self:
            if line.student_id and line.student_id.is_student:
                line.allowed_subject_ids = line.student_id.eligible_subject_ids
            else:
                line.allowed_subject_ids = False # O una lista vacía de IDs

    @api.depends('subject_id')
    def _compute_allowed_professors(self):
        for line in self:
            if line.subject_id:
                line.allowed_professor_ids = line.subject_id.professor_ids
            else:
                line.allowed_professor_ids = False # O una lista vacía de IDs