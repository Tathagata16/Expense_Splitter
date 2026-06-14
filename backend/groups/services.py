from django.db import transaction

from .models import Group, GroupMember


@transaction.atomic
def get_or_create_direct_group(
    user1,
    user2,
):
    direct_groups = (
        Group.objects.filter(
            group_type="DIRECT",
            memberships__user=user1,
            memberships__left_at__isnull=True,
        )
        .filter(
            memberships__user=user2,
            memberships__left_at__isnull=True,
        )
        .distinct()
    )

    existing_group = direct_groups.first()

    if existing_group:
        return existing_group

    group = Group.objects.create(
        group_name=(
            f"{user1.username}-"
            f"{user2.username}"
        ),

        group_type="DIRECT",

        created_by=user1,

        admin=user1,

        description="Direct expense group",
    )

    GroupMember.objects.create(
        group=group,
        user=user1,
    )

    GroupMember.objects.create(
        group=group,
        user=user2,
    )

    return group