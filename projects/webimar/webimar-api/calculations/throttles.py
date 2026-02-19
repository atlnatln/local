from rest_framework.throttling import SimpleRateThrottle


class CalculationFeedbackRateThrottle(SimpleRateThrottle):
    scope = 'calculation_feedback'
    rate = '1/m'

    def __init__(self):
        super().__init__()
        self.num_requests = 1
        self.duration = 180

    def get_cache_key(self, request, view):
        ident = self.get_ident(request)
        if not ident:
            return None
        return f'throttle_{self.scope}_{ident}'
