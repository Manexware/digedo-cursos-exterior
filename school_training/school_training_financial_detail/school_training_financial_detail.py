from openerp import _, models, fields,api

#----------------------------------------------------------
# 06.- Training Financial Detail
#----------------------------------------------------------
class SchoolTrainingFinancialDetail(models.Model):
    """Training Financial Detail"""


    # def name_get(self, cr, uid, ids, context=None):
    #     if not ids:
    #         return []
    #     reads = self.read(cr, uid, ids, ['concept_id'], context=context)
    #     res = []
    #     for record in reads:
    #         res.append((record['id'], record['concept_id']))
    #     return res

    @api.multi
    def name_get(self):
        if not self.ids:
            return []
        res = []
        for record in self:
            res.append((record.id, record.concept_id))
        return res

    _name = 'school.training.financial.detail'
    _description = 'Training Financial Detail'

    concept_id = fields.Many2one('school.training.financial.concept', _('Concept'), required=True)
    amount = fields.Float(_('Amount'), digits=(9,2))
    training_id = fields.Many2one('school.training', _('Training'))


    _sql_constraints = [
        ('concept_unq', 'unique(training_id, concept_id)', _('Concept must be unique'))
    ]