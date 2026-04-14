import os
from django.contrib.auth.models import User, Group


BOOLEAN_CHOICES = (
    (True, 'Yes'),
    (False, 'No'),
)


def create_path(instance, filename):
    return os.path.join(
        'profiles',
        instance.user.username,
        filename
    )


def create_section_path(instance, filename):
    return os.path.join(
        'sections',
        str(instance.id),
        filename
    )


def get_full_name(self):
    return self.last_name + ', ' + self.first_name


User.add_to_class("__str__", get_full_name)
