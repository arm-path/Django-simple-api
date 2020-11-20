from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthenticatedOrReadOnlyModify(BasePermission):

    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in SAFE_METHODS or
            request.user and
            request.user.is_authenticated and (obj.owner == request.user or request.user.is_staff)
        )


class IsAuthenticatedReadOnlyModify(BasePermission):
    """
    Все пользователи могут просматривать категории, получать категории
    и только администраторы системы могут Добавлять, Изменять, и удалять
    """

    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS or
            request.user.is_staff
        )
