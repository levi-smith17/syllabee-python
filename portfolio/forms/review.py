from ..models import Portfolio, PortfolioReview
from django import forms
from django.core.exceptions import ValidationError


class PortfolioReviewForm(forms.ModelForm):
    portfolio = forms.CharField(widget=forms.HiddenInput(), required=False)
    reviewer_email = forms.EmailField(help_text=PortfolioReview._meta.get_field('reviewer_email').help_text)

    def __init__(self, *args, **kwargs):
        self.portfolio_id = kwargs.pop('portfolio_id')
        super(PortfolioReviewForm, self).__init__(*args, **kwargs)
        self.fields['portfolio'].initial = self.portfolio_id

    class Meta:
        model = PortfolioReview
        exclude = ('validated', 'timestamp',)

    def clean_portfolio(self):
        try:
            return Portfolio.objects.get(pk=self.cleaned_data['portfolio'])
        except Portfolio.DoesNotExist:
            raise ValidationError('The requested portfolio does not exist.')


class PortfolioReviewDeleteForm(forms.ModelForm):
    class Meta:
        model = PortfolioReview
        exclude = ('portfolio', 'type', 'reviewer_last_name', 'reviewer_first_name', 'reviewer_email',
                   'reviewer_phone', 'validated', 'timestamp')
