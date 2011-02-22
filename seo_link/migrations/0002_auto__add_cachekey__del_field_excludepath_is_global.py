# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'CacheKey'
        db.create_table('seo_link_cachekey', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('site', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=1024)),
        ))
        db.send_create_signal('seo_link', ['CacheKey'])

        # Deleting field 'ExcludePath.is_global'
        db.delete_column('seo_link_excludepath', 'is_global')


    def backwards(self, orm):
        
        # Deleting model 'CacheKey'
        db.delete_table('seo_link_cachekey')

        # Adding field 'ExcludePath.is_global'
        db.add_column('seo_link_excludepath', 'is_global', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)


    models = {
        'seo_link.cachekey': {
            'Meta': {'object_name': 'CacheKey'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'site': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'seo_link.excludepath': {
            'Meta': {'unique_together': "(('type', 'pattern'),)", 'object_name': 'ExcludePath'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'pattern': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['seo_link.MatchType']"})
        },
        'seo_link.matchtype': {
            'Meta': {'object_name': 'MatchType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'seo_link.replacementtemplate': {
            'Meta': {'object_name': 'ReplacementTemplate'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'template_filename': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'seo_link.targetpath': {
            'Meta': {'object_name': 'TargetPath'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_external': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '1024'})
        },
        'seo_link.term': {
            'Meta': {'unique_together': "(('words', 'word_count'),)", 'object_name': 'Term'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ignore_pattern': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['seo_link.ExcludePath']", 'symmetrical': 'False', 'blank': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_case_sensitive': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'replacement_template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['seo_link.ReplacementTemplate']"}),
            'target_path': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['seo_link.TargetPath']", 'null': 'True', 'blank': 'True'}),
            'word_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'words': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['seo_link']
