from django.contrib.auth.models import User, Group
from django.db import models
from editor.models import Bond, MasterBond, MasterSyllabus, Section, Question


class SectionProgress(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    master_syllabus = models.ForeignKey(MasterSyllabus, on_delete=models.CASCADE)
    start_time = models.DateTimeField(help_text='Start time of user completing master syllabus for section.')
    stop_time = models.DateTimeField(null=True, help_text='Stop time of user completing master syllabus for section.')
    progress = models.FloatField(help_text='The current progress percentage.')
    completed = models.BooleanField(default=False, help_text='Whether all blocks are fully completed or not.')
    points = models.IntegerField(default=0, help_text='Total points awarded to user for this section.')
    lti_launch_id = models.CharField(max_length=255)
    student = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['section', 'student'], name='unique_viewer_section_hash_and_student'
            )
        ]
        ordering = ('section', 'student__last_name', 'student__first_name')
        verbose_name = 'section progress'
        verbose_name_plural = 'section progress'

    def __str__(self):
        return str(self.section) + ' ' + str(self.student)

    @classmethod
    def delete_warning(cls):
        return ''

    @classmethod
    def filterable(cls):
        return False


class MasterBondProgress(models.Model):
    section_progress = models.ManyToManyField(SectionProgress)
    master_bond = models.ForeignKey(MasterBond, on_delete=models.CASCADE)
    start_time = models.DateTimeField(null=True, help_text='Start time of user completing segment.')
    stop_time = models.DateTimeField(null=True, help_text='Stop time of user completing segment.')
    completed = models.BooleanField(default=False, help_text='Whether the segment is fully completed or not.')
    points = models.IntegerField(default=0, help_text='Total points awarded to user for this segment.')
    student = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ('student',)
        verbose_name = 'segment progress'
        verbose_name_plural = 'segment progress'


class BondProgress(models.Model):
    master_bond_progress = models.ForeignKey(MasterBondProgress, on_delete=models.CASCADE)
    bond = models.ForeignKey(Bond, on_delete=models.CASCADE)
    start_time = models.DateTimeField(null=True, help_text='Start time of user completing block.')
    stop_time = models.DateTimeField(null=True, help_text='Stop time of user completing block.')
    completed = models.BooleanField(default=False, help_text='Whether the block is fully completed or not.')
    student = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ('student',)
        verbose_name = 'block progress'
        verbose_name_plural = 'block progress'


class ResponseProgress(BondProgress):
    question = models.ForeignKey(Question, null=True, on_delete=models.CASCADE)
    attempts = models.IntegerField(default=0, help_text='The number of attempts a student has made within a response '
                                                        'block.')
    attempts_available = models.IntegerField(default=0, help_text='The number of attempts available for this response.')
    points = models.IntegerField(default=0, help_text='Total points awarded to user for completion of this block.')
    points_available = models.IntegerField(default=0, help_text='The number of points available for this response.')
    deduction = models.IntegerField(default=0, help_text='Total points deducted for this block if points ladder is '
                                                         'enabled.')

    class Meta:
        ordering = ('student',)
        verbose_name = 'response progress'
        verbose_name_plural = 'response progress'


class AttemptProgress(models.Model):
    response_progress = models.ForeignKey(ResponseProgress, on_delete=models.CASCADE)
    count = models.IntegerField(default=0, help_text='The attempt number for this response progress.')
    answer = models.TextField(help_text='The answer provided by the student.')
    correct = models.BooleanField(default=False, help_text='Whether or not the attempt was correct.')
    student = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ('student',)
        verbose_name = 'attempt progress'
        verbose_name_plural = 'attempt progress'
