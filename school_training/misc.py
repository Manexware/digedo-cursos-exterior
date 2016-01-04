import logging

from openerp import _

_logger = logging.getLogger(__name__)

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
