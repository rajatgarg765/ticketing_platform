import json
from django.views import View
from django.http import JsonResponse
from rest_framework.authtoken.models import Token
from users.models import User


class RegisterView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

        required_fields = ["email", "password", "confirm_password", "name", "gender"]

        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return JsonResponse(
                {"error": f"Missing fields: {', '.join(missing_fields)}"}, status=400
            )

        email = data.get("email")
        password = data.get("password")
        confirm_password = data.get("confirm_password")
        name = data.get("name")
        gender = data.get("gender")

        if not all([email, password, confirm_password, name, gender]):
            return JsonResponse({"error": "All fields are required and cannot be null"}, status=400)

        if password != confirm_password:
            return JsonResponse({"error": "Passwords do not match"}, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({"error": "Email already registered"}, status=400)

        user = User.objects.create(
            email=email,
            username=email,
            first_name=name
        )
        user.set_password(password)

        user.profile.gender = gender
        user.profile.save()
        user.save()

        token, _ = Token.objects.get_or_create(user=user)

        return JsonResponse({"token": token.key, "user_id": user.id}, status=201)


class LoginView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return JsonResponse({"error": "Email and Password are required"}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({"error": "Invalid credentials"}, status=400)

        if user.check_password(password):
            token, _ = Token.objects.get_or_create(user=user)
            return JsonResponse({"token": token.key, "user_id": user.id}, status=200)
        else:
            return JsonResponse({"error": "Invalid credentials"}, status=400)
