# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'MicrophysiologyCenter'
        db.create_table(u'microdevices_microphysiologycenter', (
            (u'id', self.gf('django.db.models.fields.AutoField')
             (primary_key=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(
                blank=True, related_name='microphysiologycenter_created-by', null=True, to=orm['auth.User'])),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')
             (auto_now_add=True, null=True, blank=True)),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(
                blank=True, related_name='microphysiologycenter_modified-by', null=True, to=orm['auth.User'])),
            ('modified_on', self.gf('django.db.models.fields.DateTimeField')
             (auto_now=True, null=True, blank=True)),
            ('locked', self.gf('django.db.models.fields.BooleanField')
             (default=False)),
            ('center_name', self.gf(
                'django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.CharField')
             (max_length=400, null=True, blank=True)),
            ('contact_person', self.gf('django.db.models.fields.CharField')
             (max_length=250, null=True, blank=True)),
            ('center_website', self.gf('django.db.models.fields.URLField')
             (max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal(u'microdevices', ['MicrophysiologyCenter'])

        # Adding model 'Manufacturer'
        db.create_table(u'microdevices_manufacturer', (
            (u'id', self.gf('django.db.models.fields.AutoField')
             (primary_key=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(
                blank=True, related_name='manufacturer_created-by', null=True, to=orm['auth.User'])),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')
             (auto_now_add=True, null=True, blank=True)),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(
                blank=True, related_name='manufacturer_modified-by', null=True, to=orm['auth.User'])),
            ('modified_on', self.gf('django.db.models.fields.DateTimeField')
             (auto_now=True, null=True, blank=True)),
            ('locked', self.gf('django.db.models.fields.BooleanField')
             (default=False)),
            ('manufacturer_name', self.gf(
                'django.db.models.fields.CharField')(max_length=100)),
            ('contact_person', self.gf('django.db.models.fields.CharField')
             (max_length=250, null=True, blank=True)),
            ('Manufacturer_website', self.gf('django.db.models.fields.URLField')(
                max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal(u'microdevices', ['Manufacturer'])

        # Adding model 'Microdevice'
        db.create_table(u'microdevices_microdevice', (
            (u'id', self.gf('django.db.models.fields.AutoField')
             (primary_key=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(
                blank=True, related_name='microdevice_created-by', null=True, to=orm['auth.User'])),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')
             (auto_now_add=True, null=True, blank=True)),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(
                blank=True, related_name='microdevice_modified-by', null=True, to=orm['auth.User'])),
            ('modified_on', self.gf('django.db.models.fields.DateTimeField')
             (auto_now=True, null=True, blank=True)),
            ('locked', self.gf('django.db.models.fields.BooleanField')
             (default=False)),
            ('device_name', self.gf(
                'django.db.models.fields.CharField')(max_length=200)),
            ('organ', self.gf('django.db.models.fields.related.ForeignKey')
             (to=orm['cellsamples.Organ'], null=True, blank=True)),
            ('center', self.gf('django.db.models.fields.related.ForeignKey')(
                to=orm['microdevices.MicrophysiologyCenter'], null=True, blank=True)),
            ('manufacturer', self.gf('django.db.models.fields.related.ForeignKey')(
                to=orm['microdevices.Manufacturer'], null=True, blank=True)),
            ('barcode', self.gf('django.db.models.fields.CharField')
             (max_length=200, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')
             (max_length=400, null=True, blank=True)),
            ('device_width', self.gf('django.db.models.fields.FloatField')
             (null=True, blank=True)),
            ('device_length', self.gf('django.db.models.fields.FloatField')
             (null=True, blank=True)),
            ('device_thickness', self.gf('django.db.models.fields.FloatField')
             (null=True, blank=True)),
            ('device_size_unit', self.gf('django.db.models.fields.CharField')
             (max_length=50, null=True, blank=True)),
            ('device_image', self.gf('django.db.models.fields.files.ImageField')(
                max_length=100, null=True, blank=True)),
            ('device_cross_section_image', self.gf('django.db.models.fields.files.ImageField')(
                max_length=100, null=True, blank=True)),
            ('device_fluid_volume', self.gf(
                'django.db.models.fields.FloatField')(null=True, blank=True)),
            ('device_fluid_volume_unit', self.gf('django.db.models.fields.CharField')(
                max_length=50, null=True, blank=True)),
            ('substrate_thickness', self.gf(
                'django.db.models.fields.FloatField')(null=True, blank=True)),
            ('substrate_material', self.gf('django.db.models.fields.CharField')(
                max_length=150, null=True, blank=True)),
        ))
        db.send_create_signal(u'microdevices', ['Microdevice'])

        # Adding model 'OrganModel'
        db.create_table(u'microdevices_organmodel', (
            (u'id', self.gf('django.db.models.fields.AutoField')
             (primary_key=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(
                blank=True, related_name='organmodel_created-by', null=True, to=orm['auth.User'])),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')
             (auto_now_add=True, null=True, blank=True)),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(
                blank=True, related_name='organmodel_modified-by', null=True, to=orm['auth.User'])),
            ('modified_on', self.gf('django.db.models.fields.DateTimeField')
             (auto_now=True, null=True, blank=True)),
            ('locked', self.gf('django.db.models.fields.BooleanField')
             (default=False)),
            ('model_name', self.gf(
                'django.db.models.fields.CharField')(max_length=200)),
            ('organ', self.gf('django.db.models.fields.related.ForeignKey')
             (to=orm['cellsamples.Organ'])),
            ('center', self.gf('django.db.models.fields.related.ForeignKey')(
                to=orm['microdevices.MicrophysiologyCenter'], null=True, blank=True)),
            ('device', self.gf('django.db.models.fields.related.ForeignKey')
             (to=orm['microdevices.Microdevice'], null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')
             (max_length=400, null=True, blank=True)),
        ))
        db.send_create_signal(u'microdevices', ['OrganModel'])

        # Adding M2M table for field cell_type on 'OrganModel'
        m2m_table_name = db.shorten_name(u'microdevices_organmodel_cell_type')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(
                verbose_name='ID', primary_key=True, auto_created=True)),
            ('organmodel', models.ForeignKey(
                orm[u'microdevices.organmodel'], null=False)),
            ('celltype', models.ForeignKey(
                orm[u'cellsamples.celltype'], null=False))
        ))
        db.create_unique(m2m_table_name, ['organmodel_id', 'celltype_id'])

    def backwards(self, orm):
        # Deleting model 'MicrophysiologyCenter'
        db.delete_table(u'microdevices_microphysiologycenter')

        # Deleting model 'Manufacturer'
        db.delete_table(u'microdevices_manufacturer')

        # Deleting model 'Microdevice'
        db.delete_table(u'microdevices_microdevice')

        # Deleting model 'OrganModel'
        db.delete_table(u'microdevices_organmodel')

        # Removing M2M table for field cell_type on 'OrganModel'
        db.delete_table(db.shorten_name(u'microdevices_organmodel_cell_type'))

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'cellsamples.cellsubtype': {
            'Meta': {'object_name': 'CellSubtype'},
            'cell_subtype': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'cellsamples.celltype': {
            'Meta': {'ordering': "('cell_type',)", 'object_name': 'CellType'},
            'cell_subtype': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cellsamples.CellSubtype']"}),
            'cell_type': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organ': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cellsamples.Organ']"}),
            'species': ('django.db.models.fields.CharField', [], {'default': "'Human'", 'max_length': '10', 'null': 'True', 'blank': 'True'})
        },
        u'cellsamples.organ': {
            'Meta': {'ordering': "('organ_name',)", 'object_name': 'Organ'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organ_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'microdevices.manufacturer': {
            'Manufacturer_website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'Meta': {'object_name': 'Manufacturer'},
            'contact_person': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'manufacturer_created-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'manufacturer_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'manufacturer_modified-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'microdevices.microdevice': {
            'Meta': {'object_name': 'Microdevice'},
            'barcode': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'center': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['microdevices.MicrophysiologyCenter']", 'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'microdevice_created-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'device_cross_section_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'device_fluid_volume': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'device_fluid_volume_unit': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'device_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'device_length': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'device_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'device_size_unit': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'device_thickness': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'device_width': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'manufacturer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['microdevices.Manufacturer']", 'null': 'True', 'blank': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'microdevice_modified-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'organ': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cellsamples.Organ']", 'null': 'True', 'blank': 'True'}),
            'substrate_material': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'substrate_thickness': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        u'microdevices.microphysiologycenter': {
            'Meta': {'object_name': 'MicrophysiologyCenter'},
            'center_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'center_website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'contact_person': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'microphysiologycenter_created-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'microphysiologycenter_modified-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'microdevices.organmodel': {
            'Meta': {'object_name': 'OrganModel'},
            'cell_type': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'organmodels'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['cellsamples.CellType']"}),
            'center': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['microdevices.MicrophysiologyCenter']", 'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'organmodel_created-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'device': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['microdevices.Microdevice']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'model_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'organmodel_modified-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'organ': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cellsamples.Organ']"})
        }
    }

    complete_apps = ['microdevices']
