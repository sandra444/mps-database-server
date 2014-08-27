# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Resource.resource_subtype'
        db.delete_column(u'resources_resource', 'resource_subtype_id')


    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'Resource.resource_subtype'
        raise RuntimeError("Cannot reverse this migration. 'Resource.resource_subtype' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'Resource.resource_subtype'
        db.add_column(u'resources_resource', 'resource_subtype',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['resources.ResourceSubtype']),
                      keep_default=False)


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
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'resources.resource': {
            'Meta': {'ordering': "['type', 'resource_name']", 'object_name': 'Resource'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'resource_created-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'resource_modified-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'resource_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '60'}),
            'resource_website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'signed_off_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'resource_signed_off_by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'signed_off_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['resources.ResourceType']"})
        },
        u'resources.resourcesubtype': {
            'Meta': {'ordering': "['name']", 'object_name': 'ResourceSubtype'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'resourcesubtype_created-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'resourcesubtype_modified-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'unique': 'True', 'max_length': '40'}),
            'signed_off_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'resourcesubtype_signed_off_by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'signed_off_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        u'resources.resourcetype': {
            'Meta': {'ordering': "['resource_type_name', 'resource_subtype']", 'object_name': 'ResourceType'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'resourcetype_created-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'resourcetype_modified-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'resource_subtype': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['resources.ResourceSubtype']"}),
            'resource_type_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'signed_off_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'resourcetype_signed_off_by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'signed_off_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['resources']