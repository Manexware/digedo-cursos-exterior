from osv import osv, fields
from datetime import datetime, date
import time
from tools.translate import _

TRAINING_STATES = [
	('not executed', _('Not Executed')),
	('suspend', _('Suspend')),
	('by running', _('By Running')),
	('canceled', _('Canceled')),
	('running', _('Running')),
	('executed', _('Executed'))
]

MODALITY = [
	('modality', _('Modality')),
	('blended', _('Blended Learning')),
	('open', _('Open and Distance'))
]

#----------------------------------------------------------
# 01.- Training Category
#----------------------------------------------------------
class school_training_category(osv.osv):
    """Training Category"""

    _name = 'school.training.category'
    _description = 'Training Category'
    
    _columns = {
        'name': fields.char(_('Name'), size=64, required=True),
    }

    _order = 'name'
    
school_training_category()

#----------------------------------------------------------
# 02.- Training Sector
#----------------------------------------------------------
class school_training_sector(osv.osv):
    """Training Sector"""
    
    _name = 'school.training.sector'
    _description = 'Training Sector'
    
    _columns = {
        'name': fields.char(_('Name'), size=64, required=True),
    }
    
    _order = 'name'

school_training_sector()

#----------------------------------------------------------
# 03.- City
#----------------------------------------------------------
class school_training_city(osv.osv):
	"""City"""

	_name = 'school.training.city'
	_description = 'City'

	_columns = {
		'name': fields.char(_('Name'), size=64, required=True),
		'state_id': fields.many2one('res.country.state', _('Province'), ondelete='set null'),
		'country': fields.related('state_id', 'country_id', type='many2one', relation='res.country', 
			string=_('Country'), readonly=True),
	}

	_sql_constraints = [
        ('name_unq', 'unique(name, state_id)', _('Name must be unique'))
    ]
	
school_training_city()

#----------------------------------------------------------
# 04.- Educational Institution
#----------------------------------------------------------
class school_training_educational_institution(osv.osv):
	"""Educational Institution"""

	_name = 'school.training.educational.institution'
	_description = 'Educational Institution'

	_columns = {
		'code': fields.char(_('Code'), size=64, required=True),
		'name': fields.char(_('Name'), size=64, required=True),
		'city_id': fields.many2one('school.training.city', _('City'), ondelete='restrict'),
	}

	_sql_constraints = [
		('code_unq', 'unique(code)', _('Code must be unique')),
        ('name_unq', 'unique(name)', _('Name must be unique'))
    ]

school_training_educational_institution()

#----------------------------------------------------------
# 05.- Financial Concept
#----------------------------------------------------------
class school_training_financial_concept(osv.osv):
    """Financial Concept"""
    
    _name = 'school.training.financial.concept'
    _description = 'Financial Concept'

    _columns = {
        'name': fields.char(_('Name'), size=64, required=True),
        'property_account_expense': fields.property(
            'account.account',
            type='many2one',
            relation='account.account',
            string=_('Account Expense'),
            view_load=True,
            domain="[('type', '=', 'other')]",
            help=_('This account will be used instead of the default one as the expense account for the current concept'),
            required=True),
    }

school_training_financial_concept()

#----------------------------------------------------------
# 06.- Training Financial Detail
#----------------------------------------------------------
class school_training_financial_detail(osv.osv):
	"""Training Financial Detail"""

	def name_get(self, cr, uid, ids, context=None):
		if not ids:
			return []
		reads = self.read(cr, uid, ids, ['concept_id'], context=context)
		res = []
		for record in reads:
			res.append((record['id'], record['concept_id']))
		return res

	_name = 'school.training.financial.detail'
	_description = 'Training Financial Detail'

	_columns = {
        'concept_id': fields.many2one('school.training.financial.concept', _('Concept'), required=True),
        'amount': fields.float(_('Amount'), digits=(9,2)),
        'training_id': fields.many2one('school.training', _('Training')),
    }

	_sql_constraints = [
        ('concept_unq', 'unique(training_id, concept_id)', _('Concept must be unique'))
    ]

school_training_financial_detail()

#----------------------------------------------------------
# 07.- Training
#----------------------------------------------------------
class school_training(osv.osv):
	"""Training"""

	_name = 'school.training'
	_description = 'Training'

	def name_get(self, cr, uid, ids, context=None):
		t_ids = self.search(cr, uid, [], context=context)
		return super(school_training, self).name_get(cr, uid, t_ids, context=context)

	def _compute_duration(self, cr, uid, ids, field, arg, context=None):
		if not ids:
			return {}
		sql = """SELECT id, age(end_date, start_date)::varchar 
		FROM school_training
		WHERE id IN %s"""
		cr.execute(sql, (tuple(ids),))
		return dict(cr.fetchall())

	def _compute_count(self, cr, uid, ids, field, arg, context=None):
		cr.execute('SELECT training_id, count(*) \
			FROM school_training_employee_rel \
			WHERE training_id IN %(ids)s \
			GROUP BY training_id', {'ids': tuple(ids)})
		result = dict(cr.fetchall())
		for id in ids:
			result[id] = result.get(id, 0)
		return result

	_columns = {
		'name': fields.char(_('Name'), size=96, required=True, 
			readonly=True, states={'not executed':[('readonly',False)]}),
		'sector_id': fields.many2one('school.training.sector', _('Sector'), ondelete='restrict', 
			readonly=True, states={'not executed':[('readonly',False)]}),
		'category_id': fields.many2one('school.training.category', _('Category'), ondelete='restrict', 
			readonly=True, states={'not executed':[('readonly',False)]}),
    	'country_id': fields.many2one('res.country', _('Country'), ondelete='set null', 
			readonly=True, states={'not executed':[('readonly',False)]}),
    	'edu_inst_id': fields.many2one('school.training.educational.institution', _('Educational Institution'), ondelete='restrict',
    		readonly=True, states={'not executed':[('readonly',False)]}),
    	'modality': fields.selection(MODALITY, _('Modality of Study')),
    	'year': fields.integer(_('Year'), required=True, 
			readonly=True, states={'not executed':[('readonly',False)]}),
        'grade_id': fields.many2one('school.grade', _('Grade'), ondelete='restrict', 
			readonly=True, states={'not executed':[('readonly',False)]}),
        'specialty_id': fields.many2one('school.specialty', _('Specialty'), ondelete='set null', 
			readonly=True, states={'not executed':[('readonly',False)]}),
        'quota': fields.integer(_('Quota'), 
			readonly=True, states={'not executed':[('readonly',False)]}),
        'start_date': fields.date(_('Start Date'), help=_('(mm/dd/yyyy)'), 
			readonly=True, states={'not executed':[('readonly',False)]}),
        'end_date': fields.date(_('End Date'), help=_('(mm/dd/yyyy)'), 
			readonly=True, states={'not executed':[('readonly',False)]}),
        'duration': fields.function(_compute_duration, string=_('Duration'), type='char'),
        'note': fields.text('Notes', translate=True),
        'state': fields.selection(TRAINING_STATES, _('State')),
        'student_ids': fields.many2many('hr.employee', 'school_training_employee_rel', 'training_id', 'student_id', _('Students'), 
			readonly=True, states={'not executed':[('readonly',False)]}),
        'student_count': fields.function(_compute_count, string=_('No of Students'), type='integer'),
        'financial_detail_ids': fields.one2many('school.training.financial.detail', 'training_id', _('Financial Details'), 
			readonly=True, states={'not executed':[('readonly',False)]}),
	}

	_defaults = {
		'state': lambda *args: 'not executed',
		'modality': lambda *args: 'modality',
	}

	def search(self, cr, uid, domain, offset=0, limit=None, order=None, context=None, count=False):
		if uid == 1:
			return super(school_training, self).search(cr, uid, domain, offset=offset, limit=limit, order=order, context=context, count=count)
		cr.execute("""SELECT 1 
		    FROM res_groups_users_rel gu JOIN res_groups g ON g.id = gu.gid
		    WHERE uid = %s AND name ~ 'Training Manager'"""%(uid))
		flag = cr.fetchone()
		if not flag:
			cr.execute("""SELECT n.id
				FROM school_training_employee_rel t
				JOIN hr_employee e ON e.id = t.student_id
				JOIN resource_resource r ON r.id = e.resource_id
				JOIN school_training n ON n.id = t.training_id
				WHERE user_id = %s"""%(uid))
			result = cr.fetchall()
			ids = set()
			for r in result:
				ids.add(r[0])
			domain.append(('id','in',list(ids)))
		return super(school_training, self).search(cr, uid, domain, offset, limit, order, context, count)
	
	def suspend(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, { 'state': 'suspend' })
		return True

	def by_running(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, { 'state': 'by running' })
		return True

	def canceled(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, { 'state': 'canceled' })
		return True

	def running(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, { 'state': 'running' })
		return True

	def executed(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, { 'state': 'executed' })
		return True

school_training()

#----------------------------------------------------------
# 08.- News Report
#----------------------------------------------------------
class school_training_news_report(osv.osv):
	"""News Report"""

	_name = 'school.training.news.report'
	_description = 'News Report'

	def _is_approver(self, cr, uid, ids, field, arg, context=None):
		cr.execute("""SELECT 1 
			FROM res_groups_users_rel gu JOIN res_groups g ON g.id = gu.gid 
			WHERE uid = %s AND name ~ 'Training Manager'"""%(uid))
		flag = cr.fetchone()
		result = {}
		for id in ids:
			result[id] = (flag and flag[0] == 1) and 1 or 0
		return result

	def _get_student(self, cr, uid, ids, context=None):
		cr.execute('SELECT e.id \
			FROM hr_employee e JOIN resource_resource r ON r.id = e.resource_id \
			WHERE user_id = %s'%(ids))
		result = cr.fetchone()
		return result
	
	_columns = {
		'name': fields.text(_('Notes'), required=True, readonly=True, 
			states={'draft':[('readonly',False)]}),
		'created_date': fields.datetime(_('Novelty Date'), readonly=True),
		'student_id': fields.many2one('hr.employee', _('Student'), ondelete='restrict', readonly=True),
		'training_id': fields.many2one('school.training', string=_('Training'), ondelete='restrict', required=True),
		'state': fields.selection(
			[
			('draft', 'Draft'), 
			('released', 'Released'),
			('revised', 'Revised')
			], _('State')),
		'is_approver': fields.function(_is_approver, string=_('Is Approver'), type='integer'),
	}

	_defaults = {
		'created_date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
		'student_id': lambda self, cr, uid, context: self._get_student(cr, uid, uid),
		'state': lambda *args: 'draft',
	}

	def search(self, cr, uid, domain, offset=0, limit=None, order=None, context=None, count=False):
		if uid == 1:
			return super(school_training_news_report, self).search(cr, uid, domain, offset=offset, limit=limit, order=order, context=context, count=count)
		cr.execute("""SELECT 1 
		    FROM res_groups_users_rel gu JOIN res_groups g ON g.id = gu.gid
		    WHERE uid = %s AND name ~ 'Training Manager'"""%(uid))
		flag = cr.fetchone()
		if not flag:
			cr.execute("""SELECT n.id
				FROM school_training_employee_rel t
				JOIN hr_employee e ON e.id = t.student_id
				JOIN resource_resource r ON r.id = e.resource_id
				JOIN school_training_news_report n ON n.student_id = t.student_id
				WHERE user_id = %s"""%(uid))
			result = cr.fetchall()
			ids = set()
			for r in result:
				ids.add(r[0])
			domain.append(('id','in',list(ids)))
		return super(school_training_news_report, self).search(cr, uid, domain, offset, limit, order, context, count)
	
	def release(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, { 'state': 'released' })
		return True

	def revise(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, { 'state': 'revised' })
		return True

school_training_news_report()
