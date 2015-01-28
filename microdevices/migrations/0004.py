# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ValidatedAssay'
        db.create_table(u'microdevices_validatedassay', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('organ_model', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['microdevices.OrganModel'])),
            ('assay', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assays.AssayModel'])),
        ))
        db.send_create_signal(u'microdevices', ['ValidatedAssay'])

        # Removing M2M table for field cell_type on 'OrganModel'
        db.delete_table(db.shorten_name(u'microdevices_organmodel_cell_type'))


    def backwards(self, orm):
        # Deleting model 'ValidatedAssay'
        db.delete_table(u'microdevices_validatedassay')

        # Adding M2M table for field cell_type on 'OrganModel'
        m2m_table_name = db.shorten_name(u'microdevices_organmodel_cell_type')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('organmodel', models.ForeignKey(orm[u'microdevices.organmodel'], null=False)),
            ('celltype', models.ForeignKey(orm[u'cellsamples.celltype'], null=False))
        ))
        db.create_unique(m2m_table_name, ['organmodel_id', 'celltype_id'])


    models = {
        u'assays.assaymodel': {
            'Meta': {'ordering': "('assay_name',)", 'object_name': 'AssayModel'},
            'assay_description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'assay_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'assay_protocol_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'assay_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assays.AssayModelType']"}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'assaymodel_created-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'assaymodel_modified-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'signed_off_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'assaymodel_signed_off_by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'signed_off_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'test_type': ('django.db.models.fields.CharField', [], {'max_length': '13'}),
            'version_number': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'assays.assaymodeltype': {
            'Meta': {'ordering': "('assay_type_name',)", 'object_name': 'AssayModelType'},
            'assay_type_description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'assay_type_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'assaymodeltype_created-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'assaymodeltype_modified-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'signed_off_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'assaymodeltype_signed_off_by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'signed_off_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
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
        u'cellsamples.organ': {
            'Meta': {'ordering': "('organ_name',)", 'object_name': 'Organ'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'organ_created-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'organ_modified-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'organ_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'signed_off_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'organ_signed_off_by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'signed_off_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
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
            'Meta': {'ordering': "('manufacturer_name',)", 'object_name': 'Manufacturer'},
            'contact_person': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'manufacturer_created-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'manufacturer_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'manufacturer_modified-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'signed_off_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'manufacturer_signed_off_by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'signed_off_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        u'microdevices.microdevice': {
            'Meta': {'ordering': "('device_name', 'organ')", 'object_name': 'Microdevice'},
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
            'signed_off_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'microdevice_signed_off_by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'signed_off_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'substrate_material': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'substrate_thickness': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        u'microdevices.microphysiologycenter': {
            'Meta': {'ordering': "('center_name',)", 'object_name': 'MicrophysiologyCenter'},
            'center_id': ('django.db.models.fields.CharField', [], {'default': "'-'", 'max_length': '20'}),
            'center_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'center_website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'contact_person': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'microphysiologycenter_created-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'microphysiologycenter_modified-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'signed_off_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'microphysiologycenter_signed_off_by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'signed_off_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        u'microdevices.organmodel': {
            'Meta': {'ordering': "('model_name', 'organ')", 'object_name': 'OrganModel'},
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
            'organ': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cellsamples.Organ']"}),
            'signed_off_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'organmodel_signed_off_by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'signed_off_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        u'microdevices.validatedassay': {
            'Meta': {'object_name': 'ValidatedAssay'},
            'assay': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assays.AssayModel']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organ_model': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['microdevices.OrganModel']"})
        }
    }

    complete_apps = ['microdevices']