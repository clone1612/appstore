from django.db import models
from django.utils.translation import ugettext_lazy as _
from parler.models import TranslatedFields, TranslatableModel


class App(TranslatableModel):
    id = models.CharField(max_length=128, unique=True, primary_key=True,
                          verbose_name=_('Id'),
                          help_text=_('app id, same as the folder name'))
    categories = models.ManyToManyField('Category', verbose_name=_('Category'))
    translations = TranslatedFields(
        name=models.CharField(max_length=128, verbose_name=_('Name'),
                              help_text=_('Rendered app name for users')),
        description=models.TextField(verbose_name=_('Description'),
                                     help_text=_(
                                         'Will be rendered as Markdown'))
    )
    # resources
    user_docs = models.URLField(max_length=256, blank=True,
                                verbose_name=_('User documentation url'))
    admin_docs = models.URLField(max_length=256, blank=True,
                                 verbose_name=_('Admin documentation url'))
    developer_docs = models.URLField(max_length=256, blank=True,
                                     verbose_name=_(
                                         'Developer documentation url'))
    issue_tracker = models.URLField(max_length=256, blank=True,
                                    verbose_name=_('Issue tracker url'))
    website = models.URLField(max_length=256, blank=True,
                              verbose_name=_('Homepage'))
    created = models.DateTimeField(auto_now_add=True, editable=False,
                                   verbose_name=_('Created at'))
    last_modified = models.DateTimeField(auto_now=True, editable=False,
                                         verbose_name=_('Updated at'))
    owner = models.ForeignKey('auth.User', verbose_name=_('App owner'),
                              on_delete=models.CASCADE,
                              related_name='owned_apps')
    co_maintainers = models.ManyToManyField('auth.User',
                                            verbose_name=_('Co-Maintainers'),
                                            related_name='co_maintained_apps',
                                            blank=True)
    recommendations = models.ManyToManyField('auth.User',
                                             verbose_name=_('Recommendations'),
                                             related_name='recommended_apps',
                                             blank=True)

    class Meta:
        verbose_name = _('App')
        verbose_name_plural = _('Apps')

    def __str__(self):
        return self.name

    def can_update(self, user):
        return self.owner == user or user in self.co_maintainers.all()

    def can_delete(self, user):
        return self.owner == user


class AppRelease(models.Model):
    version = models.CharField(max_length=128, verbose_name=_('Version'),
                               help_text=_(
                                   'Version follows Semantic Versioning'))
    app = models.ForeignKey('App', on_delete=models.CASCADE,
                            verbose_name=_('App'), related_name='releases')
    authors = models.ManyToManyField('Author', verbose_name=_('Authors'))
    # dependencies
    php_extensions = models.ManyToManyField('PhpExtension',
                                  through='PhpExtensionDependency',
                                  verbose_name=_('PHP extension dependency'),
                                  blank=True)
    databases = models.ManyToManyField('Database',
                                       through='DatabaseDependency',
                                       verbose_name=_('Database dependency'),
                                       blank=True)
    licenses = models.ManyToManyField('License',
                                      verbose_name=_('License'))
    shell_commands = models.ManyToManyField('ShellCommand', verbose_name=_(
        'Shell command dependency'), blank=True)
    php_min_version = models.CharField(max_length=128,
                                       verbose_name=_('PHP minimum version'),
                                       blank=True)
    php_max_version = models.CharField(max_length=128, blank=True,
                                       verbose_name=_('PHP maximum version'))
    platform_min_version = models.CharField(max_length=128,
                                            verbose_name=_(
                                                'Platform minimum version'))
    platform_max_version = models.CharField(max_length=128, blank=True,
                                            verbose_name=_(
                                                'Platform maximum version'))
    min_int_size = models.IntegerField(blank=True, default=0,
                                       verbose_name=_(
                                           'Minimum Integer Bits'),
                                       help_text=_(
                                           'e.g. 32 for 32bit '
                                           'Integers'))
    checksum = models.CharField(max_length=64,
                                verbose_name=_('SHA256 checksum'))
    download = models.URLField(max_length=256, blank=True,
                               verbose_name=_('Archive download Url'))
    created = models.DateTimeField(auto_now_add=True, editable=False,
                                   verbose_name=_('Created at'))
    last_modified = models.DateTimeField(auto_now=True, editable=False,
                                         verbose_name=_('Updated at'))

    class Meta:
        verbose_name = _('App Release')
        verbose_name_plural = _('App Releases')
        unique_together = (('app', 'version'),)

    def can_update(self, user):
        return self.app.owner == user or user in self.app.co_maintainers.all()

    def can_delete(self, user):
        return self.can_update(user)

    def __str__(self):
        return '%s %s' % (self.app, self.version)


class Screenshot(models.Model):
    url = models.URLField(max_length=256, verbose_name=_('Image url'))
    app = models.ForeignKey('App', on_delete=models.CASCADE,
                            verbose_name=_('App'), related_name='screenshots')
    ordering = models.IntegerField(verbose_name=_('Ordering'))

    class Meta:
        verbose_name = _('Screenshot')
        verbose_name_plural = _('Screenshots')
        ordering = ['ordering']

    def __str__(self):
        return self.url


class Author(models.Model):
    name = models.CharField(max_length=256, verbose_name=_('Full name'))
    mail = models.EmailField(max_length=256, blank=True,
                             verbose_name=_('Mail address'))
    homepage = models.URLField(max_length=256, blank=True,
                               verbose_name=_('Homepage'))

    class Meta:
        verbose_name = _('Author')
        verbose_name_plural = _('Authors')

    def __str__(self):
        return self.name


class ShellCommand(models.Model):
    name = models.CharField(max_length=128, unique=True, primary_key=True,
                            verbose_name=_('Shell Command'),
                            help_text=_(
                                'Name of a required shell command, e.g. grep'))

    class Meta:
        verbose_name = _('Shell Command')
        verbose_name_plural = _('Shell Commands')

    def __str__(self):
        return self.name


class Category(TranslatableModel):
    id = models.CharField(max_length=128, unique=True, primary_key=True,
                          help_text=_(
                              'Category id which is used to identify a '
                              'category. Used to identify categories when '
                              'uploading an app'), verbose_name=_('Id'))
    created = models.DateTimeField(auto_now_add=True, editable=False,
                                   verbose_name=_('Created at'))
    last_modified = models.DateTimeField(auto_now=True, editable=False,
                                         verbose_name=_('Updated at'))
    translations = TranslatedFields(
        name=models.CharField(max_length=128, help_text=_(
            'Category name which will be presented to the user'),
                              verbose_name=_('Name'))
    )

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    def __str__(self):
        return self.name


class License(models.Model):
    id = models.CharField(max_length=128, unique=True, primary_key=True,
                          verbose_name=_('Id'),
                          help_text=_(
                              'Key which is used to identify a license'))
    name = models.CharField(max_length=128, verbose_name=_('Name'),
                            help_text=_(
                                'License name which will be presented to '
                                'the user'))

    class Meta:
        verbose_name = _('License')
        verbose_name_plural = _('Licenses')

    def __str__(self):
        return self.name


class Database(models.Model):
    id = models.CharField(max_length=128, unique=True, primary_key=True,
                          verbose_name=_('Id'),
                          help_text=_(
                              'Key which is used to identify a database'))
    name = models.CharField(max_length=128, verbose_name=_('Name'),
                            help_text=_(
                                'Database name which will be presented to '
                                'the user'))

    class Meta:
        verbose_name = _('Database')
        verbose_name_plural = _('Databases')

    def __str__(self):
        return self.name


class DatabaseDependency(models.Model):
    app_release = models.ForeignKey('AppRelease', on_delete=models.CASCADE,
                                    verbose_name=_('App release'),
                                    related_name='databasedependencies')
    database = models.ForeignKey('Database', on_delete=models.CASCADE,
                                 verbose_name=_('Database'))
    min_version = models.CharField(max_length=128,
                                   verbose_name=_(
                                       'Database minimum version'))
    max_version = models.CharField(max_length=128, blank=True,
                                   verbose_name=_(
                                       'Database maximum version'))

    class Meta:
        verbose_name = _('Database Dependency')
        verbose_name_plural = _('Database Dependencies')
        unique_together = (('app_release', 'database', 'min_version',
                            'max_version'),)

    def __str__(self):
        return '%s: %s >=%s, <=%s' % (self.app_release, self.database,
                                      self.min_version,
                                      self.max_version)


class PhpExtension(models.Model):
    id = models.CharField(max_length=128, unique=True, primary_key=True,
                          verbose_name=_('PHP extension'),
                          help_text=_('e.g. libxml'))

    class Meta:
        verbose_name = _('PHP Extension')
        verbose_name_plural = _('PHP Extensions')

    def __str__(self):
        return self.id


class PhpExtensionDependency(models.Model):
    app_release = models.ForeignKey('AppRelease', on_delete=models.CASCADE,
                                    verbose_name=_('App Release'),
                                    related_name='phpextensiondependencies')
    php_extension = models.ForeignKey('PhpExtension', on_delete=models.CASCADE,
                                      verbose_name=_('PHP Extension'))
    min_version = models.CharField(max_length=128,
                                   verbose_name=_(
                                       'Extension minimum version'))
    max_version = models.CharField(max_length=128,
                                   verbose_name=_(
                                       'Extension maximum version'),
                                   blank=True)

    class Meta:
        verbose_name = _('PHP Extension Dependency')
        verbose_name_plural = _('PHP Extension Dependencies')
        unique_together = (('app_release', 'php_extension', 'min_version',
                            'max_version'),)

    def __str__(self):
        return '%s: %s >=%s, <=%s' % (self.app_release.app, self.php_extension,
                                      self.min_version,
                                      self.max_version)
