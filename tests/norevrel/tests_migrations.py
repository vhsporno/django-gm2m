import re

import django

from .. import base


# basic migration tests
class MigrationTests(base.MigrationsTestCase):

    def test_makemigrations(self):
        self.makemigrations()

        mig_ctnt = re.sub(r'models\.AutoField\(.+?\)', 'models.AutoField()',
                          self.get_migration_content())
        mig_ctnt = re.sub(r"([\s\(])b'", r"\1'", mig_ctnt)

        if django.VERSION >= (1, 8):
            self.assertIn("""
    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Links',
            fields=[
                ('id', models.AutoField()),
                ('related_objects', gm2m.fields.GM2MField(through_fields=('gm2m_src', 'gm2m_tgt', 'gm2m_ct', 'gm2m_pk'))),
            ],
        ),
    ]""", mig_ctnt)

        else:
            # django < 1.7
            self.assertIn("""
    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Links',
            fields=[
                ('id', models.AutoField()),
                ('related_objects', gm2m.fields.GM2MField(through_fields=('gm2m_src', 'gm2m_tgt', 'gm2m_ct', 'gm2m_pk'))),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]""", mig_ctnt)

    def test_migrate_app(self):
        # just check that no exception is raised when calling migrate after
        # makemigrations
        self.makemigrations()
        self.migrate()

    def test_migrate_all(self):
        self.migrate(all=True)


class MultiMigrationTests(base.MultiMigrationsTestCase):

    def test_migrate_app(self):
        # generates initial migration file 0001_initial
        self.makemigrations()

        # adds a pk_maxlength parameter and generate 2nd migration
        self.replace('gm2m.GM2MField()',
                     'gm2m.GM2MField(pk_maxlength=50)')
        self.makemigrations()

        # renames the GM2MField
        self.replace('related_objects', 'projects_and_tasks')
        self.makemigrations()

        # check that no exception is raised when calling migrate
        self.migrate()