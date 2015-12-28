from openerp import _, models, fields

#----------------------------------------------------------
# 04.- Educational Institution
#----------------------------------------------------------
class school_training_educational_institution(models.Model):
    """Educational Institution"""

    _name = 'school.training.educational.institution'
    _description = 'Educational Institution'

    code = fields.Char(_('Code'), size=64, required=True)
    name = fields.Char(_('Name'), size=64, required=True)
    city_id = fields.Many2one('school.training.city', _('City'), ondelete='restrict')


    _sql_constraints = [
        ('code_unq', 'unique(code)', _('Code must be unique')),
        ('name_unq', 'unique(name)', _('Name must be unique'))
    ]