from openerp import _, models, fields


class SchoolTrainingFinancialConcept(models.Model):
    """Financial Concept"""

    _name = 'school.training.financial.concept'
    _description = 'Financial Concept'

    name = fields.Char(_('Name'), size=64, required=True)
    property_account_expense = fields.Many2one(
        'account.account.type',
        string=_('Account Expense'),
        domain="[('type', '=', 'other')]",
        help=_('This account will be used instead of the default one as the expense account for the current concept'),
        required=True,
        company_dependent=True,)
