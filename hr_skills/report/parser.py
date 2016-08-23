from datetime import datetime
from babel.dates import format_date
from tools.translate import _

from report import report_sxw
from report.report_sxw import rml_parse

class Parser(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        
        rec = context.get('form')
        
        applicant = self.pool.get('hr.employee').browse(cr, uid, rec.get('applicant_id')[0], context=context)
        
        director = self.pool.get('hr.employee').browse(cr, uid, rec.get('director_id')[0], context=context)
        
        date_obj = datetime.strptime(rec.get('application_date'), '%Y-%m-%d')
        date = format_date(date_obj, "dd 'de' MMMM 'del' Y", locale='es')
        
        self.localcontext.update({
            'lang': context.get('lang', 'es'),
            'rec': rec,
            'date': date,
            'applicant': applicant,
            'director': director,
        })
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: