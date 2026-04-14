from django import template
from portfolio.models import Portfolio, PortfolioSettings

register = template.Library()


@register.simple_tag()
def get_review_feedback(location_id):
    return ()


@register.simple_tag()
def get_total_time2(internship_id, location_id, remaining):
    return True
