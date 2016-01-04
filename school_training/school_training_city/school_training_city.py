from openerp import _, models, fields


class SchoolTrainingCity(models.Model):
    """City"""

    _name = 'school.training.city'
    _description = 'City'

    name = fields.Char(_('Name'), size=64, required=True)
    state_id = fields.Many2one('res.country.state', _('Province'), ondelete='set null')
    country = fields.Many2one('res.country', related='state_id.country_id', string=_('Country'), readonly=True)

    _sql_constraints = [
        ('name_unq', 'unique(name, state_id)', _('Name must be unique'))
    ]
