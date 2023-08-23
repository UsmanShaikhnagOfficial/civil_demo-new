from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError
import math


class SteelTmtBarLine(models.Model):
    _name = "steel.tmt.bar"
    _inherit = "lerm.eln"
   
    
    Id_no = fields.Char("ID No")
    grade = fields.Many2one('lerm.grade.line',string="Grade",compute="_compute_grade_id",store=True)
    size = fields.Many2one('lerm.size.line',string="Size",compute="_compute_size_id",store=True)
    diameter = fields.Integer(string="Dia. in mm")
    lentgh = fields.Float(string="Length in mm",digits=(10, 3))
    weight = fields.Float(string="Weight, in kg",digits=(10, 3))
    weight_per_meter = fields.Float(string="Weight per meter, kg/m",compute="_compute_weight_per_meter",store=True)
    crossectional_area = fields.Float(string="Cross sectional Area, mm²",compute="_compute_crossectional_area",store=True)
    gauge_length = fields.Integer(string="Gauge Length mm",compute="_compute_gauge_length",store=True)
    elongated_gauge_length = fields.Float(string="Elongated Gauge Length, mm")
    percent_elongation = fields.Float(string="% Elongation",compute="_compute_elongation_percent",store=True)
    yeild_load = fields.Float(string="Yield Load  KN")
    ultimate_load = fields.Float(string="Ultimate Load, Kn")
    proof_yeid_stress = fields.Float(string="0.2% Proof Stress / Yield Stress N/mm2",compute="_compute_proof_yeid_stress",store=True)
    ult_tens_strgth = fields.Float(string="Ultimate Tensile Strength, N/mm2",compute="_compute_ult_tens_strgth",store=True)
    fracture = fields.Char("Fracture (Within Gauge Length)",default="W.G.L")
    eln_ref = fields.Many2one('lerm.eln',string="ELN")
    ts_ys_ratio = fields.Float(string="TS/YS Ratio",compute="_compute_ts_ys_ratio",store=True)
    weight_per_meter = fields.Float(string="Weight per meter",compute="_compute_weight_per_meter",store=True)
    variation = fields.Float(string="Variation")

    requirement_utl = fields.Float(string="Requirement",compute="_compute_requirement_utl",store=True)
    requirement_yield = fields.Float(string="Requirement",compute="_compute_requirement_yield",store=True)
    requirement_ts_ys = fields.Float(string="Requirement",compute="_compute_requirement_ts_ys",store=True)
    requirement_elongation = fields.Float(string="Requirement",compute="_compute_requirement_elongation",store=True)
    requirement_weight_per_meter = fields.Float(string="Requirement",compute="_compute_requirement_weight_per_meter",digits=(16, 4),store=True)


    
    bend_test = fields.Selection([
        ('satisfactory', 'Satisfactory'),
        ('non-satisfactory', 'Non-Satisfactory')],"Bend Test",store=True)
    
    re_bend_test = fields.Selection([
        ('satisfactory', 'Satisfactory'),
        ('non-satisfactory', 'Non-Satisfactory')],"Re-Bend Test",store=True)


    uts_nabl = fields.Selection([
        ('pass', 'Pass'),
        ('fail', 'Fail')],string="NABL",compute="_compute_uts_nabl",store=True)

    yield_nabl = fields.Selection([
        ('pass', 'Pass'),
        ('fail', 'Fail')],string="NABL",compute="_compute_yield_nabl",store=True)

    elongation_nabl = fields.Selection([
        ('pass', 'Pass'),
        ('fail', 'Fail')],string="NABL",compute="_compute_elongation_nabl",store=True)

    ts_ys_nabl = fields.Selection([
        ('pass', 'Pass'),
        ('fail', 'Fail')],string="NABL",compute="_compute_ts_ys_nabl",store=True)

    weight_per_meter_nabl = fields.Selection([
        ('pass', 'Pass'),
        ('fail', 'Fail')],string="NABL",compute="_compute_weight_per_meter_nabl",store=True)


    @api.depends('weight','lentgh')
    def _compute_weight_per_meter(self):
        for record in self:
            if record.lentgh != 0:   
                record.weight_per_meter =  record.weight/record.lentgh
            else:
                record.weight_per_meter = 0

    @api.depends('weight_per_meter','eln_ref','size')
    def _compute_weight_per_meter_nabl(self):
        for record in self:
            # print("Steel Size",record.size)
            record.weight_per_meter_nabl = 'fail'
            line = self.env['lerm.parameter.master'].search([('parameter_name','=','Weight per Meter (TMT Steel)')])
            materials = self.env['lerm.parameter.master'].search([('parameter_name','=','Weight per Meter (TMT Steel)')]).parameter_table
            for material in materials:
                # print("Materials size",material.size.id)
                if material.size.id == record.size.id:
                    req_min = material.req_min
                    req_max = material.req_max
                    mu_value = line.mu_value
                    
                    lower = record.weight_per_meter - record.weight_per_meter*mu_value
                    upper = record.weight_per_meter + record.weight_per_meter*mu_value
                    
                    if lower >= req_min and upper <= req_max:
                        record.weight_per_meter_nabl = 'pass'
                        break
                    else:
                        record.weight_per_meter_nabl = 'fail'

    @api.depends('eln_ref','size')
    def _compute_requirement_weight_per_meter(self):
        for record in self:
            # record.requirement_yield = 0
            # line = self.env['eln.parameters.result'].search([('eln_id','=',record.eln_ref.id),('parameter.parameter_name','=','Yield Stress (TMT)')]).parameter
            # materials = self.env['lerm.parameter.master'].search([('id','=',line.id)]).parameter_table
            materials = self.env['lerm.parameter.master'].search([('parameter_name','=','Weight per Meter (TMT Steel)')]).parameter_table
            for material in materials:
                if material.size.id == record.size.id:
                    req_min = material.req_min
                    record.requirement_weight_per_meter = req_min
                    break
                else:
                    record.requirement_weight_per_meter = 0

    @api.depends('ult_tens_strgth','proof_yeid_stress')
    def _compute_ts_ys_ratio(self):
        for record in self:
            if record.proof_yeid_stress != 0:
                record.ts_ys_ratio = record.ult_tens_strgth / record.proof_yeid_stress
            else:
                record.ts_ys_ratio = 0


    @api.depends('ult_tens_strgth','eln_ref','grade')
    def _compute_uts_nabl(self):
        for record in self:
            
            # line = self.env['eln.parameters.result'].search([('eln_id','=',record.eln_ref.id),('parameter.parameter_name','=','Ultimate tensile Strength (TMT Steel)')]).parameter
            line = self.env['lerm.parameter.master'].search([('parameter_name','=','Ultimate tensile Strength (TMT Steel)')])
            materials = self.env['lerm.parameter.master'].search([('id','=',line.id)]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    req_min = material.req_min
                    lab_max = line.lab_max_value
                    mu_value = line.mu_value
                    lower = record.ult_tens_strgth - record.ult_tens_strgth*mu_value
                    upper = record.ult_tens_strgth + record.ult_tens_strgth*mu_value
                    if lower >= req_min and upper <= lab_max:
                        record.uts_nabl = 'pass'
                        break
                    else:
                        record.uts_nabl = 'fail'

    @api.depends('eln_ref','grade')
    def _compute_requirement_utl(self):
        for record in self:
            # record.requirement_utl = 0
            # line = self.env['eln.parameters.result'].search([('eln_id','=',record.eln_ref.id),('parameter.parameter_name','=','Ultimate tensile Strength (TMT Steel)')]).parameter
            # materials = self.env['lerm.parameter.master'].search([('id','=',line.id)]).parameter_table
            # for material in materials:
            #     if material.grade.id == record.grade.id:
            #         req_min = material.req_min
            #         print("REQ_MIN",req_min)
            #         record.requirement_utl = req_min
            #     else:
            #         record.requirement_utl = 0
            materials = self.env['lerm.parameter.master'].search([('parameter_name','=','Ultimate tensile Strength (TMT Steel)')]).parameter_table
            print("sadsdsadsdasdasdsadadsdsds",materials)
            for material in materials:
                if material.grade.id == record.grade.id:
                    req_min = material.req_min
                    record.requirement_utl = req_min
                    break
                else:
                    record.requirement_utl = 0
                    


    @api.depends('percent_elongation','eln_ref','grade')
    def _compute_elongation_nabl(self):
        for record in self:
            record.elongation_nabl = 'fail'
            # line = self.env['eln.parameters.result'].search([('eln_id','=',record.eln_ref.id),('parameter.parameter_name','=','% Elongation (TMT)')]).parameter
            # materials = self.env['lerm.parameter.master'].search([('id','=',line.id)]).parameter_table
            line = self.env['lerm.parameter.master'].search([('parameter_name','=','% Elongation (TMT)')])
            materials = self.env['lerm.parameter.master'].search([('parameter_name','=','% Elongation (TMT)')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    req_min = material.req_min
                    lab_max = line.lab_max_value
                    mu_value = line.mu_value
                    lower = record.percent_elongation - record.percent_elongation*mu_value
                    upper = record.percent_elongation + record.percent_elongation*mu_value
                    if lower >= req_min and upper <= lab_max:
                        record.elongation_nabl = 'pass'
                        break
                    else:
                        record.elongation_nabl = 'fail'

    @api.depends('eln_ref','grade')
    def _compute_requirement_elongation(self):
        for record in self:
            # record.requirement_elongation = 0
            # line = self.env['eln.parameters.result'].search([('eln_id','=',record.eln_ref.id),('parameter.parameter_name','=','% Elongation (TMT)')]).parameter
            # materials = self.env['lerm.parameter.master'].search([('id','=',line.id)]).parameter_table
            materials = self.env['lerm.parameter.master'].search([('parameter_name','=','% Elongation (TMT)')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    req_min = material.req_min
                    record.requirement_elongation = req_min
                    break
                else:
                    record.requirement_elongation = 0


    @api.depends('proof_yeid_stress','eln_ref','grade')
    def _compute_yield_nabl(self):
        for record in self:
            record.yield_nabl = 'fail'
            # line = self.env['eln.parameters.result'].search([('eln_id','=',record.eln_ref.id),('parameter.parameter_name','=','Yield Stress (TMT)')]).parameter
            # materials = self.env['lerm.parameter.master'].search([('id','=',line.id)]).parameter_table
            line = self.env['lerm.parameter.master'].search([('parameter_name','=','Yield Stress (TMT)')])
            materials = self.env['lerm.parameter.master'].search([('parameter_name','=','Yield Stress (TMT)')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    req_min = material.req_min
                    lab_max = line.lab_max_value
                    mu_value = line.mu_value
                    lower = record.proof_yeid_stress - record.proof_yeid_stress*mu_value
                    upper = record.proof_yeid_stress + record.proof_yeid_stress*mu_value
                    if lower >= req_min and upper <= lab_max:
                        record.yield_nabl = 'pass'
                        break
                    else:
                        record.yield_nabl = 'fail'

    @api.depends('eln_ref','grade')
    def _compute_requirement_yield(self):
        for record in self:
            print("Saifsdadddddddddd")
            # record.requirement_yield = 0
            # line = self.env['eln.parameters.result'].search([('eln_id','=',record.eln_ref.id),('parameter.parameter_name','=','Yield Stress (TMT)')]).parameter
            # materials = self.env['lerm.parameter.master'].search([('id','=',line.id)]).parameter_table
            materials = self.env['lerm.parameter.master'].search([('parameter_name','=','Yield Stress (TMT)')]).parameter_table
            
            for material in materials:
                print("DATA ", material)
                if material.grade.id == record.grade.id:
                    req_min = material.req_min
                    record.requirement_yield = req_min
                    break
                else:
                    record.requirement_yield = 0
        
    @api.depends('ts_ys_ratio','eln_ref','grade')
    def _compute_ts_ys_nabl(self):
        for record in self:
            record.ts_ys_nabl = 'fail'
            line = self.env['lerm.parameter.master'].search([('parameter_name','=','TS / YS Ratio (TMT)')])
            materials = self.env['lerm.parameter.master'].search([('parameter_name','=','TS / YS Ratio (TMT)')]).parameter_table
            for material in materials:
                    req_min = material.req_min
                    lab_max = line.lab_max_value
                    mu_value = line.mu_value
                    lower = record.ts_ys_ratio - record.ts_ys_ratio*mu_value
                    upper = record.ts_ys_ratio + record.ts_ys_ratio*mu_value
                    if lower >= req_min:
                        record.ts_ys_nabl = 'pass'
                        break
                    else:
                        record.ts_ys_nabl = 'fail'

    @api.depends('eln_ref','grade')
    def _compute_requirement_ts_ys(self):
        for record in self:
            # record.requirement_yield = 0
            # line = self.env['eln.parameters.result'].search([('eln_id','=',record.eln_ref.id),('parameter.parameter_name','=','Yield Stress (TMT)')]).parameter
            # materials = self.env['lerm.parameter.master'].search([('id','=',line.id)]).parameter_table
            materials = self.env['lerm.parameter.master'].search([('parameter_name','=','TS / YS Ratio (TMT)')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    req_min = material.req_min
                    record.requirement_ts_ys = req_min
                    break
                else:
                    record.requirement_ts_ys = 0
        


    @api.depends('weight', 'lentgh')
    def _compute_weight_per_meter(self):
        for record in self:
            if record.lentgh != 0:
                record.weight_per_meter = record.weight / record.lentgh
            else:
                record.weight_per_meter = 0.0

    @api.depends('weight', 'lentgh')
    def _compute_crossectional_area(self):
        for record in self:
            if record.lentgh != 0:
                # print(record.weight / (0.00785 * record.lentgh))
                record.crossectional_area = round((record.weight / (0.00785 * record.lentgh)),2)
                
            else:
                record.crossectional_area = 0.0

    @api.depends('crossectional_area')
    def _compute_gauge_length(self):
        for record in self:
            record.gauge_length = round(5.65 * math.sqrt(record.crossectional_area))


    @api.depends('yeild_load','crossectional_area')
    def _compute_proof_yeid_stress(self):
        for record in self:
            if record.crossectional_area != 0:
                record.proof_yeid_stress = record.yeild_load / record.crossectional_area * 1000
            else:
                record.proof_yeid_stress = 0.0

    @api.depends('ultimate_load')
    def _compute_ult_tens_strgth(self):
        for record in self:
            if record.crossectional_area != 0:
                record.ult_tens_strgth = record.ultimate_load / record.crossectional_area * 1000
            else:
                record.ult_tens_strgth = 0.0


    @api.depends('gauge_length','elongated_gauge_length')
    def _compute_elongation_percent(self):
        for record in self:
            if record.gauge_length != 0:
                record.percent_elongation = ((record.elongated_gauge_length - record.gauge_length)/record.gauge_length)*100
            else:
                record.percent_elongation = 0


    @api.model
    def create(self, vals):
        # import wdb;wdb.set_trace()
        record = super(SteelTmtBarLine, self).create(vals)
        # record.get_all_fields()
        record.eln_ref.write({'model_id':record.id})
        return record


    @api.depends('eln_ref')
    def _compute_grade_id(self):
        if self.eln_ref:
            self.grade = self.eln_ref.grade_id.id
    

    @api.depends('eln_ref')
    def _compute_size_id(self):
        if self.eln_ref:
            self.size = self.eln_ref.size_id.id

    


  
          