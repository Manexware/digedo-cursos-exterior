from openerp import _, models, fields, api
# from ..misc import MODALITY,TRAINING_STATES
# from dateutil.relativedelta import relativedelta
# from openerp.exceptions import ValidationError, Warning
import time


class SchoolTrainingNewsReport(models.Model):
    """News Report"""

    _name = 'school.training.news.report'
    _description = 'News Report'

    # def _is_approver(self, cr, uid, ids, field, arg, context=None):
    #     cr.execute("""SELECT 1
    #         FROM res_groups_users_rel gu JOIN res_groups g ON g.id = gu.gid
    #         WHERE uid = %s AND name ~ 'Training Manager'"""%(uid))
    #     flag = cr.fetchone()
    #     result = {}
    #     for id in ids:
    #         result[id] = (flag and flag[0] == 1) and 1 or 0
    #     return result

    @api.one
    def _is_approver(self):
        # users = []
        users = self.env['res.groups'].search([('id', '=', self.env.ref('school_training.administrator')[0].id),
                                               ('users', '=', self._uid)])
        self.is_approver = False
        if users:
            self.is_approver = True

    def _get_student(self):
        if not self.student_id:
            student_id = self.env['hr.employee'].search([('user_id', '=', self._uid)])
            return student_id.id

    name = fields.Text(_('Notes'), required=True, readonly=True, states={'draft': [('readonly', False)]})
    created_date = fields.Datetime(_('Novelty Date'), readonly=True, default=time.strftime('%Y-%m-%d %H:%M:%S'))
    student_id = fields.Many2one('hr.employee', _('Student'), default=_get_student, ondelete='restrict', readonly=True,
                                 store=True)
    training_id = fields.Many2one('school.training', string=_('Training'), ondelete='restrict', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('released', 'Released'),
        ('revised', 'Revised')
        ], _('State'), default='draft')
    is_approver = fields.Integer(compute='_is_approver', string=_('Is Approver'))

    # def search(self, cr, uid, domain, offset=0, limit=None, order=None, context=None, count=False):
    #     if uid == 1:
    #         return super(school_training_news_report, self).
    # search(cr, uid, domain, offset=offset, limit=limit, order=order, context=context, count=count)
    #     cr.execute("""SELECT 1
    #         FROM res_groups_users_rel gu JOIN res_groups g ON g.id = gu.gid
    #         WHERE uid = %s AND name ~ 'Training Manager'"""%(uid))
    #     flag = cr.fetchone()
    #     if not flag:
    #         cr.execute("""SELECT n.id
    #             FROM school_training_employee_rel t
    #             JOIN hr_employee e ON e.id = t.student_id
    #             JOIN resource_resource r ON r.id = e.resource_id
    #             JOIN school_training_news_report n ON n.student_id = t.student_id
    #             WHERE user_id = %s"""%(uid))
    #         result = cr.fetchall()
    #         ids = set()
    #         for r in result:
    #             ids.add(r[0])
    #         domain.append(('id','in',list(ids)))
    #     return super(school_training_news_report, self).search(cr, uid, domain, offset, limit, order, context, count)

    @api.one
    def release(self):
        self.state = 'released'

    @api.one
    def revise(self):
        self.state = 'revised'
