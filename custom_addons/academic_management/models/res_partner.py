# -*- coding: utf-8 -*-
from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'
    is_student = fields.Boolean(string='Es Estudiante', default=False)
    student_code = fields.Char(string='Código de Estudiante', copy=False)
    is_professor = fields.Boolean(string='Es Profesor', default=False)
    professor_id_number = fields.Char(string='Número de Identificación de Profesor', copy=False)
    # subject_ids = fields.Many2many(
    #     'academic.subject',
    #     'academic_subject_professor_rel',
    #     'professor_id',
    #     'subject_id',
    #     string='Materias que Imparte'
    # )
    eligible_subject_ids = fields.Many2many(
        'academic.subject',
        'res_partner_academic_subject_rel', # Nombre de la tabla de relación
        'partner_id',                      # Columna que apunta a res.partner
        'subject_id',                      # Columna que apunta a academic.subject
        string='Materias Elegibles'
    )

    _sql_constraints = [
        ('student_code_unique', 'unique(student_code)', 'El código de estudiante debe ser único.'),
        ('professor_id_number_unique', 'unique(professor_id_number)', 'El número de identificación del profesor debe ser único.'),
    ]