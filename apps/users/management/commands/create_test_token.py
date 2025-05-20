from django.core.management.base import BaseCommand
from apps.users.models import User
from rest_framework_simplejwt.tokens import RefreshToken

class Command(BaseCommand):
    help = '为指定用户或新创建的测试用户生成JWT令牌'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='要为其生成令牌的用户名')
        parser.add_argument('--create', action='store_true', help='如果指定，将创建一个新的测试用户')

    def handle(self, *args, **options):
        username = options.get('username')
        create = options.get('create')

        if create:
            # 创建新的测试用户
            username = 'testuser'
            password = 'testpassword123'
            try:
                user = User.objects.get(username=username)
                self.stdout.write(self.style.WARNING(f'用户 {username} 已存在，将使用此用户生成令牌'))
            except User.DoesNotExist:
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    is_active=True,
                    is_staff=True
                )
                self.stdout.write(self.style.SUCCESS(f'成功创建测试用户: {username}'))
        else:
            # 使用指定的用户名
            if not username:
                self.stdout.write(self.style.ERROR('请提供用户名或使用 --create 参数创建测试用户'))
                return
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'用户 {username} 不存在'))
                return

        # 生成JWT令牌
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        self.stdout.write(self.style.SUCCESS(f'为用户 {username} 生成的令牌:'))
        self.stdout.write(f'访问令牌: {access_token}')
        self.stdout.write(f'刷新令牌: {refresh_token}')
        self.stdout.write('\n测试命令:')
        self.stdout.write(f'curl -H "Authorization: Bearer {access_token}" http://localhost:8000/api/notifications/')
