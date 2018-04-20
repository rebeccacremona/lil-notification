from rest_framework.authentication import TokenAuthentication as DRFTokenAuthentication

from django.conf import settings

class TokenAuthentication(DRFTokenAuthentication):
    """
        Override default TokenAuth to allow GET, POST, or Authorization header techniques.
    """
    keyword = 'ApiKey'

    def authenticate(self, request):
        """
            Locally, try getting api_key from get/post param before using Authorization header.
        """
        if settings.DEBUG:
            api_key = request.POST.get('api_key') or request.query_params.get('api_key')
            if api_key:
                return self.authenticate_credentials(api_key)
        return super(TokenAuthentication, self).authenticate(request)
