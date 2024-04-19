import logging
from typing import Callable

from django.http.request import HttpRequest
from django.utils.functional import SimpleLazyObject

from pta_export.core.models import User as PtaUser

logger = logging.getLogger(__name__)


def get_pta_user(request):
    if not hasattr(request, "_cached_pta_user"):
        try:
            pta_user = PtaUser.objects.get(email=(email := request.user.email))
        except PtaUser.DoesNotExist:
            pta_user = None
            logger.info("Could not find PTA user for email: %s", email)
        request._cached_pta_user = pta_user
    return request._cached_pta_user


class PtaUserMiddleware:
    """
    Look up the OCPTA user from the email address of the django user.
    """

    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        request.pta_user = SimpleLazyObject(lambda: get_pta_user(request))
        return self.get_response(request)
