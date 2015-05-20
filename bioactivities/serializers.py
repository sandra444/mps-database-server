from rest_framework import serializers
from bioactivities.models import Bioactivity, Target, Assay
from compounds.models import Compound

class CompoundSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = Compound
        fields = ('name',)

class TargetSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = Target
        fields = ('name',)

class AssaySerializer(serializers.ModelSerializer):

    class Meta(object):
        model = Assay
        fields = ('chemblid',)


class BioactivitiesSerializer(serializers.ModelSerializer):

    compound = CompoundSerializer(read_only=True)
    target = TargetSerializer(read_only=True)
    assay = AssaySerializer(read_only=True)

    class Meta(object):
        model = Bioactivity
        fields = ('compound', 'target', 'organism', 'standard_name', 'operator', 'standardized_value', 'standardized_units', 'assay')

    # Old API
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
