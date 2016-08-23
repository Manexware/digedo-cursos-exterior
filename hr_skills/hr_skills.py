# -*- coding: utf-8 -*-

from osv import osv, fields
from tools.translate import _
from datetime import datetime, date
import time
import re

STATE = [
    ('draft', _('Draft')),
    ('accepted', _('Accepted')),
    ('rejected', _('Rejected')),
    ('approved', _('Approved')),
]

########################################################################
class hr_training_type(osv.osv):
    """"""
    
    _name = 'hr.training.type'
    _description = 'Type of Training'
    
    _columns = {
        'name': fields.char(_('Name'), size=120, required=True),
    }
    
    _sql_constraints = [
        ('name_unq', 'unique(name)', _('Name must be unique')),
    ]

hr_training_type()

########################################################################
class hr_training_valoration(osv.osv):
    """"""
    
    _name = 'hr.training.valoration'
    _description = 'Valoration'
    
    def name_get(self, cr, uid, ids, context=None):
	reads = self.read(cr, uid, ids, ['name', 'score'], context=context)
	res = []
	for record in reads:
	    name = '%s (%.2f)' % (record['name'], record['score'])
	    res.append((record['id'], name))
	return res
	
    _columns = {
        'name': fields.char(_('Name'), size=120, required=True),
        'score': fields.float(_('Score'), digits=(1,2), required=True),
        'note': fields.text(_('Note')),
        'type_id': fields.many2one('hr.training.type', _('Type'), required=True, ondelete='restrict'),
    }
    
    _defaults = {
        'score': lambda *args: 0.0,
    }
    
    _sql_constraints = [
        ('name_unq', 'unique(name)', _('Name must be unique')),
        ('score_chk', 'check(score > 0)', _('Score must be greater than 0')),
    ]

hr_training_valoration()

########################################################################
class hr_training_document_valuation(osv.osv):
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
    
    _columns = {
        'trade_no': fields.char(_('Trade No'), size=64, required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'application_date': fields.date(_('Application Date'), required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'type_id': fields.many2one('hr.training.type', _('Type'), required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'valoration_id': fields.many2one('hr.training.valoration', _('Valoration'), domain="[('type_id', '=', type_id)]", required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'historic_score': fields.function(_compute_score, string=_('Historic Score'), type='float', multi='compute'),
        'score': fields.function(_compute_score, string=_('Score'), type='float', digits=(2,2), store=True, multi='compute'),
        'applicant_id': fields.many2one('hr.employee', _('Applicant'), required=True, ondelete='restrict', readonly=True, states={'draft':[('readonly',False)]}),
        'school_id': fields.many2one('hr.base.school', _('School'), required=True, ondelete='restrict', readonly=True, states={'draft':[('readonly',False)]}),
        'title': fields.char(_('Title'), size=128, required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'director_id': fields.many2one('hr.employee', _('Director'), ondelete='set null'),
        'director_fname': fields.char(_('First Name'), size=48),
        'director_lname1': fields.char(_('Last Name 1'), size=48),
        'director_lname2': fields.char(_('Last Name 2'), size=48),
        'annex': fields.char(_('Annex'), size=64),
        'signature': fields.char(_('Signature'), size=64),
        'allocation': fields.char(_('Allocation'), size=64, required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'state': fields.selection(STATE, _('State')),
        'approved_date': fields.date(_('Approved Date'), readonly=True, help=_('Date when document was approved')),
    }
    
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
    
hr_training_document_valuation()

########################################################################
class hr_training_registration_detail(osv.osv):
    
    _name = 'hr.training.registration.detail'
    _description = 'Detail of Document Registration'
    _rec_name = 'school_id'

    _columns = {
        'school_id': fields.many2one('hr.base.school', _('School'), required=True, ondelete='restrict'),
        'title': fields.text(_('Title'), required=True),
        'registration_id': fields.many2one('hr.training.document.registration', _('Registration'), required=True, ondelete='cascade'),
    }
    
hr_training_registration_detail()

########################################################################
class hr_training_document_registration(osv.osv):
    
    _name = 'hr.training.document.registration'
    _description = 'Registration of Document'
    _rec_name = 'trade_no'
    
    def _no_annex(self, cr, uid, ids, field, arg, context=None):
	if not ids:
	    return {}
	sql = """SELECT registration_id, count(*) \
	    FROM hr_training_registration_detail \
	    WHERE registration_id IN %s \
	    GROUP BY registration_id"""
	cr.execute(sql, (tuple(ids),))
	result = dict(cr.fetchall())
        for id in ids:
            result[id] = result.get(id, 0)
        return result
    
    _columns = {
        'trade_no': fields.char(_('Trade No'), size=64, required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'application_date': fields.date(_('Application Date'), required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'applicant_id': fields.many2one('hr.employee', _('Applicant'), required=True, ondelete='restrict', readonly=True, states={'draft':[('readonly',False)]}),
        'allocation': fields.char(_('Allocation'), size=64, required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'director_id': fields.many2one('hr.employee', _('Director'), ondelete='set null'),
        'director_fname': fields.char(_('First Name'), size=48),
        'director_lname1': fields.char(_('Last Name 1'), size=48),
        'director_lname2': fields.char(_('Last Name 2'), size=48),
        'no_annex': fields.function(_no_annex, string=_('No of Annexes'), type='integer'),
        'signature': fields.char(_('Signature'), size=64),
        'detail_ids': fields.one2many('hr.training.registration.detail', 'registration_id', _('Details'), readonly=True, states={'draft':[('readonly',False)]}),
        'state': fields.selection(STATE, _('State')),
        'approved_date': fields.date(_('Approved Date'), readonly=True, help=_('Date when document was approved')),
    }
    
    _defaults = {
        'application_date': lambda *args: time.strftime('%Y-%m-%d'),
        'state': lambda *args: 'draft',
    }
    
    _sql_constraints = [
        ('trade_unq', 'unique(trade_no)', _('Trade No must be unique')),
    ]
    
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
    
    def print_registration(self, cr, uid, ids, context=None):
	context['form'] = self.read(cr, uid, ids)[0]
	return {
	    'type':'ir.actions.report.xml',
	    'report_name':'registration_report',
	    'context': context,
	}

    def copy(self, cr, uid, ids, default=None, context=None):
	vals = {}
	current_rec = self.read(cr, uid, ids, context=context)
	new_no = re.sub(r'-[0-9]*-', '-0-', current_rec.get('trade_no'))
	#print new_no
	vals.update({'trade_no': new_no})
	return super(hr_training_document_registration, self).copy(cr, uid, ids, vals, context=context)
    
    def search(self, cr, uid, domain, offset=0, limit=None, order=None, context=None, count=False):
	cr.execute("""SELECT 1 
            FROM res_groups_users_rel gu JOIN res_groups g ON g.id = gu.gid
            WHERE uid = %s AND name ~ 'Digitizer of Documents'"""%(uid))
	flag = cr.fetchone()
	if not flag:
	    cr.execute("""SELECT d.id
	        FROM hr_training_document_registration d 
	        JOIN hr_employee e ON e.id = d.applicant_id
	        JOIN resource_resource r ON r.id = e.resource_id
	        WHERE user_id = %s"""%(uid))
	    result = cr.fetchall()
	    ids = set()
	    for r in result:
		ids.add(r[0])
	    domain.append(('id','in',list(ids)))	    
	return super(hr_training_document_registration, self).search(cr, uid, domain, offset, limit, order, context, count)
    
hr_training_document_registration()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
