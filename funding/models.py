from django.db import models
from django.contrib.auth.models import User
from django.db import models
# Create your models here.

class Comment(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='comments')  # 게시글과 연결
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 댓글 작성자
    content = models.TextField()  # 댓글 내용
    created_at = models.DateTimeField(auto_now_add=True)  # 댓글 작성 시간

    def __str__(self):
        return f"댓글 by {self.user.username} on {self.post.title}"

class Post(models.Model):
    title = models.CharField(max_length=100)  # 게시글 제목
    content = models.TextField()  # 게시글 내용
    price = models.PositiveIntegerField()  # 가격
    capacity = models.PositiveIntegerField(default=10)  # 모집 인원
    current_applicants = models.PositiveIntegerField(default=0)  # 현재 지원자 수
    created_at = models.DateTimeField(auto_now_add=True)  # 생성 시간
    updated_at = models.DateTimeField(auto_now=True)  # 수정 시간
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')  # 작성자
    
    def __str__(self):
        return self.title

    def is_full(self):
        return self.current_applicants >= self.capacity  # 모집 마감 여부
    
class Support(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)  # 지원 게시글
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 지원한 사용자

    class Meta:
        unique_together = ('post', 'user')  # 중복 지원 방지