
from math import ceil

from django.core.paginator import InvalidPage, EmptyPage, PageNotAnInteger

from pagination.page import Page
from pagination.settings import SHOW_FIRST_PAGE_WHEN_INVALID


class Paginator(object):

    page_class = Page

    def __init__(
            self,
            object_list,
            per_page,
            orphans=0,
            allow_empty_first_page=True,
            request=None):

        self.request = request
        self.object_list = object_list
        self.per_page = per_page
        self.orphans = orphans
        self.allow_empty_first_page = allow_empty_first_page
        self._num_pages = self._count = None

    def validate_number(self, number):
        "Validates the given 1-based page number."
        try:
            number = int(number)
        except ValueError:
            raise PageNotAnInteger('That page number is not an integer')
        if number < 1:
            if SHOW_FIRST_PAGE_WHEN_INVALID:
                number = 1
            else:
                raise EmptyPage('That page number is less than 1')
        if number > self.num_pages:
            if number == 1 and self.allow_empty_first_page:
                pass
            elif SHOW_FIRST_PAGE_WHEN_INVALID:
                number = 1
            else:
                raise EmptyPage('That page contains no results')
        return number

    def page(self, number):
        "Returns a Page object for the given 1-based page number."
        number = self.validate_number(number)
        bottom = (number - 1) * self.per_page
        top = bottom + self.per_page
        if top + self.orphans >= self.count:
            top = self.count
        return self.page_class(self.object_list[bottom:top], number, self)

    @property
    def count(self):
        "Returns the total number of objects, across all pages."
        if self._count is None:
            try:
                self._count = self.object_list.count()
            except (AttributeError, TypeError):
                # AttributeError if object_list has no count() method.
                # TypeError if object_list.count() requires arguments
                # (i.e. is of type list).
                self._count = len(self.object_list)
        return self._count

    @property
    def num_pages(self):
        "Returns the total number of pages."
        if self._num_pages is None:
            if self.count == 0 and not self.allow_empty_first_page:
                self._num_pages = 0
            else:
                hits = max(1, self.count - self.orphans)
                self._num_pages = int(ceil(hits / float(self.per_page)))
        return self._num_pages

    @property
    def page_range(self):
        """
        Returns a 1-based range of pages for iterating through within
        a template for loop.
        """
        return range(1, self.num_pages + 1)


def paginate(request, objects, per_page=12, paginator_class=Paginator):

    paginator = paginator_class(objects, per_page=per_page, request=request)

    try:
        return paginator.page(request.GET.get('page') or 1)
    except InvalidPage:
        return paginator.page(1)
