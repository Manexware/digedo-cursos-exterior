from openerp import _, models, fields, api


class SchoolSpecialty(models.Model):
    """Specialty"""

    _name = 'school.specialty'
    _description = 'Specialty'

    code = fields.Char(_('Code'), size=4, required=True)
    name = fields.Char(_('Name'), size=64, required=True)

    _sql_constraints = [
        ('code_unq', 'unique(code)', _('Code must be unique')),
        ('name_unq', 'unique(name)', _('Name must be unique'))
    ]

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        ids = False
        if len(name) == 2:
            ids = self.search([('code', 'ilike', name)] + args,
                              limit=limit,)
        if not ids:
            ids = self.search([('name', operator, name)] + args,
                              limit=limit)
        return ids.name_get()
