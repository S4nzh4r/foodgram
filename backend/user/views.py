from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from djoser.serializers import SetPasswordSerializer
from django.shortcuts import get_object_or_404

from api.pagination import CustomPagination
from api.permissions import IsCurrentUserOrAdminOrReadOnly
from api.serializers import FollowSerializer
from recipe.models import Follow
from .models import CustomUser
from .serializers import (UserSerializer,
                          UserAvatarSerializer,
                          UserReadSerializer)


class UserViewSet(viewsets.ModelViewSet):
    """Viewset для пользователя / подписок."""

    queryset = CustomUser.objects.all()
    permission_classes = (IsCurrentUserOrAdminOrReadOnly, )
    pagination_class = CustomPagination

    def get_serializer_class(self):
        """Метод установки класс сеализатора."""
        if self.request.method in SAFE_METHODS:
            return UserReadSerializer
        return UserSerializer

    @action(detail=False,
            methods=['get'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        """Кастомное получение профиля пользователя."""
        user = self.request.user
        serializer = UserReadSerializer(user, context={'request': request})
        return Response(serializer.data)

    @action(['post'],
            detail=False,
            permission_classes=[IsAuthenticated])
    def set_password(self, request, *args, **kwargs):
        """Кастомное изменение пароля с помощью cериалайзера.

        из пакета djoser SetPasswordSerializer.
        """
        serializer = SetPasswordSerializer(
            data=request.data,
            context={'request': request})
        if serializer.is_valid(raise_exception=True):
            self.request.user.set_password(serializer.data["new_password"])
            self.request.user.save()
            return Response('Пароль успешно изменен',
                            status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(['put', 'delete'],
            detail=False,
            url_path=r'me/avatar',
            permission_classes=[IsAuthenticated])
    def avatar(self, request):
        """Кастомное добавление и удаление аватара."""
        user = request.user

        if request.method == 'PUT':
            serializer = UserAvatarSerializer(
                user, data=request.data, partial=True
            )
            if 'avatar' not in serializer.initial_data:
                return Response(
                    'Поле avatar обязательное!',
                    status=status.HTTP_400_BAD_REQUEST
                )

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        user.avatar.delete()
        user.save()
        return Response({"detail": "Аватар удален."},
                        status=status.HTTP_204_NO_CONTENT)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated,])
    def subscribe(self, request, *args, **kwargs):
        """Создание и удаление подписки."""
        author = get_object_or_404(CustomUser, id=self.kwargs.get('pk'))
        user = self.request.user
        if request.method == 'POST':
            serializer = FollowSerializer(
                data=request.data,
                context={'request': request, 'author': author})
            if serializer.is_valid(raise_exception=True):
                serializer.save(author=author, user=user)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response({'errors': 'Объект не найден'},
                            status=status.HTTP_404_NOT_FOUND)
        if Follow.objects.filter(author=author, user=user).exists():
            Follow.objects.get(author=author).delete()
            return Response('Успешная отписка',
                            status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Объект не найден'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False,
            methods=['get'],
            permission_classes=[IsAuthenticated,])
    def subscriptions(self, request):
        """Отображает все подписки пользователя."""
        follows = Follow.objects.filter(user=self.request.user)
        pages = self.paginate_queryset(follows)
        serializer = FollowSerializer(pages,
                                      many=True,
                                      context={'request': request})
        return self.get_paginated_response(serializer.data)
