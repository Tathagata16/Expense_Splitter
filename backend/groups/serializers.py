from rest_framework import serializers
from .models import Group, GroupInvitation
from django.contrib.auth import get_user_model


class GroupCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = [
            "id",
            "group_name",
            "group_type",
            "description",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
        ]


from django.contrib.auth import get_user_model

User = get_user_model()


class GroupAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class GroupListSerializer(serializers.ModelSerializer):
    admin = GroupAdminSerializer(read_only=True)

    class Meta:
        model = Group
        fields = [
            "id",
            "group_name",
            "group_type",
            "description",
            "admin",
            "created_at",
        ]

User = get_user_model()
class UserSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
        ]


class GroupInviteSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()



#inviation serialiers...
class InvitationInviterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
        ]


class InvitationListSerializer(serializers.ModelSerializer):
    invited_by = InvitationInviterSerializer(read_only=True)

    group_id = serializers.IntegerField(source="group.id")

    group_name = serializers.CharField(source="group.group_name")

    class Meta:
        model = GroupInvitation

        fields = [
            "id",
            "group_id",
            "group_name",
            "invited_by",
            "created_at",
        ]


class GroupMemberSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()

class GroupDetailSerializer(serializers.ModelSerializer):
    admin = GroupAdminSerializer(read_only=True)

    member_count = serializers.SerializerMethodField()

    members = serializers.SerializerMethodField()

    is_admin = serializers.SerializerMethodField()

    class Meta:
        model = Group

        fields = [
            "id",
            "group_name",
            "group_type",
            "description",
            "admin",
            "member_count",
            "is_admin",
            "members",
            "created_at",
        ]

    def get_member_count(self, obj):
        return obj.memberships.filter(
            left_at__isnull=True
        ).count()

    def get_is_admin(self, obj):
        request = self.context.get("request")

        if request is None:
            return False

        return obj.admin == request.user

    def get_members(self, obj):
        active_memberships = obj.memberships.filter(
            left_at__isnull=True
        ).select_related("user")

        return [
            {
                "id": membership.user.id,
                "username": membership.user.username,
                "email": membership.user.email,
            }
            for membership in active_memberships
        ]    
   
    

