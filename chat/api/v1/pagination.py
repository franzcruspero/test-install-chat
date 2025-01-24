from rest_framework.pagination import CursorPagination


class MessageCursorPagination(CursorPagination):
    page_size = 25
    ordering = "-created"
    cursor_query_param = "cursor"
