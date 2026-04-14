import json
from ..models import AttemptProgress, BondProgress, MasterBondProgress, ResponseProgress, SectionProgress
from datetime import datetime
from django.db.models import Q
from django.http import Http404
from django.urls import reverse
from editor.models import Bond, MasterBond, MasterSyllabus, Profile, Question, ResponseBlock, Section, Segment
from random import shuffle


def check_response(request, master_syllabus, bond_progress):
    """
    Verifies that the response chosen by the user is the correct one or not.

    Parameters:
    :param (object) request:                    The request object (for session variables).
    :param (MasterSyllabus) master_syllabus:    The master syllabus (used for interactive syllabus settings).
    :param (BondProgress) bond_progress:        The bond progress object being checked.

    Returns:
    :return (tuple)                             - Returns a tuple containing all necessary progress objects for the
                                                current user.
    """
    if hasattr(bond_progress, 'responseprogress'):
        response_progress = bond_progress.responseprogress
        response_block = bond_progress.bond.block.responseblock
        attempts = (AttemptProgress.objects
                    .filter(response_progress=response_progress, student=request.user)
                    .order_by('-count'))
        count = attempts.first().count if attempts.exists() else 0
        try:
            attempt = AttemptProgress(response_progress=response_progress, student=request.user, count=(count+1),
                                      answer=request.GET.get('response'))
        except:
            return False
        question = get_response_question(response_progress.question)
        if str(request.GET.get('response')) == str(question.correct_response):
            # The user provided a correct response!
            if question.max_points > 0:
                response_progress.points += (question.max_points + response_progress.deduction)
                max_points = question.max_points
            elif response_block.max_points > 0:
                response_progress.points += (response_block.max_points + response_progress.deduction)
                max_points = response_block.max_points
            else:
                response_progress.points += (master_syllabus.max_points + response_progress.deduction)
                max_points = master_syllabus.max_points
            if response_progress.points > max_points:
                response_progress.points = (max_points + response_progress.deduction)
            response_progress.attempts += 1
            response_progress.save()
            attempt.correct = True
            attempt.save()
            return True
        else:
            # The user provided an incorrect response!
            # Update the user's number of attempts.
            response_progress.attempts += 1
            # If points ladder is enabled, deduct the required number of points.
            if master_syllabus.points_ladder:
                response_progress.deduction -= master_syllabus.points_ladder_deduction
            response_progress.save()
            attempt.correct = False
            attempt.save()
            return False
    return False


def create_or_get_progress(request, master_syllabus, section, create=False, pre_stage=False):
    """
    Creates or retrieves the progress objects for the current user.

    Parameters:
    :param (object) request:                    The request object (for session variables).
    :param (MasterSyllabus) master_syllabus:    The master syllabus to check (or create) against.
    :param (Section) section:                   The section to check (or create) against.
    :param (boolean) create:                    Whether to create progress objects or only get what currently exists.
    :param (boolean) pre_stage:                 Whether to pre-stage progress objects or not. Pre-staging only creates
                                                SectionProgress and MasterBondProgress objects.

    Returns:
    :return (tuple)                             - Returns a tuple containing all necessary progress objects for the
                                                current user.
    """
    try:
        # Try to get the existing progress for the current user.
        section_progress = SectionProgress.objects.get(section__hash=section.hash, student=request.user)
    except SectionProgress.DoesNotExist:
        # No existing progress exists, so start the creation process.
        if create:
            section_progress = SectionProgress(section=section, master_syllabus=master_syllabus, student=request.user,
                                               start_time=datetime.now(), progress=0.0)
            section_progress.save()
    # Compare the number of MasterBonds to the number of MasterBondProgresses and see if we need to create any
    # MasterBondProgress objects.
    if create:
        master_bonds = (MasterBond.objects
                        .filter(Q(master_syllabus=master_syllabus) & (Q(masterbondsection__section=None) |
                                                                      Q(masterbondsection__section=section)))
                        .order_by('order'))
        #master_bond_progresses = (MasterBondProgress.objects
        #                          .filter(section_progress=section_progress, student=request.user)
        #                          .order_by('master_bond__order'))
        #if master_bond_progresses.count() < master_bonds.count():
        for master_bond in master_bonds:
            if not MasterBondProgress.objects.filter(master_bond=master_bond, student=request.user).exists():
                section_progress.completed = False
                section_progress.save()
                master_bond_progress = MasterBondProgress(master_bond=master_bond, student=request.user)
                master_bond_progress.save()
                master_bond_progress.section_progress.add(section_progress)
            master_bond_progress = MasterBondProgress.objects.get(master_bond=master_bond, student=request.user)
            if not (master_bond_progress.section_progress.filter(pk=section_progress.id,
                                                                 masterbondprogress__master_bond=master_bond,
                                                                 student=request.user).exists()):
                section_progress.completed = False
                section_progress.save()
                master_bond_progress.section_progress.add(section_progress)
    master_bond_progresses = (MasterBondProgress.objects
                              .filter(section_progress=section_progress, student=request.user)
                              .order_by('master_bond__order'))
    # Let's follow the same formula to retrieve or create the BondProgress objects.
    if create and not pre_stage:
        bonds = (Bond.objects
                 .filter(Q(segment__masterbond__master_syllabus=master_syllabus) &
                         (Q(segment__masterbond__masterbondsection__section=None) |
                          Q(segment__masterbond__masterbondsection__section=section)))
                 .exclude((Q(block__printableblock__scheduleblock__isnull=False) &
                           ~Q(block__printableblock__scheduleblock__schedule__term_length=section.term.length)))
                 .order_by('order'))
        bond_progresses = BondProgress.objects.filter(master_bond_progress__section_progress=section_progress,
                                                      student=request.user)
        #if bond_progresses.count() < bonds.count():
        for master_bond_progress in master_bond_progresses:
            bonds = (Bond.objects
                     .filter(segment__masterbond=master_bond_progress.master_bond)
                     .exclude((Q(block__printableblock__scheduleblock__isnull=False) &
                               ~Q(block__printableblock__scheduleblock__schedule__term_length=section.term.length)))
                     .order_by('order'))
            for bond in bonds:
                if hasattr(bond.block, 'printableblock') and not (BondProgress.objects
                        .filter(master_bond_progress=master_bond_progress, bond=bond, student=request.user).exists()):
                    section_progress.completed = False
                    section_progress.save()
                    bond_progress = BondProgress(master_bond_progress=master_bond_progress, bond=bond,
                                                 student=request.user)
                    bond_progress.save()
                elif hasattr(bond.block, 'responseblock') and not (ResponseProgress.objects
                        .filter(master_bond_progress=master_bond_progress, bond=bond, student=request.user).exists()):
                    section_progress.completed = False
                    section_progress.save()
                    questions = list(Question.objects.filter(response_block__bond=bond))
                    if len(questions) >= 1:
                        shuffle(questions)
                        a_available, p_available = get_attempts_and_points_available(master_syllabus,
                                                                                     bond.block.responseblock,
                                                                                     questions[0])
                        response_progress = ResponseProgress(master_bond_progress=master_bond_progress, bond=bond,
                                                             student=request.user, question=questions[0],
                                                             attempts_available=a_available,
                                                             points_available=p_available)
                        response_progress.save()
    else:
        bond_progresses = BondProgress.objects.filter(master_bond_progress__section_progress=section_progress,
                                                      student=request.user)
    return section_progress, master_bond_progresses, bond_progresses


def create_or_update_section_progress(request, master_syllabus, section, lti_launch_id):
    """
    Creates or updates the section progress object for the current user with the correct LTI launch ID.

    Parameters:
    :param (object) request:                    The request object (for session variables).
    :param (MasterSyllabus) master_syllabus:    The master syllabus to check (or create) against.
    :param (Section) section:                   The section to check (or create) against.
    :param (str) lti_launch_id:                 The LTI launch ID (needed to reconnect back to the LTI consumer).
    """
    try:
        section_progress = SectionProgress.objects.get(section__hash=section.hash, student=request.user)
        section_progress.lti_launch_id = lti_launch_id
    except SectionProgress.DoesNotExist:
        section_progress = SectionProgress(section=section, master_syllabus=master_syllabus, student=request.user,
                                           start_time=datetime.now(), progress=0.0, lti_launch_id=lti_launch_id)
    section_progress.save()


def get_attempts_and_points_available(master_syllabus, response_block, question):
    """
    Retrieves the number of attempts and points available for a master syllabus, block, and question combination.

    Parameters:
    :param (MasterSyllabus) master_syllabus:    The MasterSyllabus object to use for determining attempts and points
                                                available.
    :param (ResponseBlock) response_block:      The ResponseBlock object to use for determining attempts and points
                                                available.
    :param (Question) question:                 The Question object to use for determining attempts and points
                                                available.

    Returns:
    :return (int, int)                          - Returns a tuple representing the number of attempts and points
                                                available (as a tuple, respectively).
    """
    if question.max_attempts > 0:
        attempts_available = question.max_attempts
    elif response_block.max_attempts > 0:
        attempts_available = response_block.max_attempts
    else:
        attempts_available = master_syllabus.max_attempts
    if question.max_points > 0:
        points_available = question.max_points
    elif response_block.max_points > 0:
        points_available = response_block.max_points
    else:
        points_available = master_syllabus.max_points
    return attempts_available, points_available


def get_attempts_remaining(master_syllabus, bond_progress):
    """
    Retrieves the number of attempts remaining for a BondProgress (for a student).

    Parameters:
    :param (MasterSyllabus) master_syllabus:    The MasterSyllabus object to use for the maximum number of attempts.
    :param (BondProgress) bond_progress:        The BondProgress object used to retrieve the number of attempts
                                                    remaining.

    Returns:
    :return (int, str)                          - Returns a tuple representing the number of attempts remaining (the
                                                first value is an integer, the second value is a string).
    """
    if hasattr(bond_progress, 'responseprogress'):
        if bond_progress.responseprogress.question.max_attempts > 0:
            attempts_remaining = (bond_progress.responseprogress.question.max_attempts
                                  - bond_progress.responseprogress.attempts)
            return attempts_remaining, str(attempts_remaining)
        elif bond_progress.responseprogress.bond.block.responseblock.max_attempts > 0:
            attempts_remaining = (bond_progress.responseprogress.bond.block.responseblock.max_attempts
                                  - bond_progress.responseprogress.attempts)
            return attempts_remaining, str(attempts_remaining)
        elif master_syllabus.max_attempts > 0:
            attempts_remaining = master_syllabus.max_attempts - bond_progress.responseprogress.attempts
            return attempts_remaining, str(attempts_remaining)
    return 1, 'unlimited'


def get_bond_progress_next(section_progress, bond_progress):
    """
    Retrieves the BondProgress object that succeeds the one provided.

    Parameters:
    :param (SectionProgress) section_progress:  The SectionProgress object in which to retrieve the next BondProgress.
    :param (BondProgress) bond_progress:        The BondProgress object used to retrieve the next one.

    Returns:
    :return (BondProgress)                      - Returns a BondProgress object if one succeeds the one provided. None,
                                                otherwise.
    """
    bond_progress_next = (BondProgress.objects
                          .filter(master_bond_progress=bond_progress.master_bond_progress,
                                  bond__order__gt=bond_progress.bond.order, completed=False)
                          .order_by('bond__order')
                          .first())
    if bond_progress_next:
        return bond_progress_next
    else:  # Get next MasterBondProgress.
        master_bond_progress_next = (MasterBondProgress.objects
                                     .filter(section_progress=section_progress,
                                             master_bond__order__gt=bond_progress.master_bond_progress.master_bond.order,
                                             completed=False)
                                     .order_by('master_bond__order')
                                     .first())
        if master_bond_progress_next:
            if not master_bond_progress_next.start_time:
                master_bond_progress_next.start_time = datetime.now()
                master_bond_progress_next.save()
            return (BondProgress.objects
                    .filter(master_bond_progress=master_bond_progress_next, completed=False)
                    .order_by('bond__order')
                    .first())
    return None


def get_bond_progress_previous(section_progress, bond_progress):
    """
    Retrieves the BondProgress object that precedes the one provided.

    Parameters:
    :param (SectionProgress) section_progress:  The SectionProgress object in which to retrieve the previous
                                                BondProgress.
    :param (BondProgress) bond_progress:        The BondProgress object used to retrieve the previous one.

    Returns:
    :return (BondProgress)                      - Returns a BondProgress object if one precedes the one provided. None,
                                                otherwise.
    """
    bond_progress_prev = (BondProgress.objects
                          .filter(master_bond_progress=bond_progress.master_bond_progress,
                                  bond__order__lt=bond_progress.bond.order)
                          .order_by('bond__order')
                          .last())
    if bond_progress_prev:
        return bond_progress_prev
    else:  # Get previous MasterBondProgress.
        master_bond_progress_prev = (MasterBondProgress.objects
                                     .filter(section_progress=section_progress,
                                             master_bond__order__lt=bond_progress.master_bond_progress.master_bond.order)
                                     .order_by('master_bond__order')
                                     .last())
        if master_bond_progress_prev:
            return (BondProgress.objects
                    .filter(master_bond_progress=master_bond_progress_prev)
                    .order_by('bond__order')
                    .last())

    return None


def get_context_interactive(request, **kwargs):
    """
    Retrieves the context for the statically loaded portion of a syllabus.

    Parameters:
    :param (Request) request:   The request object (for session variables).

    Returns:
    :return (dict)              - Returns a dictionary object containing a context.
    """
    master_syllabus, section = get_master_syllabus_and_section(**kwargs)
    instructor = Profile.objects.get(pk=section.instructor.id)
    context = {'completed': is_complete_total(request, section), 'editable': True, 'instructor': instructor,
               'master_syllabus': master_syllabus, 'print_modal': has_optional_segments(master_syllabus, section),
               'section': section, 'term': section.term,
               'visible': is_syllabus_visible(request, master_syllabus, section)}
    return context


def get_context_print(request, **kwargs):
    """
    Retrieves the context for the dynamically loaded portion of a syllabus.

    Parameters:
    :param (Request) request:   The request object (for session variables).

    Returns:
    :return (dict)              - Returns a dictionary object containing a context.
    """
    master_syllabus, section = get_master_syllabus_and_section(**kwargs)
    segments = request.session.pop('print_segments', None)
    # Limit the master bonds returned to only those not associated with a section or those associated with the
    # selected section.
    q_objects = Q()
    q_objects.add(Q(master_syllabus=master_syllabus) & (Q(masterbondsection__section=None) |
                                                        Q(masterbondsection__section=section)), Q.AND)
    # Limit what segments are printed based on their optional status if we are rendering the print page.
    if segments:
        master_bonds = MasterBond.objects.filter(q_objects, (Q(segment__printing_optional=False) |
                                                             Q(segment_id__in=segments))).order_by('order')
    else:
        master_bonds = (MasterBond.objects
                        .filter(q_objects).exclude(segment__printing_optional=True)
                        .order_by('order'))
    instructor = Profile.objects.get(pk=section.instructor.id)
    context = {'instructor': instructor, 'master_bonds': master_bonds, 'master_syllabus': master_syllabus,
               'section': section, 'term': section.term, 'title': get_syllabus_title(section),
               'visible': is_syllabus_visible(request, master_syllabus, section)}
    return context


def get_context_traditional(request, **kwargs):
    """
    Retrieves the context for the statically loaded portion of a traditional syllabus.

    Parameters:
    :param (Request) request:   The request object (for session variables).

    Returns:
    :return (dict)              - Returns a dictionary object containing a context.
    """
    master_syllabus, section = get_master_syllabus_and_section(**kwargs)
    # Limit the master bonds returned to only those not associated with a section or those associated with the
    # selected section.
    master_bonds = MasterBond.objects.filter(Q(master_syllabus=master_syllabus) &
                                             (Q(masterbondsection__section=None) |
                                              Q(masterbondsection__section=section)))
    # Get instructor information.
    instructor = Profile.objects.get(pk=section.instructor.id)
    context = {'editable': False, 'instructor': instructor, 'master_bonds': master_bonds,
               'master_syllabus': master_syllabus, 'print_modal': has_optional_segments(master_syllabus, section),
               'section': section, 'term': section.term, 'title': get_syllabus_title(section),
               'visible': is_syllabus_visible(request, master_syllabus, section)}
    return context


def get_master_syllabus_and_section(**kwargs):
    """
    Retrieves the context for a syllabus.

    Returns:
    :return MasterSyllabus, Section         - Returns a master_syllabus and section object.
    """
    if 'section_hash' in kwargs:
        try:
            section = Section.objects.get(hash=kwargs['section_hash'])
        except Section.DoesNotExist:
            raise Http404
    elif 'course_code' in kwargs and 'section_code' in kwargs and 'term_code' in kwargs:
        try:
            section = Section.objects.get(course__course_code=kwargs['course_code'],
                                          section_code=kwargs['section_code'],
                                          term__term_code=kwargs['term_code'])
        except Section.DoesNotExist:
            raise Http404
    else:
        raise Http404
    try:
        master_syllabus = MasterSyllabus.objects.get(masterbond__masterbondsection__section=section)
    except MasterSyllabus.DoesNotExist:
        raise Http404
    return master_syllabus, section


def get_progress(section_progress):
    """
    Retrieves the MasterBondProgress, BondProgress, and progress percentage for a user.

    Parameters:
    :param (SectionProgress) section_progress:  The SectionProgress object in which to retrieve the progress data for.

    Returns:
    :return (tuple)                             - Returns a tuple containing a MasterBondProgress object, a BondProgress
                                                object, and the progress percentage for a user.
    """
    bond_progress_count = (BondProgress.objects
                           .filter(master_bond_progress__section_progress=section_progress)).count()
    master_bond_progresses = (MasterBondProgress.objects
                              .filter(section_progress=section_progress)
                              .order_by('master_bond__order'))
    position = 0
    total_points = 0
    master_bond_progress_to_return = None
    bond_progress_to_return = None
    for master_bond_progress in master_bond_progresses:
        bond_progresses = (BondProgress.objects
                           .filter(master_bond_progress=master_bond_progress)
                           .order_by('bond__order'))
        for bond_progress in bond_progresses:
            position += 1
            if hasattr(bond_progress, 'responseprogress'):
                total_points += bond_progress.responseprogress.points
            if not bond_progress.stop_time:
                bond_progress_to_return = bond_progress
                break
        if bond_progress_to_return:
            master_bond_progress_to_return = master_bond_progress
            break
    progress = round((position / bond_progress_count) * 100, 1)
    section_progress.progress = progress
    section_progress.save()
    return master_bond_progress_to_return, bond_progress_to_return, progress, total_points


def get_response_question(question):
    """
    Retrieves the type of response block (as that object type) based on the provided block, if it is a response block.

    Parameters:
    :param (Question) question:     The question to retrieve a question type for.

    Returns:
    :return (mixed)                 - Returns a specific type of question type as an object of that type OR None if the
                                    provided question type is not supported.
    """
    if hasattr(question, 'multiplechoicequestion'):
        return question.multiplechoicequestion
    elif hasattr(question, 'truefalsequestion'):
        return question.truefalsequestion
    else:
        return None


def get_segments_interactive(request, section_hash):
    """
    Retrieves the segments to be displayed within the content section of a syllabus. Used for viewing all segments and
    blocks at once.

    Parameters:
    :param (Request) request:   The request object (for session variables).
    :param (str) section_hash:  A hash value representing a section.

    Returns:
    :return (JSON)              - Returns a JSON object.
    """
    try:
        section_progress = SectionProgress.objects.get(section__hash=section_hash, student=request.user)
    except SectionProgress.DoesNotExist:
        master_syllabus, section = get_master_syllabus_and_section(section_hash=section_hash)
        section_progress, mbp, bp = create_or_get_progress(request, master_syllabus, section, True, True)
    segments = {}
    master_bond_progresses = (MasterBondProgress.objects
                              .filter(section_progress=section_progress)
                              .order_by('master_bond__order'))
    for master_bond_progress in master_bond_progresses:
        segments['#content-container-' + str(master_bond_progress.master_bond.segment.id)] = (
            reverse('viewer:interactive:segment', args=(section_progress.section.hash,
                                                        master_bond_progress.master_bond.segment.id)))
    return json.dumps(segments)


def get_segments_traditional(request, **kwargs):
    """
    Retrieves the segments to be displayed within the content section of a syllabus. Used for viewing all segments and
    blocks at once.

    Parameters:
    :param (Request) request:   The request object (for session variables).

    Returns:
    :return (JSON)              - Returns a JSON object.
    """
    context = get_context_traditional(request, **kwargs)
    segments = {}
    for master_bond in context['master_bonds']:
        segments['#segment-container-' + str(master_bond.segment.id)] = reverse('viewer:traditional:segment',
                                                                                args=(context['section'].course.course_code.lower(),
                                                                                      context['section'].section_code.lower(),
                                                                                      context['section'].term.term_code.lower(),
                                                                                      master_bond.segment.id))
    return json.dumps(segments)


def get_syllabus_title(section):
    """
    Retrieves the syllabus title, which is displayed within the browser tab/window and syllabus header.

    Parameters:
    :param (Section) section:   The Section object to get the title for.

    Returns:
    :return (str)               - Returns a string containing the syllabus title.
    """
    try:
        return (section.course.course_code + ' - ' + section.course.name + ' - ' + section.term.name +
                (' (ARCHIVED)' if section.term.archived else ''))
    except AttributeError:
        return ''


def get_total_points(master_bond_progress):
    """
    Retrieves the total points for a MasterBondProgress object.

    Parameters:
    :param (MasterBondProgress) master_bond_progress:       The MasterBondProgress object to calculate total points for.

    Returns:
    :return (int)                                           - Returns the total number of points for the requested
                                                            MasterBondProgress object.
    """
    points = 0
    response_progresses = ResponseProgress.objects.filter(master_bond_progress=master_bond_progress)
    for response_progress in response_progresses:
        points += response_progress.points
    return points


def get_total_points_possible(section_hash):
    """
    Retrieves the total points possible for an interactive syllabus.

    Parameters:
    :param (str) section_hash:      The section hash identify the interactive syllabus to calculate the total points
                                    for.

    Returns:
    :return (int)                   - Returns the total number of points for the requested interactive syllabus.
    """
    master_syllabus, section = get_master_syllabus_and_section(section_hash=section_hash)
    master_bonds = (MasterBond.objects
                    .filter(Q(master_syllabus=master_syllabus) & (Q(masterbondsection__section=None) |
                                                                  Q(masterbondsection__section=section)))
                    .order_by('order'))
    points = 0
    for master_bond in master_bonds:
        response_blocks = ResponseBlock.objects.filter(bond__segment=master_bond.segment)
        for response_block in response_blocks:
            questions = list(Question.objects.filter(response_block=response_block))
            if len(questions) >= 1:
                attempts_available, points_available = get_attempts_and_points_available(master_syllabus,
                                                                                         response_block, questions[0])
                points += points_available
    return points


def has_optional_segments(master_syllabus, section):
    """
    Determines whether a syllabus has any optional segments for printing.

    Parameters:
    :param (MasterSyllabus) master_syllabus:    The master syllabus to check.
    :param (Section) section:                   The section to check.

    Returns:
    :return Boolean                             - Returns True if this syllabus has optional segments. False, otherwise.
    """
    # Check and see if there are any optional segments (determines whether a dialog is displayed or the user can just
    # print immediately).
    q_objects = Q()
    q_objects.add(Q(printing_optional=True), Q.AND)
    q_objects.add(Q(masterbond__master_syllabus=master_syllabus), Q.AND)
    q_objects_or = Q()
    q_objects_or.add(Q(masterbond__masterbondsection__section=None), Q.AND)
    q_objects_or.add(Q(masterbond__masterbondsection__section=section), Q.OR)
    optional_segment_count = Segment.objects.filter(q_objects & q_objects_or).count()
    return optional_segment_count > 0


def is_complete(request, section):
    """
    Determines whether an interactive syllabus is complete or not for a user.

    Parameters:
    :param (object) request:                    The request object (for session variables).
    :param (Section) section:                   The section to check against.

    Returns:
    :return Boolean                             - Returns True if the syllabus is complete. False, otherwise.
    """
    if request.user.is_authenticated:
        section_progress = SectionProgress.objects.get(section=section, student=request.user)
        master_bond_progresses = MasterBondProgress.objects.filter(section_progress=section_progress,
                                                                   completed=False)
        if master_bond_progresses.exists():
            return False
        bond_progresses = BondProgress.objects.filter(master_bond_progress__section_progress=section_progress,
                                                      completed=False)
        if bond_progresses.exists():
            return False
    return True


def is_complete_total(request, section):
    """
    Determines whether an interactive syllabus is fully complete or not for a user.

    Parameters:
    :param (object) request:                    The request object (for session variables).
    :param (Section) section:                   The section to check against.

    Returns:
    :return Boolean                             - Returns True if the syllabus is fully complete. False, otherwise.
    """
    if request.user.is_authenticated:
        try:
            section_progress = SectionProgress.objects.get(section=section, student=request.user)
            return section_progress.completed == 1  # and is_complete(request, section)
        except SectionProgress.DoesNotExist:
            return False
    return True


def is_syllabus_visible(request, master_syllabus, section):
    """
    Determines whether a syllabus should be visible or not. If at least one segment is not visible, then the entire
    syllabus should not be visible to students.

    Parameters:
    :param (object) request:                    The request object (for session variables).
    :param (MasterSyllabus) master_syllabus:    The master syllabus to check.
    :param (Section) section:                   The section to check.

    Returns:
    :return Boolean                             - Returns True if at least one segment is not visible to students,
                                                False, otherwise.
    """
    q_objects = Q()
    q_objects.add(Q(master_syllabus=master_syllabus) & (Q(masterbondsection__section=None) |
                                                        Q(masterbondsection__section=section)), Q.AND)
    one_segment_not_visible = MasterBond.objects.filter(q_objects & Q(visibility=0)).exists()
    return not one_segment_not_visible
