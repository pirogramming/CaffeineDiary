from django.db import migrations, models


def set_nickname_to_username(apps, schema_editor):
    UserProfile = apps.get_model("accounts", "UserProfile")
    for profile in UserProfile.objects.select_related("user").all():
        if not profile.nickname:
            profile.nickname = profile.user.username
            profile.save(update_fields=["nickname"])


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="nickname",
            field=models.CharField(blank=True, default="", max_length=150),
            preserve_default=False,
        ),
        migrations.RunPython(set_nickname_to_username, migrations.RunPython.noop),
    ]
