from django.contrib.auth.models import User

DEFAULT_USERS = [
    ("manager", "manager@10086", True, True),   # admin
    ("test01", "groupmember01", False, False),
    ("test02", "groupmember02", False, False),
    ("test03", "groupmember03", False, False),
]

def seed_default_users():
    for username, password, is_staff, is_superuser in DEFAULT_USERS:
        if User.objects.filter(username=username).exists():
            continue
        u = User.objects.create_user(username=username, password=password)
        u.is_staff = is_staff
        u.is_superuser = is_superuser
        u.save()


