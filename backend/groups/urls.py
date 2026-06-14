from django.urls import path
from .views import (AcceptInvitationView, GroupCreateView, GroupDetailView, GroupInviteView, GroupListView, InvitationListView, LeaveGroupView, RejectInvitationView, UserSearchView)

urlpatterns = [
    path("", GroupListView.as_view(), name="group-list"),

    path("create/", GroupCreateView.as_view(), name="group-create"),

    path("users/search/",UserSearchView.as_view(),name="user-search"),

    path("<int:group_id>/invite/",
    GroupInviteView.as_view(),
    name="group-invite"),

    path("invitations/",
    InvitationListView.as_view(),
    name="invitation-list"),

    path("invitations/<int:invitation_id>/accept/",
    AcceptInvitationView.as_view(),
    name="accept-invitation",),

    path("invitations/<int:invitation_id>/reject/",
    RejectInvitationView.as_view(),
    name="reject-invitation"),

    path("<int:group_id>/leave/",
    LeaveGroupView.as_view(),
    name="leave-group"),

    path("<int:group_id>/",
    GroupDetailView.as_view(),
    name="group-detail"),
]





