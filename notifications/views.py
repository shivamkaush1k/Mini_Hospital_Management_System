from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .models import Notification


@login_required
def notification_list(request):

    notifications = request.user.notifications.all()
    return render(request,"notifications/list.html",{"notifications": notifications})


@login_required
def mark_read(request, pk):

    notification = request.user.notifications.get(pk=pk)

    notification.is_read = True

    notification.save()

    if notification.url:
        return redirect(notification.url)

    return redirect("notifications:list")