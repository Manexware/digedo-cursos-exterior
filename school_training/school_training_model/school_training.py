from openerp import _, models, fields, api
from ..misc import MODALITY, TRAINING_STATES
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError, Warning


class SchoolTraining(models.Model):
    """Training"""

    _name = 'school.training'
    _description = 'Training'

    # def name_get(self, cr, uid, ids, context=None):
    #     t_ids = self.search(cr, uid, [], context=context)
    #     return super(school_training, self).name_get(cr, uid, t_ids, context=context)

    # @api.multi
    # @api.depends('name', 'last_name', 'grade_id', 'specialty_id', 'title', 'suffix', 'status')
    # def name_get(self, cr, uid, ids, context=None):
    #     t_ids = self.search(cr, uid, [], context=context)
    #     return super(school_training, self).name_get(cr, uid, t_ids, context=context)

    @api.one
    @api.constrains('end_date', 'start_date')
    def _check_end_date(self):
        if self.start_date and self.end_date:
            start_date = fields.Datetime.from_string(self.start_date)
            end_date = fields.Datetime.from_string(self.end_date)
            if end_date < start_date:
                end_date = start_date + relativedelta(months=+ 3)
                self.end_date = end_date
                raise Warning("La fecha de fin de curso tiene que ser mayor a la fecha de inicio")
        else:
            raise ValidationError("Seleccione las fecha de inicio y fin de curso")

    # def _compute_duration(self, cr, uid, ids, field, arg, context=None):
    #     if not ids:
    #         return {}
    #     sql = """SELECT id, age(end_date, start_date)::varchar
    #     FROM school_training
    #     WHERE id IN %s"""
    #     cr.execute(sql, (tuple(ids),))
    #     return dict(cr.fetchall())

    @api.one
    @api.depends('start_date', 'end_date')
    def _compute_duration(self):
        if self.start_date and self.end_date:
            start_date = fields.Date.from_string(self.start_date)
            end_date = fields.Date.from_string(self.end_date)
            rdelta = relativedelta(end_date, start_date)
            self.duration = '%s Years %s Months %s Days' % (rdelta.years, rdelta.months, rdelta.days)

    # def _compute_count(self, cr, uid, ids, field, arg, context=None):
    #     cr.execute('SELECT training_id, count(*) \
    #         FROM school_training_employee_rel \
    #         WHERE training_id IN %(ids)s \
    #         GROUP BY training_id', {'ids': tuple(ids)})
    #     result = dict(cr.fetchall())
    #     for id in ids:
    #         result[id] = result.get(id, 0)
    #     return result

    @api.one
    @api.depends('student_ids')
    def _compute_count(self):
        if self.student_ids:
            self.student_count = len(self.student_ids)

    name = fields.Char(_('Name'), size=96, required=True,
                       readonly=True, states={'not executed': [('readonly', False)]})
    sector_id = fields.Many2one('school.training.sector', _('Sector'), ondelete='restrict',
                                readonly=True, states={'not executed': [('readonly', False)]})
    category_id = fields.Many2one('school.training.category', _('Category'), ondelete='restrict',
                                  readonly=True, states={'not executed': [('readonly', False)]})
    country_id = fields.Many2one('res.country', _('Country'), ondelete='set null',
                                 readonly=True, states={'not executed': [('readonly', False)]})
    edu_inst_id = fields.Many2one('school.training.educational.institution', _('Educational Institution'),
                                  ondelete='restrict', readonly=True, states={'not executed': [('readonly', False)]})
    modality = fields.Selection(MODALITY, _('Modality of Study'), default='modality')
    year = fields.Integer(_('Year'), required=True,
                          readonly=True, states={'not executed': [('readonly', False)]})
    grade_id = fields.Many2one('school.grade', _('Grade'), ondelete='restrict',
                               readonly=True, states={'not executed': [('readonly', False)]})
    specialty_id = fields.Many2one('school.specialty', _('Specialty'), ondelete='set null',
                                   readonly=True, states={'not executed': [('readonly', False)]})
    quota = fields.Integer(_('Quota'),
                           readonly=True, states={'not executed': [('readonly', False)]})
    start_date = fields.Date(_('Start Date'), help=_('(mm/dd/yyyy)'),
                             readonly=True, states={'not executed': [('readonly', False)]})
    end_date = fields.Date(_('End Date'), help=_('(mm/dd/yyyy)'),
                           readonly=True, states={'not executed': [('readonly', False)]})
    duration = fields.Char(compute='_compute_duration', string=_('Duration'))
    note = fields.Text('Notes', translate=True)
    state = fields.Selection(TRAINING_STATES, _('State'), default='not executed')
    student_ids = fields.Many2many('hr.employee', 'school_training_employee_rel', 'training_id',
                                   'student_id', _('Students'), readonly=True,
                                   states={'not executed': [('readonly', False)]})
    student_count = fields.Integer(compute='_compute_count', string=_('No of Students'))
    financial_detail_ids = fields.One2many('school.training.financial.detail', 'training_id', _('Financial Details'),
                                           readonly=True, states={'not executed': [('readonly', False)]})

    @api.one
    def suspend(self):
        self.state = 'suspend'

    @api.one
    def by_running(self):
        self.state = 'by running'

    @api.one
    def canceled(self):
        self.state = 'canceled'

    @api.one
    def running(self):
        self.state = 'running'

    @api.one
    def executed(self):
        self.state = 'executed'

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if self._uid == 1:
            return super(SchoolTraining, self).search(args, offset=offset, limit=limit, order=order, count=count)
        self.env.cr.execute("""SELECT 1
            FROM res_groups_users_rel gu JOIN res_groups g ON g.id = gu.gid
            WHERE uid = %s AND name ~ 'Training Manager'""" % (self._uid))
        flag = self.env.cr.fetchone()
        if not flag:
            self.env.cr.execute("""SELECT n.id
                FROM school_training_employee_rel t
                JOIN hr_employee e ON e.id = t.student_id
                JOIN resource_resource r ON r.id = e.resource_id
                JOIN school_training n ON n.id = t.training_id
                WHERE user_id = %s""" % (self._uid))
            result = self.env.cr.fetchall()
            ids = set()
            for r in result:
                ids.add(r[0])
            args.append(('id','in',list(ids)))
        return super(SchoolTraining, self).search(args, offset, limit, order, count=False)

    # def search(self, cr, uid, domain, offset=0, limit=None, order=None, context=None, count=False):
        # if uid == 1:
        # 	return super(school_training, self).search(cr, uid, domain, offset=offset, limit=limit, order=order, context=context, count=count)
        # cr.execute("""SELECT 1
        #     FROM res_groups_users_rel gu JOIN res_groups g ON g.id = gu.gid
        #     WHERE uid = %s AND name ~ 'Training Manager'"""%(uid))
        # flag = cr.fetchone()
        # if not flag:
        # 	cr.execute("""SELECT n.id
        # 		FROM school_training_employee_rel t
        # 		JOIN hr_employee e ON e.id = t.student_id
        # 		JOIN resource_resource r ON r.id = e.resource_id
        # 		JOIN school_training n ON n.id = t.training_id
        # 		WHERE user_id = %s"""%(uid))
        # 	result = cr.fetchall()
        # 	ids = set()
        # 	for r in result:
        # 		ids.add(r[0])
        # 	domain.append(('id','in',list(ids)))
        # return super(school_training, self).search(cr, uid, domain, offset, limit, order, context, count)
