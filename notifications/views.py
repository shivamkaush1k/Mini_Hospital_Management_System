from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Notification


@login_required
def notification_list(request):

    notifications = (
        request.user.notifications
        .all()
        .order_by("-created_at")
    )

    unread_count = notifications.filter(is_read=False).count()

    return render(
        request,
        "notifications/list.html",
        {
            "notifications": notifications,
            "unread_count": unread_count,
        },
    )


@login_required
def mark_read(request, pk):

    notification = get_object_or_404(
        Notification,
        pk=pk,
        user=request.user,
    )

    if not notification.is_read:
        notification.is_read = True
        notification.save(update_fields=["is_read"])

    if notification.url:
        return redirect(notification.url)

    return redirect("notifications:list")


@login_required
def mark_all_read(request):

    request.user.notifications.filter(
        is_read=False
    ).update(is_read=True)

    return redirect("notifications:list")


@login_required
def delete_notification(request, pk):

    notification = get_object_or_404(
        Notification,
        pk=pk,
        user=request.user,
    )

    if request.method == "POST":
        notification.delete()

    return redirect("notifications:list")


@login_required
def unread_count(request):

    count = request.user.notifications.filter(
        is_read=False
    ).count()

    return JsonResponse(
        {
            "count": count
        }
    )