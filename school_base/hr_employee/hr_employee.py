# -*- coding: utf-8 -*-

from openerp import _, models, fields, api
from ..misc import BLOOD_TYPE
from openerp.exceptions import ValidationError


class SchoolPerson(models.Model):
    """Person"""

    @api.multi
    @api.depends('name', 'last_name', 'grade_id', 'specialty_id', 'title', 'suffix', 'status')
    def name_get(self):
        res = []
        for record in self:
            name = record.name
            if record.last_name:
                name = name + ' ' + record.last_name
            if record.status:
                if record.status == 'functionary':
                    if record.title:
                        name = record.title + ' ' + name
                    if record.suffix:
                        name = name + ', ' + record.suffix
                elif record.status == 'active' or record.status == 'passive':
                    if record.grade_id:
                        if record.status == 'passive':
                            name = record.grade_id.code + '(SP) ' + name
                        else:
                            if record.specialty_id:
                                name = record.grade_id.code + '-' + record.specialty_id.code + ' ' + name
                            else:
                                name = record.grade_id.code + ' ' + name
                    if record.suffix:
                        name = name + ', ' + record.suffix
                    elif record.title:
                        name = name + ', ' + record.title
            res.append((record.id, name))
        return res

    # @api.multi
    # @api.depends('name', 'last_name', 'grade_id', 'specialty_id', 'title', 'suffix', 'status')
    # def name_get(self):
    #     res = []
    #     name = self.name
    #     if self.last_name:
    #         name = name + ' ' + self.last_name
    #     if self.status:
    #         if self.status == 'functionary':
    #             if self.title:
    #                 name = self.title + ' ' + name
    #             if self.suffix:
    #                 name = name + ', ' + self.suffix
    #         elif (self.status == 'active' or self.status == 'passive'):
    #             if self.grade_id:
    #                 if self.status == 'passive':
    #                     name = self.grade_id.code + '(SP) ' + name
    #                 else:
    #                     if self.specialty_id:
    #                         name = self.grade_id.code + '-' + self.specialty_id.code + ' ' + name
    #                     else:
    #                         name = self.grade_id.code + ' ' + name
    #             if self.suffix:
    #                 name = name + ', ' + self.suffix
    #             elif self.title:
    #                 name = name + ', ' + self.title
    #     res.append((self.id,name))
    #     return res

    # def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
    #     res = self.name_get(cr, uid, ids, context=context)
    #     return dict(res)

    @api.one
    @api.depends('name', 'last_name', 'grade_id', 'specialty_id', 'title', 'suffix', 'status')
    def _name_get_fnc(self):
        self.full_name = self.name_get()[0][1]

    _inherit = 'hr.employee'

    title = fields.Char(_('Title'), size=16)
    last_name = fields.Char(_('Last Name'), size=32)
    grade_id = fields.Many2one('school.grade', _('Grade'))
    specialty_id = fields.Many2one('school.specialty', _('Specialty'))
    suffix = fields.Char(_('Suffix'), size=16, help=_('Masters degree, PhD'))
    status = fields.Selection([
            ('active', _('Active in Force')),
            ('passive', _('Passive in Force')),
            ('functionary', _('Public Functionary'))
        ], _('Status'), default='active')
    full_name = fields.Char(compute='_name_get_fnc', string='Name')
    # full_name = fields.Char(string='Name',store=True)
    blood_type = fields.Selection(BLOOD_TYPE, _('Blood Type'))
    admission_date = fields.Date(_('Admission Date'), help=_('(mm/dd/yyyy)'))
    last_ascent_date = fields.Date(_('Last Ascent Date'), help=_('(mm/dd/yyyy)'))
    height = fields.Float(_('Height'), help=_('In meters'))
    eye_color = fields.Char(_('Eye Color'), size=32)
    hair_color = fields.Char(_('Hair Color'), size=32)
    shirt_size = fields.Integer(_('Shirt Size'))
    pants_size = fields.Integer(_('Pants Size'))
    shoe_size = fields.Integer(_('Shoe Size'))
    cap_size = fields.Integer(_('Cap Size'))

    _sql_constraints = [
        ('id_unq', 'unique(identification_id)', _('ID must be unique'))
    ]

    @api.one
    @api.constrains('identification_id')
    def _check_id(self):
        if self.identification_id:
            if len(self.identification_id) != 10 or not self.identification_id.isdigit():
                raise ValidationError("ID is not valid")
            accum = 0
            for i in range(9):
                d = int(self.identification_id[i])
                if (i % 2) == 0:
                    accum += (d * 2) > 9 and (d * 2) - 9 or (d * 2)
                else:
                    accum += d
            last = int(self.identification_id[9])
            residue = (accum % 10)
            digit = residue > 0 and 10 - residue or 0
            if not digit == last:
                raise ValidationError("ID is not valid")

    # _constraints = [
    #     (_check_id, _('ID is not valid'), ['identification_id'])
    # ]

    _order = 'last_name'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        name_array = name.split(' ')
        if len(name_array) == 1:
            args += ['|', ('name', operator, name), ('last_name', operator, name)]
        if len(name_array) == 2:
            args += [('name', operator, name_array[0]), ('last_name', operator, name_array[1])]
        if len(name_array) == 3:
            args += [('name', operator, name_array[0]), ('last_name', operator, name_array[1]+' '+name_array[2])]
        ids = self.search(args, limit=limit)
        return ids.name_get()
