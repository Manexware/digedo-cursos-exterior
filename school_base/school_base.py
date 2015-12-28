from osv import osv, fields
from tools.translate import _

BLOOD_TYPE = [
    ('O-', 'O Rh-'),
    ('O+', 'O Rh+'),
    ('A-', 'A Rh-'),
    ('A+', 'A Rh+'),
    ('B-', 'B Rh-'),
    ('B+', 'B Rh+'),
    ('AB-', 'AB Rh-'),
    ('AB+', 'AB Rh+')
]

#----------------------------------------------------------
# 01.- Grade
#----------------------------------------------------------
class school_grade(osv.osv):
    """Grade"""

    _name = 'school.grade'
    _description = 'Grade'
    
    _columns = {
        'code': fields.char(_('Code'), size=6, required=True),
        'name': fields.char(_('Name'), size=64, required=True),
        'is_official': fields.boolean(_('Is official'), help=_('Indicates if the marine is official')),
    }

    _defaults = {
        'is_official': lambda *args: False,
    }
    
    _sql_constraints = [
        ('code_unq', 'unique(code)', _('Code must be unique'))
    ]

    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        if not args:
            args=[]
        if not context:
            context={}
        ids = False
        if len(name) == 4:
            ids = self.search(cr, user, [('code', 'ilike', name)] + args,
                    limit=limit, context=context)
        if not ids:
            ids = self.search(cr, user, [('name', operator, name)] + args,
                    limit=limit, context=context)
        return self.name_get(cr, user, ids, context)
    
school_grade()

#----------------------------------------------------------
# 02.- Specialty
#----------------------------------------------------------
class school_specialty(osv.osv):
    """Specialty"""

    _name = 'school.specialty'
    _description = 'Specialty'

    _columns = {
        'code': fields.char(_('Code'), size=4, required=True),
        'name': fields.char(_('Name'), size=64, required=True),
    }

    _sql_constraints = [
        ('code_unq', 'unique(code)', _('Code must be unique')),
        ('name_unq', 'unique(name)', _('Name must be unique'))
    ]
    
    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        if not args:
            args=[]
        if not context:
            context={}
        ids = False
        if len(name) == 2:
            ids = self.search(cr, user, [('code', 'ilike', name)] + args,
                    limit=limit, context=context)
        if not ids:
            ids = self.search(cr, user, [('name', operator, name)] + args,
                    limit=limit, context=context)
        return self.name_get(cr, user, ids, context)
    
school_specialty()

#----------------------------------------------------------
# 03.- Employee
#----------------------------------------------------------
class school_person(osv.osv):
    """Person"""

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        reads = self.read(cr, uid, ids, ['name', 'last_name', 'grade_id', 'specialty_id', 'title', 'suffix', 'status'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['last_name']:
                name = name + ' ' + record['last_name']
            if record['status']:
                if record['status'] == 'functionary':
                    if record['title']:
                        name = record['title'] + ' ' + name
                    if record['suffix']:
                        name = name + ', ' + record['suffix']
                elif (record['status'] == 'active' or record['status'] == 'passive'):
                    if record['grade_id']:
                        grade = self.pool.get('school.grade').browse(cr, uid, record['grade_id'][0], context=context)
                        if record['status'] == 'passive':
                            name = grade.code + '(SP) ' + name
                        else:
                            if record['specialty_id']:
                                specialty = self.pool.get('school.specialty').browse(cr, uid, record['specialty_id'][0], context=context)
                                name = grade.code + '-' + specialty.code + ' ' + name
                            else:
                                name = grade.code + ' ' + name
                    if record['suffix']:
                        name = name + ', ' + record['suffix']
                    elif record['title']:
                        name = name + ', ' + record['title']
            res.append((record['id'], name))
        return res

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    _inherit = 'hr.employee'

    _columns = {
        'title': fields.char(_('Title'), size=16),
        'last_name': fields.char(_('Last Name'), size=32),
        'grade_id': fields.many2one('school.grade', _('Grade')),
        'specialty_id': fields.many2one('school.specialty', _('Specialty')),
        'suffix': fields.char(_('Suffix'), size=16, help=_('Masters degree, PhD')),
        'status': fields.selection([
                ('active', _('Active in Force')), 
                ('passive', _('Passive in Force')), 
                ('functionary', _('Public Functionary'))
            ], _('Status')),
        'full_name': fields.function(_name_get_fnc, type="char", string='Name'),
        'blood_type': fields.selection(BLOOD_TYPE, _('Blood Type')),
        'admission_date': fields.date(_('Admission Date'), help=_('(mm/dd/yyyy)')),
        'last_ascent_date': fields.date(_('Last Ascent Date'), help=_('(mm/dd/yyyy)')),
        'height': fields.float(_('Height'), help=_('In meters')),
        'eye_color': fields.char(_('Eye Color'), size=32),
        'hair_color': fields.char(_('Hair Color'), size=32),
        'shirt_size': fields.integer(_('Shirt Size')),
        'pants_size': fields.integer(_('Pants Size')),
        'shoe_size': fields.integer(_('Shoe Size')),
        'cap_size': fields.integer(_('Cap Size')),
    }

    _defaults = {
        'status': lambda *args: 'functionary',
    }

    _sql_constraints = [
        ('id_unq', 'unique(identification_id)', _('ID must be unique'))
    ]
    
    def _check_id(self, cr, uid, ids):
        for s in self.browse(cr, uid, ids):
            if not s.identification_id:
                return True
            if len(s.identification_id) != 10 or not s.identification_id.isdigit():
                return False
            accum = 0
            for i in range(9):
                d = int(s.identification_id[i])
                if ((i % 2) == 0):
                    accum += (d * 2) > 9 and (d * 2) - 9 or (d * 2)
                else:
                    accum += d
            last = int(s.identification_id[9])
            residue = (accum % 10)
            digit = residue > 0 and 10 - residue or 0
            return digit == last
        return True

    _constraints = [
        (_check_id, _('ID is not valid'), ['identification_id'])
    ]

    _order = 'last_name'
    
    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        if not args:
            args=[]
        if not context:
            context={}
        ids = False
        name_array = name.split(' ')
        if len(name_array) == 1:
            args += ['|',('name','ilike',name),('last_name','ilike',name)]
        if len(name_array) == 2:
            args += [('name','ilike',name_array[0]),('last_name','ilike',name_array[1])]
        if len(name_array) == 3:
            args += [('name','ilike',name_array[0]),('last_name','ilike',name_array[1]+' '+name_array[2])]
        ids = self.search(cr, user, args, limit=limit, context=context)
        return self.name_get(cr, user, ids, context)
    
school_person()

#----------------------------------------------------------
# 04.- Formation Shaft
#----------------------------------------------------------
class school_crew_formation_shaft(osv.osv):
    """Formation Shaft"""

    _name = 'school.formation.shaft'
    _description = 'Formation Shaft'

    _columns = {
        'name': fields.char(_('Name'), size=64, required=True),
    }

    _order = 'name'

    _sql_constraints = [
        ('name_unq', 'unique(name)', _('Name must be unique'))
    ]

school_crew_formation_shaft()    

#----------------------------------------------------------
# 05.- Batch
#----------------------------------------------------------
class school_crew_batch(osv.osv):
    """Batch"""

    _name = 'school.batch'
    _description = 'Batch'

    _columns = {
        'name': fields.char(_('Name'), size=64, required=True),
    }

    _order = 'name'

    _sql_constraints = [
        ('name_unq', 'unique(name)', _('Name must be unique'))
    ]
    
school_crew_batch()

#----------------------------------------------------------
# 06.- Evaluation Parameter
#----------------------------------------------------------
class school_crew_evaluation_parameter(osv.osv):
    """Evaluation Parameter"""

    _name = 'school.evaluation.parameter'
    _description = 'Evaluation Parameter'

    _columns = {
        'name': fields.char(_('Name'), size=32, required=True),
        'factor': fields.float(_('Factor'), digits=(1,4), required=True),
        'matter_id': fields.many2one('school.matter', _('Matter')),
    }

    _defaults = {
        'factor': lambda *args: 0.2,
    }

    def _check_factor(self, cr, uid, ids):
        for p in self.browse(cr, uid, ids):
            if p.factor < 0 or p.factor > 1:
                return False
        return True

    _constraints = [
        (_check_factor, _('Factor must be between 0 and 1'), ['factor'])
    ]

school_crew_evaluation_parameter()

#----------------------------------------------------------
# 07.- Topic
#----------------------------------------------------------
class school_topic(osv.osv):
    """Topic"""

    _name = 'school.topic'
    _description = 'Topic'

    _columns = {
        'sequence': fields.integer(_('Sequence')),
        'name': fields.char(_('Name'), size=256, required=True),
        'no_hours': fields.integer(_('# Hours'), required=True),
        'teaching_unit_id': fields.many2one('school.teaching.unit', _('Teaching Unit')),
    }

    _sql_constraints = [
        ('hours_chk', 'check(no_hours > 0)', _('# Hours must be greater than 0'))
    ]
    
school_topic()    

#----------------------------------------------------------
# 08.- Teaching Unit
#----------------------------------------------------------
class school_teaching_unit(osv.osv):
    """Teaching Unit"""

    _name = 'school.teaching.unit'
    _description = 'Teaching Unit'

    def _compute_hours(self, cr, uid, ids, field, arg, context=None):
        cr.execute('SELECT teaching_unit_id, sum(no_hours) \
            FROM school_topic \
            WHERE teaching_unit_id IN %(ids)s \
            GROUP BY teaching_unit_id', {'ids': tuple(ids)})
        result = dict(cr.fetchall())
        for id in ids:
            result[id] = result.get(id, 0)
        return result

    _columns = {
        'sequence': fields.integer(_('Sequence')),
        'name': fields.char(_('Name'), size=64, required=True),
        'objective': fields.text(_('Objetive')),
        'topic_ids': fields.one2many('school.topic', 'teaching_unit_id', _('Topics')),
        'no_hours': fields.function(_compute_hours, string=_('# Hours'), type='integer'),
        'matter_id': fields.many2one('school.matter', _('Matter')),
    }

school_teaching_unit()

#----------------------------------------------------------
# 09.- Matter
#----------------------------------------------------------
class school_crew_matter(osv.osv):
    """Matter"""

    _name = 'school.matter'
    _description = 'Matter'

    _columns = {
        'name': fields.char(_('Name'), size=128, required=True),
        'code': fields.char(_('Code'), size=10, required=True),
        'formation_id': fields.many2one('school.formation.shaft', _('Formation Shaft'), ondelete='restrict'),
        'credits': fields.integer(_('Credits'), required=True),
        'batch_id': fields.many2one('school.batch', _('Batch')),
        'param_ids': fields.one2many('school.evaluation.parameter', 'matter_id', _('Evaluation Parameters')),
        'requirements': fields.text(_('Requirements')),
        'specific_objetives': fields.text(_('Specific Objetives')),
        'conceptual_approach': fields.text(_('Conceptual Approach')),
        'teaching_unit_ids': fields.one2many('school.teaching.unit', 'matter_id', _('Teaching Units')),
    }

    _defaults = {
        'credits': lambda *args: 1,
    }

    _sql_constraints = [
        ('code_unq', 'unique(code)', _('Code must be unique')),
        ('name_unq', 'unique(name)', _('Name must be unique')),
        ('credits_chk', 'check(credits > 0)', _('Credits must be greater than 0'))
    ]
    
    _order = 'formation_id, name'

    def _check_factor(self, cr, uid, ids):
        for matter in self.browse(cr, uid, ids):
            total = 0
            for d in matter.param_ids:
                total += d.factor
            if total == 1:
                return True
        return False

    _constraints = [
        (_check_factor, _('Sum of factors must be 1'), ['param_ids'])
    ]

school_crew_matter()
