from django.conf import settings
from django.db import transaction
from django.http import Http404
from nextcloudappstore.core.api.v1.release.importer import AppReleaseImporter
from nextcloudappstore.core.api.v1.release.provider import AppReleaseProvider
from nextcloudappstore.core.api.v1.serializers import AppSerializer, \
    AppReleaseDownloadSerializer
from nextcloudappstore.core.models import App, AppRelease
from nextcloudappstore.core.permissions import UpdateDeletePermission
from nextcloudappstore.core.versioning import app_has_included_release
from rest_framework import authentication
from rest_framework.generics import DestroyAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class Apps(DestroyAPIView):
    authentication_classes = (authentication.BasicAuthentication,)
    permission_classes = (UpdateDeletePermission,)
    serializer_class = AppSerializer
    queryset = App.objects.all()

    def get(self, request, *args, **kwargs):
        apps = App.objects.prefetch_related('translations',
                                            'categories__translations',
                                            'categories', 'authors',
                                            'releases', 'screenshots',
                                            'releases__databases',
                                            'releases__libs').all()

        def app_filter(app):
            return app_has_included_release(app, self.kwargs['version'])

        working_apps = list(filter(app_filter, apps))
        serializer = self.get_serializer(working_apps, many=True)
        return Response(serializer.data)


class AppReleases(DestroyAPIView):
    authentication_classes = (authentication.BasicAuthentication,)
    permission_classes = (UpdateDeletePermission, IsAuthenticated)

    def put(self, request, app, version):
        serializer = AppReleaseDownloadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with(transaction.atomic()):
            # first make sure to operate on the correct instances and run
            # permission checks
            status = self._init_release(request, app, version)

            # if everything is fine, download the latest release and create
            # or update the models
            url = serializer.validated_data['download']
            provider = AppReleaseProvider()
            info = provider.get_release_info(app, version, url,
                                             settings.RELEASE_DOWNLOAD_ROOT)
            importer = AppReleaseImporter()
            importer.import_release(info)
        return Response(status=status)

    def _init_release(self, request, app, version):
        # if an app does not exist, the request should create it with its
        # owner set to the currently logged in user
        try:
            app = App.objects.get(pk=app)
        except App.DoesNotExist:
            app = App.objects.create(pk=app, owner=request.user)

        # if an app release does not exist, it must be checked if the
        # user is allowed to create it first
        try:
            self.get_object()
            status = 200
        except Http404:
            release = AppRelease()
            release.version = version
            release.app = app
            self.check_object_permissions(request, release)
            release.save()
            status = 201

        return status

    def get_object(self):
        release = AppRelease.objects.filter(version=self.kwargs['version'],
                                            app__id=self.kwargs['app'])
        release = get_object_or_404(release)
        self.check_object_permissions(self.request, release)
        return release
