from rest_framework import serializers
from bioactivities.models import Bioactivity

# Old API
# class BioactivitiesSerializer(serializers.ModelSerializer):
#
#     class Meta(object):
#         model = Bioactivity
#         fields = ('compound', 'target',)

    # pk = serializers.Field()  # Note: `Field` is an untyped read-only field.
    # title = serializers.CharField(required=False,
    #                               max_length=100)
    # code = serializers.CharField(widget=widgets.Textarea,
    #                              max_length=100000)
    # linenos = serializers.BooleanField(required=False)
    #
    # def restore_object(self, attrs, instance=None):
    #     """
    #     Create or update a new snippet instance, given a dictionary
    #     of deserialized field values.
    #
    #     Note that if we don't define this method, then deserializing
    #     data will simply return a dictionary of items.
    #     """
    #     if instance:
    # Update existing instance
    #         instance.title = attrs.get('title', instance.title)
    #         instance.code = attrs.get('code', instance.code)
    #         instance.linenos = attrs.get('linenos', instance.linenos)
    #         return instance
    #
    # Create new instance
    #     return Bioactivity(**attrs)
