from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from haystack.backends.whoosh_backend import WhooshSearchBackend, WhooshEngine
from whoosh.fields import NGRAM, Schema


class ConfigurableWhooshBackend(WhooshSearchBackend):
    """Extends the WhooshEngine class in Haystack so field defaults can be changed

    Currently, the following field defaults have been changed:
    The minsize for NGRAMs was changed from 3 to 1
    """

    def build_schema(self, fields):
        content_field_name, old_schema = super(
            ConfigurableWhooshBackend,
            self
        ).build_schema(fields)

        new_mapping = {}

        # Inefficient but flexible way of changing schema
        # Please note that the generator is called 'items()' not 'fields()'
        for field_name, field_class in old_schema.items():
            if type(field_class) != NGRAM:
                new_mapping[field_name] = field_class

        # Find and reset ngram
        for field_name, field_class in fields.items():
            if field_class.field_type == 'ngram':
                new_mapping[field_class.index_fieldname] = NGRAM(
                    minsize=1,
                    maxsize=15,
                    stored=field_class.stored,
                    field_boost=field_class.boost
                )

        return (content_field_name, Schema(**new_mapping))


class ConfigurableWhooshEngine(WhooshEngine):
    backend = ConfigurableWhooshBackend


class CaseInsensitiveModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        try:
            case_insensitive_username_field = '{}__iexact'.format(UserModel.USERNAME_FIELD)
            user = UserModel._default_manager.get(**{case_insensitive_username_field: username})
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user (#20760).
            UserModel().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
