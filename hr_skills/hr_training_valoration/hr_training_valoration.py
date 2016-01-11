from openerp import _, models, fields, api


class HrTrainingValoration(models.Model):
    """"""

    _name = 'hr.training.valoration'
    _description = 'Valoration'

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            name = '%s (%.2f)' % (record.name, record.score)
            res.append((record.id, name))
        return res

    name = fields.Char(_('Name'), size=120, required=True)
    score = fields.Float(_('Score'), digits=(1, 2), required=True, default=0)
    note = fields.Text(_('Note'))
    type_id = fields.Many2one('hr.training.type', _('Type'), required=True, ondelete='restrict')

    _sql_constraints = [
        ('name_unq', 'unique(name)', _('Name must be unique')),
        ('score_chk', 'check(score > 0)', _('Score must be greater than 0')),
    ]
