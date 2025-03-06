from rest_framework.views import APIView
from django.http import JsonResponse
from django.utils import timezone
from .models import Event, Attendance
import json


class EventListView(APIView):
    def get(self, request):
        events = Event.objects.all().values("id", "title", "description", "date")
        return JsonResponse(list(events), safe=False)


class EventDetailView(APIView):
    def get(self, request, pk):
        try:
            event = Event.objects.values("id", "title", "description", "date", "ticket_fee").get(pk=pk)
            attendees = Attendance.objects.filter(event_id=pk).count()
            event["attendees_count"] = attendees
            return JsonResponse(event)
        except Event.DoesNotExist:
            return JsonResponse({"error": "Event not found"}, status=404)


class AttendEventView(APIView):
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

        event_id = data.get("event_id")
        attend = data.get("attend", True)
        attendees = []

        if not event_id:
            return JsonResponse({"error": "Event ID is required", "all_attendees": attendees}, status=400)

        try:
            event = Event.objects.get(pk=event_id)
            attendees = list(
                Attendance.objects.filter(event=event, is_active=True)
                .values_list("user__email", flat=True)
            )
        except Event.DoesNotExist:
            return JsonResponse(
                {"error": "Event not found"}, status=400
            )

        if request.user.profile.gender == "female":
            ticket_fee = float(event.ticket_fee) - (float(event.ticket_fee)*0.05)
        else:
            ticket_fee = float(event.ticket_fee)

        event_details = {
            "title": event.title,
            "ticket_price": ticket_fee,
            "date": event.date.date(),
            "time": event.date.time()
        }

        if event.date < timezone.now():
            return JsonResponse(
                {"error": "Cannot attend/unattend past events", "event_details": event_details, "all_attendees": attendees},
                status=400,
            )

        if attend:

            attendance, created = Attendance.objects.get_or_create(
                user=request.user, event=event, is_active=True
            )

            if not created:
                return JsonResponse(
                    {"message": "Already attending this event", "event_details": event_details, "all_attendees": attendees},
                    status=200,
                )
            else:
                message = "Attendance confirmed successfully"

        else:
            try:
                attendance = Attendance.objects.get(
                    user=request.user, event=event, is_active=True
                )
                attendance.is_active = False
                attendance.save()
                message = "Attendance removed successfully"
            except Attendance.DoesNotExist:
                return JsonResponse(
                    {"message": "You haven't requested to attend this event yet.", "event_details": event_details, "all_attendees": attendees},
                    status=400,
                )

        attendees = list(
            Attendance.objects.filter(event=event, is_active=True)
            .values_list("user__email", flat=True)
        )

        return JsonResponse(
            {
                "message": message,
                "event_details": event_details,
                "all_attendees": attendees,
            },
            status=200,
        )
