from rest_framework.throttling import AnonRateThrottle


class DonationRedirectThrottle(AnonRateThrottle):
    scope = "donation_redirect"
