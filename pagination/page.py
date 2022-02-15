
import functools
import collections

from django.template.loader import render_to_string

from pagination.settings import MARGIN_PAGES_DISPLAYED, PAGE_RANGE_DISPLAYED


class PageRepresentation(int):
    def __new__(cls, x, querystring):
        obj = int.__new__(cls, x)
        obj.querystring = querystring
        return obj


def add_page_querystring(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        if isinstance(result, int):
            querystring = self._other_page_querystring(result)
            return PageRepresentation(result, querystring)
        elif isinstance(result, collections.Iterable):
            new_result = []
            for number in result:
                if isinstance(number, int):
                    querystring = self._other_page_querystring(number)
                    new_result.append(PageRepresentation(number, querystring))
                else:
                    new_result.append(number)
            return new_result
        return result

    return wrapper


class Page(object):

    template = 'pagination.html'

    def __init__(self, object_list, number, paginator):

        self.object_list = object_list
        self.paginator = paginator

        if paginator.request:
            self.base_queryset = self.paginator.request.GET.copy()

        self.number = PageRepresentation(number, self._other_page_querystring(number))

    def __repr__(self):
        return '<Page %s of %s>' % (self.number, self.paginator.num_pages)

    def has_next(self):
        return self.number < self.paginator.num_pages

    def has_previous(self):
        return self.number > 1

    def has_other_pages(self):
        return self.has_previous() or self.has_next()

    @add_page_querystring
    def next_page_number(self):
        return self.number + 1

    @add_page_querystring
    def previous_page_number(self):
        return self.number - 1

    def start_index(self):
        """
        Returns the 1-based index of the first object on this page,
        relative to total objects in the paginator.
        """
        # Special case, return zero if no items.
        if self.paginator.count == 0:
            return 0
        return (self.paginator.per_page * (self.number - 1)) + 1

    def end_index(self):
        """
        Returns the 1-based index of the last object on this page,
        relative to total objects found (hits).
        """
        # Special case for the last page because there can be orphans.
        if self.number == self.paginator.num_pages:
            return self.paginator.count
        return self.number * self.paginator.per_page

    @add_page_querystring
    def pages(self):
        if self.paginator.num_pages <= PAGE_RANGE_DISPLAYED:
            return range(1, self.paginator.num_pages + 1)
        result = []
        left_side = PAGE_RANGE_DISPLAYED / 2
        right_side = PAGE_RANGE_DISPLAYED - left_side
        if self.number > self.paginator.num_pages - PAGE_RANGE_DISPLAYED / 2:
            right_side = self.paginator.num_pages - self.number
            left_side = PAGE_RANGE_DISPLAYED - right_side
        elif self.number < PAGE_RANGE_DISPLAYED / 2:
            left_side = self.number
            right_side = PAGE_RANGE_DISPLAYED - left_side
        for page in range(1, self.paginator.num_pages + 1):
            if page <= MARGIN_PAGES_DISPLAYED:
                result.append(page)
                continue
            if page > self.paginator.num_pages - MARGIN_PAGES_DISPLAYED:
                result.append(page)
                continue
            if (page >= self.number - left_side) and (page <= self.number + right_side):
                result.append(page)
                continue
            if result[-1]:
                result.append(None)

        return result

    def _other_page_querystring(self, page_number):
        """
        Returns a query string for the given page, preserving any
        GET parameters present.
        """
        if self.paginator.request:
            self.base_queryset['page'] = page_number
            return self.base_queryset.urlencode()

        # raise Warning("You must supply Paginator() with the request object for a proper querystring.")
        return 'page=%s' % page_number

    def render(self):
        return render_to_string(self.template, {
            'current_page': self,
            'page_obj': self,  # Issue 9 https://github.com/jamespacileo/django-pure-pagination/issues/9
                               # Use same naming conventions as Django
        })

    @property
    def next_page_url(self):

        if not self.has_next():
            return ''

        return '{}?{}'.format(
            self.paginator.request.path,
            self.next_page_number().querystring)
