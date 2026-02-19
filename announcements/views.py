import json
import logging
import os

import firebase_admin
from firebase_admin import credentials, firestore, messaging
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.conf import settings
from employees.models import Employee
from .models import Announcement
from .serializers import AnnouncementSerializer

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Firebase Admin SDK – initialise once
# ---------------------------------------------------------------------------
_firebase_app = None


def _get_firebase_app():
    """Return the default Firebase Admin app, initialising it if necessary."""
    global _firebase_app
    if _firebase_app is not None:
        return _firebase_app

    try:
        _firebase_app = firebase_admin.get_app()
    except ValueError:
        try:
            # Look for service account key file
            key_path = os.environ.get(
                "GOOGLE_APPLICATION_CREDENTIALS",
                os.path.join(settings.BASE_DIR, "serviceAccountKey.json"),
            )
            if os.path.isfile(key_path):
                cred = credentials.Certificate(key_path)
                _firebase_app = firebase_admin.initialize_app(cred)
                logger.info("Firebase Admin SDK initialised with service account key.")
            else:
                logger.warning(
                    "Service account key not found at %s. "
                    "Download it from Firebase Console → Project Settings → Service accounts. "
                    "Push notifications will be unavailable.",
                    key_path,
                )
                return None
        except Exception as exc:
            logger.warning(
                "Firebase Admin SDK could not be initialised: %s. "
                "Push notifications will be unavailable.",
                exc,
            )
            return None
    return _firebase_app


# ---------------------------------------------------------------------------
# Helper – send FCM to every user that has a token in Firestore
# ---------------------------------------------------------------------------

def _send_fcm_notifications(announcement: Announcement):
    """Fetch all FCM tokens from Firestore and send a notification."""
    app = _get_firebase_app()
    if app is None:
        logger.warning("Firebase not initialised – skipping push notifications.")
        return

    try:
        db = firestore.client(app)
        users_ref = db.collection("users")
        docs = users_ref.stream()

        tokens = []
        for doc in docs:
            data = doc.to_dict()
            token = data.get("fcmToken")
            if token:
                tokens.append(token)

        if not tokens:
            logger.info("No FCM tokens found – skipping push.")
            return

        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=f"📢 {announcement.title}",
                body=announcement.content[:200],
            ),
            data={
                "announcement_id": str(announcement.id),
                "priority": announcement.priority,
            },
            webpush=messaging.WebpushConfig(
                notification=messaging.WebpushNotification(
                    icon="/notification-icon-192.png",
                    badge="/notification-badge-96.png",
                    tag=f"announcement-{announcement.id}",
                    renotify=True,
                ),
                fcm_options=messaging.WebpushFCMOptions(
                    link="/announcements",
                ),
            ),
            tokens=tokens,
        )

        response = messaging.send_each_for_multicast(message, app=app)
        logger.info(
            "FCM multicast: %d success, %d failure",
            response.success_count,
            response.failure_count,
        )
    except Exception as exc:
        logger.error("Error sending FCM notifications: %s", exc)


# ---------------------------------------------------------------------------
# API views
# ---------------------------------------------------------------------------

@api_view(['GET'])
def announcement_list(request):
    """Return all active announcements, newest first."""
    announcements = Announcement.objects.filter(is_active=True)
    serializer = AnnouncementSerializer(announcements, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def announcement_create(request):
    """Create an announcement and push-notify every registered user."""
    serializer = AnnouncementSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    employee = None
    email = request.headers.get('X-Employee-Email')
    if email:
        employee = Employee.objects.filter(email=email).first()

    announcement = serializer.save(created_by=employee)

    # Fire-and-forget push notifications
    _send_fcm_notifications(announcement)

    return Response(
        AnnouncementSerializer(announcement).data,
        status=status.HTTP_201_CREATED,
    )


@api_view(['GET'])
def announcement_detail(request, pk):
    """Return a single announcement."""
    try:
        announcement = Announcement.objects.get(pk=pk)
    except Announcement.DoesNotExist:
        return Response({"error": "Announcement not found"}, status=status.HTTP_404_NOT_FOUND)
    serializer = AnnouncementSerializer(announcement)
    return Response(serializer.data)


@api_view(['PUT', 'PATCH'])
def announcement_update(request, pk):
    """Update an existing announcement."""
    try:
        announcement = Announcement.objects.get(pk=pk)
    except Announcement.DoesNotExist:
        return Response({"error": "Announcement not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = AnnouncementSerializer(announcement, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    serializer.save()
    return Response(serializer.data)


@api_view(['DELETE'])
def announcement_delete(request, pk):
    """Soft-delete an announcement (set is_active = False)."""
    try:
        announcement = Announcement.objects.get(pk=pk)
    except Announcement.DoesNotExist:
        return Response({"error": "Announcement not found"}, status=status.HTTP_404_NOT_FOUND)

    announcement.is_active = False
    announcement.save()
    return Response({"message": "Announcement deleted"}, status=status.HTTP_204_NO_CONTENT)
