from django.db import transaction
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth import get_user_model
from django.db.models import Q

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Group,
    GroupInvitation,
    GroupMember,
)
from .serializers import (GroupCreateSerializer, UserSearchSerializer, GroupInviteSerializer, InvitationListSerializer, GroupDetailSerializer)

from rest_framework import permissions

from django.utils import timezone


class GroupCreateView(generics.CreateAPIView):
    serializer_class = GroupCreateSerializer
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def perform_create(self, serializer):
        user = self.request.user

        group = serializer.save(
            created_by=user,
            admin=user,
        )

        GroupMember.objects.create(
            group=group,
            user=user,
        )



#returns the list of the groups that the user is a member of. This includes both direct and group types, along with the admin details for each group.


from .serializers import GroupListSerializer


class GroupListView(generics.ListAPIView):
    serializer_class = GroupListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        return Group.objects.filter(
            memberships__user=user,
            memberships__left_at__isnull=True,
        ).select_related(
            "admin"
        ).distinct()

User = get_user_model()


class UserSearchView(generics.ListAPIView):
    serializer_class = UserSearchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        query = self.request.query_params.get("q", "").strip()

        if not query:
            return User.objects.none()

        return User.objects.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query)
        ).exclude(
            id=self.request.user.id
        )[:10]

#group invite view to handle sending group invitations to users. It checks if the user is the admin of the group and if the invited user is not already a member before creating a new invitation.

class GroupInviteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, group_id):
        serializer = GroupInviteSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        invited_user_id = serializer.validated_data["user_id"]

        group = get_object_or_404(Group, id=group_id)

        # Only admin can invite
        if group.admin != request.user:
            return Response(
                {
                    "error": "Only the group admin can send invitations."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # Prevent inviting active members
        is_member = GroupMember.objects.filter(
            group=group,
            user_id=invited_user_id,
            left_at__isnull=True,
        ).exists()

        if is_member:
            return Response(
                {
                    "error": "User is already a member of this group."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Prevent duplicate pending invitations
        pending_invitation = GroupInvitation.objects.filter(
            group=group,
            invited_user_id=invited_user_id,
            status=GroupInvitation.InvitationStatus.PENDING,
        ).exists()

        if pending_invitation:
            return Response(
                {
                    "error": "User already has a pending invitation."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        invitation = GroupInvitation.objects.create(
            group=group,
            invited_user_id=invited_user_id,
            invited_by=request.user,
        )

        return Response(
            {
                "message": "Invitation sent successfully.",
                "invitation_id": invitation.id,
            },
            status=status.HTTP_201_CREATED,
        )


class InvitationListView(generics.ListAPIView):
    serializer_class = InvitationListSerializer

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            GroupInvitation.objects.filter(
                invited_user=self.request.user,
                status=GroupInvitation.InvitationStatus.PENDING,
            )
            .select_related(
                "group",
                "invited_by",
            )
            .order_by("-created_at")
        )


#view to accept invitations, which checks if the invitation is valid and pending, then adds the user to the group and updates the invitation status to accepted.


class AcceptInvitationView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, invitation_id):
        invitation = get_object_or_404(
            GroupInvitation,
            id=invitation_id,
            invited_user=request.user,
        )

        if invitation.status != GroupInvitation.InvitationStatus.PENDING:
            return Response(
                {
                    "error": "This invitation has already been processed."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        invitation.status = (
            GroupInvitation.InvitationStatus.ACCEPTED
        )

        invitation.responded_at = timezone.now()

        invitation.save()

        GroupMember.objects.create(
            group=invitation.group,
            user=request.user,
        )

        return Response(
            {
                "message": "Invitation accepted successfully."
            },
            status=status.HTTP_200_OK,
        )
    

#view to reject invitations, which checks if the invitation is valid and pending, then updates the invitation status to rejected without adding the user to the group.

class RejectInvitationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, invitation_id):
        invitation = get_object_or_404(
            GroupInvitation,
            id=invitation_id,
            invited_user=request.user,
        )

        if invitation.status != GroupInvitation.InvitationStatus.PENDING:
            return Response(
                {
                    "error": "This invitation has already been processed."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        invitation.status = (
            GroupInvitation.InvitationStatus.REJECTED
        )

        invitation.responded_at = timezone.now()

        invitation.save()

        return Response(
            {
                "message": "Invitation rejected successfully."
            },
            status=status.HTTP_200_OK,
        )
    
#view to leave group

class LeaveGroupView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, group_id):
        group = get_object_or_404(
            Group,
            id=group_id,
        )

        if group.admin == request.user:
            return Response(
                {
                    "error": "Admin cannot leave the group."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        membership = get_object_or_404(
            GroupMember,
            group=group,
            user=request.user,
            left_at__isnull=True,
        )

        membership.left_at = timezone.now()

        membership.save()

        return Response(
            {
                "message": "You have left the group."
            },
            status=status.HTTP_200_OK,
        )
    
#view to get a specific group details, including the admin information, member count, and whether the requesting user is the admin of the group.

class GroupDetailView(generics.RetrieveAPIView):
    serializer_class = GroupDetailSerializer

    permission_classes = [IsAuthenticated]

    lookup_url_kwarg = "group_id"

    def get_queryset(self):
        return (
            Group.objects.filter(
                memberships__user=self.request.user,
                memberships__left_at__isnull=True,
            )
            .select_related("admin")
            .prefetch_related("memberships__user")
            .distinct()
        )

