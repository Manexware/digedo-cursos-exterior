import logging


_logger = logging.getLogger(__name__)

STATE = [
    ('draft', _('Draft')),
    ('accepted', _('Accepted')),
    ('rejected', _('Rejected')),
    ('approved', _('Approved')),
]
