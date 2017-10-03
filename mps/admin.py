from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group


class MyUserAdmin(UserAdmin):
    """Revised User Admin interface"""
    save_on_top = True
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'all_groups',
        'is_active',
        'is_staff',
        'is_superuser'
    )

    def all_groups(self, obj):
        contents = u''
        trigger = u''
        if obj.groups.all().count():
            contents = u'<br>'.join([group.name for group in obj.groups.all().order_by('name')])
            trigger = u'<a href="javascript:void(0)" onclick=$("#groups_{0}").toggle()>Show/Hide Groups</a>'.format(obj.pk)
        return u'{0}<div hidden id="groups_{1}">{2}</div>'.format(trigger, obj.pk, contents)

    all_groups.allow_tags = True

admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)


class MyGroupAdmin(GroupAdmin):
    """Revised Group Admin interface"""
    save_on_top = True
    list_display = (
        'name',
        'all_users'
    )

    def all_users(self, obj):
        contents = u''
        trigger = u''
        if obj.user_set.all().count():
            contents = u'<br>'.join([' '.join([user.first_name, user.last_name]) for user in obj.user_set.all().order_by('username')])
            trigger = u'<a href="javascript:void(0)" onclick=$("#users_{0}").toggle()>Show/Hide Users</a>'.format(obj.pk)
        return u'{0}<div hidden id="users_{1}">{2}</div>'.format(trigger, obj.pk, contents)

    all_users.allow_tags = True

admin.site.unregister(Group)
admin.site.register(Group, MyGroupAdmin)
