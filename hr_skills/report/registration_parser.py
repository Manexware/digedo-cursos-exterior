# -*- coding: utf-8 -*-

from datetime import datetime
from babel.dates import format_date
from tools.translate import _

from report import report_sxw
from report.report_sxw import rml_parse

class Parser(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        
        rec = context.get('form')
        
        #print rec.get('detail_ids')
        details = self.pool.get('hr.training.registration.detail').browse(cr, uid, rec.get('detail_ids'), context=context)
        #print details
        titles = []
        for d in details:
            titles.append({'title': d.title})
        #print titles
                
        applicant = self.pool.get('hr.employee').browse(cr, uid, rec.get('applicant_id')[0], context=context)
        
        director = self.pool.get('hr.employee').browse(cr, uid, rec.get('director_id')[0], context=context)
        
        date_obj = datetime.strptime(rec.get('application_date'), '%Y-%m-%d')
        #date = format_date(date_obj, "dd 'de' MMMM 'del' Y", locale='es')
        date = '%02d de %s del %d' % (date_obj.day, format_date(date_obj, 'MMMM', locale='es').capitalize(), date_obj.year)
        
        self.localcontext.update({
            'rec': rec,
            'rec_detail': titles,
            'date': date,
            'applicant': applicant,
            'director': director,
        })
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: