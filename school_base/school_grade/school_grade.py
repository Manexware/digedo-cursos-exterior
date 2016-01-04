from openerp import _, models, fields,api

#----------------------------------------------------------
# 01.- Grade
#----------------------------------------------------------
class SchoolGrade(models.Model):
    """Grade"""

    _name = 'school.grade'
    _description = 'Grade'

    code = fields.Char(_('Code'), size=6, required=True)
    name = fields.Char(_('Name'), size=64, required=True)
    is_official = fields.Boolean(_('Is official'), help=_('Indicates if the marine is official'),default = False)


    _sql_constraints = [
        ('code_unq', 'unique(code)', _('Code must be unique'))
    ]

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        ids = False
        if len(name) == 4:
            ids = self.search([('code', 'ilike', name)] + args,
                    limit=limit)
        if not ids:
            ids = self.search([('name', operator, name)] + args,
                    limit=limit)
        return ids.name_get()

