from openerp import _, models, fields, api
from ..misc import STATE



class HrTrainingDocumentValuation(models.Model):
    """"""

    _name = 'hr.training.document.valuation'
    _description = 'Valuation of Document'
    _rec_name = 'trade_no'

    def _compute_score(self, cr, uid, ids, field, arg, context=None):
        res = {}
        for id in ids:
            res[id] = {'historic_score': 0.0, 'score': 0.0}
        sql = 'SELECT sum(score) \
            FROM hr_training_document_valuation \
            WHERE id < %s AND applicant_id = %s'
        records = self.browse(cr, uid, ids, context=context)
        for record in records:
            cr.execute(sql % (record.id, record.applicant_id.id))
            hist = cr.fetchone()
            #print hist
            hist_score = (hist and hist[0]) and hist[0] or 0.0
            res[record.id]['historic_score'] = hist_score
            #res[record.id]['score'] = record.valoration_id.score - hist_score ##mvega
            res[record.id]['score'] = record.valoration_id.score
        #print res
        return res


    trade_no = fields.Char(_('Trade No'), size=64, required=True, readonly=True, states={'draft':[('readonly',False)]})
    application_date = fields.Date(_('Application Date'), required=True, readonly=True, states={'draft':[('readonly',False)]})
    type_id = fields.Many2one('hr.training.type', _('Type'), required=True, readonly=True, states={'draft':[('readonly',False)]})
    valoration_id = fields.Many2one('hr.training.valoration', _('Valoration'), domain="[('type_id', '=', type_id)]", required=True, readonly=True, states={'draft':[('readonly',False)]})
    historic_score = fields.Float(compute='_compute_score', string=_('Historic Score'), multi='compute')
    score = fields.Float(compute='_compute_score', string=_('Score'), digits=(2,2), store=True, multi='compute')
    applicant_id = fields.Many2one('hr.employee', _('Applicant'), required=True, ondelete='restrict', readonly=True, states={'draft':[('readonly',False)]})
    school_id = fields.Many2one('hr.base.school', _('School'), required=True, ondelete='restrict', readonly=True, states={'draft':[('readonly',False)]})
    title = fields.Char(_('Title'), size=128, required=True, readonly=True, states={'draft':[('readonly',False)]})
    director_id = fields.Many2one('hr.employee', _('Director'), ondelete='set null')
    director_fname = fields.Char(_('First Name'), size=48)
    director_lname1 = fields.Char(_('Last Name 1'), size=48)
    director_lname2 = fields.Char(_('Last Name 2'), size=48)
    annex = fields.Char(_('Annex'), size=64)
    signature = fields.Char(_('Signature'), size=64)
    allocation = fields.Char(_('Allocation'), size=64, required=True, readonly=True, states={'draft':[('readonly',False)]})
    state = fields.Selection(STATE, _('State'))
    approved_date = fields.Date(_('Approved Date'), readonly=True, help=_('Date when document was approved'))


    _defaults = {
        'application_date': lambda *args: time.strftime('%Y-%m-%d'),
        'state': lambda *args: 'draft',
        'annex': lambda *args: u'01 f/ú',
    }

    _sql_constraints = [
        ('trade_unq', 'unique(trade_no)', _('Trade No must be unique')),
    ]

    def onchange_type(self, cr, uid, ids, type_id, context=None):
        value = {'valoration_id': False}
        return {'value': value}

    def onchange_director(self, cr, uid, ids, director_id, context=None):
    	employee_obj = self.pool.get('hr.employee')
    	employee_data = employee_obj.browse(cr, uid, director_id, context=context)
    	value = {'director_fname': False, 'director_lname1': False, 'director_lname2': ''}
    	if employee_data:
	    name_array = employee_data.name.split(' ')
            value['director_fname'] = name_array[0]
	    if 'last_name' in employee_data:
		lname_array = employee_data.last_name.split(' ')
		index = 0
		for lname in lname_array:
		    if index == 0:
			value['director_lname1'] = lname.upper()
		    else:
			value['director_lname2'] = value['director_lname2'] + ' ' + lname
		    index += 1
	    elif len(name_array) > 1:
		value['director_lname1'] = name_array[1].upper()
    	return {'value': value}

    def accept(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'accepted'})
        return True

    def reject(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'rejected'})
        return True

    def approve(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'approved', 'approved_date': time.strftime('%Y-%m-%d')})
        return True

    def print_valuation(self, cr, uid, ids, context=None):
	context['form'] = self.read(cr, uid, ids)[0]
	return {
	    'type':'ir.actions.report.xml',
	    'report_name':'valuation_report',
	    'context': context,
	}

    def copy(self, cr, uid, ids, default=None, context=None):
        vals = {}
        current_rec = self.read(cr, uid, ids, context=context)
        new_no = re.sub(r'-[0-9]*-', '-0-', current_rec.get('trade_no'))
        #print new_no
        vals.update({'trade_no': new_no})
        return super(hr_training_document_valuation, self).copy(cr, uid, ids, vals, context=context)

    def search(self, cr, uid, domain, offset=0, limit=None, order=None, context=None, count=False):
	cr.execute("""SELECT 1
	    FROM res_groups_users_rel gu JOIN res_groups g ON g.id = gu.gid
	    WHERE uid = %s AND name ~ 'Digitizer of Documents'"""%(uid))
	flag = cr.fetchone()
	if not flag:
	    cr.execute("""SELECT d.id
	        FROM hr_training_document_valuation d
	        JOIN hr_employee e ON e.id = d.applicant_id
	        JOIN resource_resource r ON r.id = e.resource_id
	        WHERE user_id = %s"""%(uid))
	    result = cr.fetchall()
	    ids = set()
	    for r in result:
		ids.add(r[0])
	    domain.append(('id','in',list(ids)))
	return super(hr_training_document_valuation, self).search(cr, uid, domain, offset, limit, order, context, count)
