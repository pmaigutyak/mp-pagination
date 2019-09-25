
from pagination.paginator import Paginator


class PaginationMixin(object):

    paginator_class = Paginator

    def get_paginator(
            self,
            queryset,
            per_page,
            orphans=0,
            allow_empty_first_page=True):

        return self.paginator_class(
            queryset,
            per_page,
            orphans=orphans,
            allow_empty_first_page=allow_empty_first_page,
            request=self.request)
