# -*- coding: utf-8 -*-
from odoo import models, fields

class AcademicSubject(models.Model):
    _name = 'academic.subject'
    _description = 'Materia Académica'

    name = fields.Char(string='Nombre de la Materia', required=True)
    code = fields.Char(string='Código de Materia', required=True, copy=False) # copy=False previene que se copie al duplicar el registro
    description = fields.Text(string='Descripción')
    credits = fields.Integer(string='Créditos', default=0)
    
    professor_ids = fields.Many2many(
        'res.partner', # Modelo de Contactos de Odoo
        'academic_subject_professor_rel', # Nombre de la tabla de relación (generado automáticamente si no se especifica)
        'subject_id', # Nombre de la columna en la tabla de relación que apunta a academic.subject
        'professor_id', # Nombre de la columna en la tabla de relación que apunta a res.partner (profesor)
        string='Profesores Asignados',
        domain=[('is_professor', '=', True)] # Dominio para filtrar solo contactos marcados como profesores
    )

    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'El código de la materia ya existe. ¡Debe ser único!'),
    ]