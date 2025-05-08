from .models import *

def create_jobs_user(username, password, is_admin=False):
    if not username or not password:
        raise ValueError("Username và password không được để trống.")
    full_username = f"jobs_{username}"
    with transaction.atomic():
        user = User.objects.create(
            username=full_username,
            password=make_password(password)
        )
        jobs_user = JobsUser.objects.create(
            user=user,
            is_admin=is_admin
        )
    return jobs_user
