from odoo import api, fields, models
from odoo.exceptions import UserError



class SampleRangeLine(models.Model):
    _name ='sample.range.line'


    srf_id = fields.Many2one('lerm.civil.srf' , string="SRF ID" )
    sample_range = fields.Char(string="Sample Range." ,required=True,readonly=True, default=lambda self: 'New')
    sample_qty = fields.Integer(string="Sample Quantity")
    casting = fields.Boolean(string="Casting")
    discipline_id = fields.Many2one('lerm_civil.discipline',string="Discipline")
    group_id = fields.Many2one('lerm_civil.group',string="Group")
    material_id = fields.Many2one('product.template',string="Material")
    brand = fields.Char(string="Brand")
    size_id = fields.Many2one('lerm.size.line',string="Size")
    grade_id = fields.Many2one('lerm.grade.line',string="Grade")
    received_by_id = fields.Many2one('res.partner',string="Received By")
    sample_received_date = fields.Date(string="Sample Received Date")
    sample_condition = fields.Selection([
        ('satisfactory', 'Satisfactory'),
        ('non_satisfactory', 'Non-Satisfactory'),
    ], string='Sample Condition', default='satisfactory')
    # technicians = fields.Many2one("res.users",string="Technicians")
    location = fields.Char(string="Location")
    sample_reject_reason = fields.Char(string="Sample Reject Reason")
    witness = fields.Char(string="Witness")
    scope = fields.Selection([
        ('nabl', 'NABL'),
        ('non_nabl', 'Non-NABL'),
    ], string='Scope', default='nabl')
    sample_description = fields.Text(string="Sample Description")
    group_ids = fields.Many2many('lerm_civil.group',string="Group Ids")
    material_ids = fields.Many2many('product.template',string="Material Ids")
    size_ids = fields.Many2many('lerm.size.line',string="Size Ids")
    grade_ids = fields.Many2many('lerm.grade.line',string="Grade Ids")
    qty_ids = fields.Many2many('lerm.qty.line',string="Qty Ids")
    days_casting = fields.Selection([
        ('3', '3 Days'),
        ('7', '7 Days'),
        ('14', '14 Days'),
        ('28', '28 Days'),
    ], string='Days of casting', default='3')
    customer_id = fields.Many2one('res.partner' , string="Customer")
    alias = fields.Char(string="Alias")
    parameters = fields.Many2many('lerm.parameter.master',string="Parameter")
    # parameters_ids = fields.Many2many('lerm.datasheet.line',string="Parameter" , compute="compute_param_ids")
    kes_range = fields.Char("KES Range",required=True,readonly=True, default=lambda self: 'New')
    casting_date = fields.Date(string="Casting Date")
    client_sample_id = fields.Char(string="Client Sample Id")
    
    status = fields.Selection([
        ('1-pending', 'Pending'),
        ('2-confirmed', 'Confirmed'),
    ], string='Status', default='1-pending')

    state = fields.Selection([
        ('1-allotment_pending', 'Assignment Pending'),
        ('2-alloted', 'Alloted'),
        ('3-in_report', 'In-Report'),
    ], string='State',default='1-allotment_pending')


    