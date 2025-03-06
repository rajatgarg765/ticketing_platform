from django.contrib import admin
from events.models import Event, Attendance


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):

    list_display = [
        "title",
        "description",
        "date",
        "ticket_fee"
    ]


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):

    list_display = [
        "useremail",
        "eventtitle",
        "joined_at",
        "is_active"
    ]

    def useremail(self, obj):
        return obj.user.email if obj.user else '-'

    def eventtitle(self, obj):
        return obj.event.title if obj.event else '-'
