from openerp import _, models, fields

class SchoolTrainingCategory(models.Model):
    """Training Category"""

    _name = 'school.training.category'
    _description = 'Training Category'

    name = fields.Char(_('Name'), size=64, required=True)

    _order = 'name'