from djangovoice.utils import get_voice_extra_context


class VoiceMixin(object):
    def get_context_data(self, **kwargs):
        context = super(VoiceMixin, self).get_context_data(**kwargs)
        context.update(get_voice_extra_context())

        return context
