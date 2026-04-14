from django.contrib.auth.models import User
from django.db import models
from editor.models import Section


LIKERT_SCALE = (
    (1, 'Strongly Disagree'),
    (2, 'Somewhat Disagree'),
    (3, 'Neutral'),
    (4, 'Somewhat Agree'),
    (5, 'Strongly Agree'),
)


REVIEW_TYPES = (
    ('employer', 'Employer'),
    ('instructor', 'Instructor'),
    ('peer', 'Peer'),
)


class Portfolio(models.Model):
    section = models.ForeignKey(Section, on_delete=models.PROTECT, help_text='Section associated with this portfolio.')
    student = models.ForeignKey(User, unique=True, on_delete=models.PROTECT,
                                help_text='Student associated with this portfolio.')
    completed_reviews = models.IntegerField(default=0, help_text='The number or reviews completed for this portfolio.')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['section', 'student'], name='unique_section_student_constraint'
            )
        ]
        ordering = ('-section__term__term_code', 'section__course__prefix', 'section__course__number',
                    'section__section_code', 'student__last_name', 'student__first_name')
        verbose_name = 'portfolio'
        verbose_name_plural = 'portfolios'

    def __str__(self):
        return str(self.section) + ' - ' + str(self.student)

    @classmethod
    def delete_warning(cls):
        return ''

    @classmethod
    def filterable(cls):
        return False


class PortfolioReview(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.PROTECT)
    type = models.CharField(max_length=12, choices=REVIEW_TYPES, help_text='The type of portfolio review. You must '
                                                                           'complete one review of each type '
                                                                           'throughout the term.')
    reviewer_first_name = models.CharField(max_length=64, help_text='The reviewer\'s first name.')
    reviewer_last_name = models.CharField(max_length=64, help_text='The reviewer\'s last name.')
    reviewer_email = models.CharField(max_length=255, help_text='The reviewer\'s email address.')
    reviewer_phone = models.CharField(max_length=10, blank=True, null=True,
                                      help_text='The reviewer\'s phone number (digits only).')
    validated = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True, help_text='The date and time this review was created.')

    class Meta:
        ordering = ('portfolio', 'type',)
        verbose_name = 'portfolio review'
        verbose_name_plural = 'portfolio reviews'

    def __str__(self):
        return str(self.type) + ' Review'

    @classmethod
    def delete_warning(cls):
        return ''

    @classmethod
    def filterable(cls):
        return False


class PortfolioReviewFeedback(models.Model):
    review = models.ForeignKey(PortfolioReview, on_delete=models.CASCADE,
                               help_text='The review that this feedback is associated with.')
    strengths = models.TextField(help_text='What are the strengths of the student\'s portfolio? Please be as '
                                           'descriptive as possible.')
    weaknesses = models.TextField(help_text='What are the weaknesses of the student\'s portfolio? Please be as '
                                            'constructive and descriptive as possible.')
    recommendations = models.TextField(help_text='What recommendations do you have for the student to improve '
                                                 'their portfolio?')
    timestamp = models.DateTimeField(auto_now_add=True, help_text='The date and time this feedback was provided.')

    class Meta:
        ordering = ('review',)
        verbose_name = 'portfolio review feedback'
        verbose_name_plural = 'portfolio review feedback'

    @classmethod
    def delete_warning(cls):
        return ''

    @classmethod
    def filterable(cls):
        return False


class PortfolioReviewPresentationFeedback(models.Model):
    feedback = models.OneToOneField(PortfolioReviewFeedback, on_delete=models.CASCADE,
                                    help_text='The review feedback that this presentation is associated with.')
    delivery = models.IntegerField(choices=LIKERT_SCALE, help_text='The student delivered the presentation in a '
                                                                   'clear and structured manner.')
    maintained_interest = models.IntegerField(choices=LIKERT_SCALE, help_text='The student maintained my interest '
                                                                              'during the entire presentation.')
    answered_questions = models.IntegerField(choices=LIKERT_SCALE, help_text='The student answered questions '
                                                                             'effectively.')
    enthusiasm = models.IntegerField(choices=LIKERT_SCALE, help_text='The student was enthusiastic about the process.')
    organization = models.IntegerField(choices=LIKERT_SCALE, help_text='The student was well organized and prepared.')
    professionalism = models.IntegerField(choices=LIKERT_SCALE, help_text='The student was sufficiently presentable '
                                                                          '(dressed professionally, good hygiene, '
                                                                          'etc.)')
    eye_contact = models.IntegerField(choices=LIKERT_SCALE, help_text='The student maintained eye contact with '
                                                                      'the audience.')
    elocution = models.IntegerField(choices=LIKERT_SCALE, help_text='The student spoke in a clearly audible and '
                                                                    'respectful tone.')
    overall = models.IntegerField(choices=LIKERT_SCALE, help_text='Overall, I would rate the presentation:')
    comments = models.TextField(help_text='Do you have any additional comments for the student regarding their '
                                          'presentation skills?')
    timestamp = models.DateTimeField(auto_now_add=True, help_text='The date and time this feedback was provided.')

    class Meta:
        ordering = ('feedback',)
        verbose_name = 'portfolio review presentation feedback'
        verbose_name_plural = 'portfolio review presentation feedback'

    @classmethod
    def delete_warning(cls):
        return ''

    @classmethod
    def filterable(cls):
        return False


class PortfolioReviewProcessFeedback(models.Model):
    feedback = models.OneToOneField(PortfolioReviewFeedback, on_delete=models.CASCADE,
                                    help_text='The review feedback that this process feedback is associated with.')
    process = models.TextField(help_text='Do you have any recommendations for improving the portfolio review process? '
                                         'We\'d be happy to receive any feedback you can give!')
    timestamp = models.DateTimeField(auto_now_add=True, help_text='The date and time this feedback was provided.')

    class Meta:
        ordering = ('feedback',)
        verbose_name = 'portfolio review process feedback'
        verbose_name_plural = 'portfolio review process feedback'

    @classmethod
    def delete_warning(cls):
        return ''

    @classmethod
    def filterable(cls):
        return False


class PortfolioSettings(models.Model):
    instructor = models.ForeignKey(User, on_delete=models.PROTECT, unique=True)
    review_points = models.FloatField(default=400, help_text='The total number of points awarded for a portfolio '
                                                             'review.')
    reviews_required = models.IntegerField(default=3, help_text='The number of reviews required for a portfolio.')

    class Meta:
        verbose_name = 'portfolio setting'
        verbose_name_plural = 'portfolio settings'

    @classmethod
    def delete_warning(cls):
        return ''

    @classmethod
    def filterable(cls):
        return False
