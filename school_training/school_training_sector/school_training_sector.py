from openerp import _, models, fields


class SchoolTrainingSector(models.Model):
    """Training Sector"""

    _name = 'school.training.sector'
    _description = 'Training Sector'

    name = fields.Char(_('Name'), size=64, required=True)

    _order = 'name'
