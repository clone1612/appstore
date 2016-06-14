from nextcloudappstore.core.models import App, AppRelease


class AppReleaseImporter:
    def import_release(self, info):
        self._update_release(info)
        if not older_version:
            self.update_app(info)

    def _update_release(self, info):
        release = AppRelease.objects.get(app__pk=app, version=version)
        release.libs = libs
        release.databases = databases
        release.licenses = licenses
        release.shell_commands = shell_commands
        release.php_min_version = php_min_version
        release.php_max_version = php_max_version
        release.platform_min_version = platform_min_version
        release.platform_max_version = platform_max_version
        release.min_int_size = min_int_size




    def update_app(self, info):
        app = App.objects.get(pk=app)
        app.categories = categories
        app.authors = authors
        app.user_docs = user_docs
        app.admin_docs = admin_docs
        app.developer_docs = developer_docs
        app.website = website
        app.issue_tracker = issue_tracker
        app.save()

        for name, lang in names:
            app.set_current_language(lang)
            app.name = name
            app.save()
        for description, lang in descriptions:
            app.set_current_language(lang)
            app.description = description
            app.save()
