from openerp import _, models, fields, api


class HrBaseSchool(models.Model):

    _name = 'hr.base.school'
    _description = 'School'

    abbreviation = fields.Char(_('Abbreviation'), size=32, required=True)
    name = fields.Char(_('Name'), size=128, required=True)

    _sql_constraints = [
        ('abbr_unq', 'unique(abbreviation)', _('Abbreviation must be unique')),
        ('name_unq', 'unique(name)', _('Name must be unique'))
    ]

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=50):
        args = args or []
        ids = self.search(['|', ('abbreviation', operator, name), ('name', operator, name)] + args, limit=limit)
        return ids.name_get()
