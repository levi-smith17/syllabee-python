from django.urls import reverse


def render_generic_button(title, url_name, *args):
    """
    Retrieves a generic HTML opening button tag.

    Parameters:
    :param (string) title:          The text displayed within the title attribute of this button.
    :param (string) url_name:       A URL name used by the reverse() function. Must be a valid URL name in urls.py.

    Returns:
    :return (string)                - Returns HTML containing a properly formatted opening button tag.
    """
    return '<button type="button" class="offcanvas-btn btn btn-warning d-flex align-items-center" ' \
           'title="' + title + '" data-url="' + reverse(url_name, args=(*args,)) + \
           '" data-control="offcanvas" aria-controls="offcanvas-generic">'


def render_add_button(title, url_name, *args):
    """
    Retrieves a generic add button.

    Parameters:
    :param (string) title:          The text displayed within the title attribute of this button.
    :param (string) url_name:       A URL name used by the reverse() function. Must be a valid URL name in urls.py.

    Returns:
    :return (string)                - Returns HTML containing a properly formatted generic add button.
    """
    html = render_generic_button('Add ' + title, url_name, *args)
    html += '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" ' \
            'class="bi bi-plus-lg" viewBox="0 0 16 16"><path fill-rule="evenodd" ' \
            'd="M8 2a.5.5 0 0 1 .5.5v5h5a.5.5 0 0 1 0 1h-5v5a.5.5 0 0 ' \
            '1-1 0v-5h-5a.5.5 0 0 1 0-1h5v-5A.5.5 0 0 1 8 2Z"/></svg>'
    html += '</button>'
    return html


def render_arrange_button(title, url_name, *args):
    """
    Retrieves a generic arrange button.

    Parameters:
    :param (string) title:          The text displayed within the title attribute of this button.
    :param (string) url_name:       A URL name used by the reverse() function. Must be a valid URL name in urls.py.

    Returns:
    :return (string)                - Returns HTML containing a properly formatted generic edit button.
    """
    html = '<button type="button" class="modal-btn btn btn-warning d-flex align-items-center" ' \
           'title="Arrange ' + title + '" data-url="' + reverse(url_name, args=(*args,)) + \
           '" data-control="modal" aria-controls="modal-generic">'
    html += '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi ' \
            'bi-arrows-move" viewBox="0 0 16 16"><path fill-rule="evenodd" d="M7.646.146a.5.5 0 0 1 .708 0l2 2a.5.5 ' \
            '0 0 1-.708.708L8.5 1.707V5.5a.5.5 0 0 1-1 0V1.707L6.354 2.854a.5.5 0 1 1-.708-.708l2-2zM8 10a.5.5 0 0 ' \
            '1 .5.5v3.793l1.146-1.147a.5.5 0 0 1 .708.708l-2 2a.5.5 0 0 1-.708 0l-2-2a.5.5 0 0 1 .708-.708L7.5 ' \
            '14.293V10.5A.5.5 0 0 1 8 10zM.146 8.354a.5.5 0 0 1 0-.708l2-2a.5.5 0 1 1 .708.708L1.707 7.5H5.5a.5.5 0 ' \
            '0 1 0 1H1.707l1.147 1.146a.5.5 0 0 1-.708.708l-2-2zM10 8a.5.5 0 0 1 .5-.5h3.793l-1.147-1.146a.5.5 0 0 ' \
            '1 .708-.708l2 2a.5.5 0 0 1 0 .708l-2 2a.5.5 0 0 1-.708-.708L14.293 8.5H10.5A.5.5 0 0 1 10 8z"/></svg>'
    html += '</button>'
    return html


def render_copy_button(title, url_name, *args):
    """
    Retrieves a generic copy button.

    Parameters:
    :param (string) title:          The text displayed within the title attribute of this button.
    :param (string) url_name:       A URL name used by the reverse() function. Must be a valid URL name in urls.py.

    Returns:
    :return (string)                - Returns HTML containing a properly formatted generic copy button.
    """
    html = '<button type="button" class="modal-btn btn btn-warning d-flex align-items-center ms-0" ' \
           'title="Copy ' + title + '" data-url="' + reverse(url_name, args=(*args,)) + \
           '" data-control="modal" aria-controls="modal-buttons">'
    html += '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi ' \
            'bi-clipboard" viewBox="0 0 16 16"><path d="M4 1.5H3a2 2 0 0 0-2 2V14a2 2 0 0 0 2 2h10a2 2 0 0 0 ' \
            '2-2V3.5a2 2 0 0 0-2-2h-1v1h1a1 1 0 0 1 1 1V14a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V3.5a1 1 0 0 1 ' \
            '1-1h1v-1z"/><path d="M9.5 1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-3a.5.5 0 0 1-.5-.5v-1a.5.5 0 0 1 ' \
            '.5-.5h3zm-3-1A1.5 1.5 0 0 0 5 1.5v1A1.5 1.5 0 0 0 6.5 4h3A1.5 1.5 0 0 0 11 2.5v-1A1.5 1.5 0 0 0 9.5 ' \
            '0h-3z"/></svg>'
    html += '</button>'
    return html


def render_edit_button(title, url_name, *args):
    """
    Retrieves a generic edit button.

    Parameters:
    :param (string) title:          The text displayed within the title attribute of this button.
    :param (string) url_name:       A URL name used by the reverse() function. Must be a valid URL name in urls.py.

    Returns:
    :return (string)                - Returns HTML containing a properly formatted generic edit button.
    """
    html = render_generic_button('Edit ' + title, url_name, *args)
    html += '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" ' \
            'class="bi bi-pencil" viewBox="0 0 16 16"><path ' \
            'd="M12.146.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1 0 .708l-10 10a.5.5 0 0 ' \
            '1-.168.11l-5 2a.5.5 0 0 1-.65-.65l2-5a.5.5 0 0 1 .11-.168l10-10zM11.207 2.5 13.5 4.793 14.793 3.5 12.5 ' \
            '1.207 11.207 2.5zm1.586 3L10.5 3.207 4 9.707V10h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 ' \
            '.5.5v.5h.293l6.5-6.5zm-9.761 5.175-.106.106-1.528 3.821 3.821-1.528.106-.106A.5.5 0 0 1 5 ' \
            '12.5V12h-.5a.5.5 0 0 1-.5-.5V11h-.5a.5.5 0 0 1-.468-.325z"/></svg>'
    html += '</button>'
    return html
