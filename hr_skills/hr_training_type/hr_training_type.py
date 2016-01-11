from openerp import _, models, fields


class HrTrainingType(models.Model):
    """"""

    _name = 'hr.training.type'
    _description = 'Type of Training'

    name = fields.Char(_('Name'), size=120, required=True)

    _sql_constraints = [
        ('name_unq', 'unique(name)', _('Name must be unique')),
    ]
