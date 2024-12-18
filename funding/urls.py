from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.post_list, name='post_list'),  # 루트 URL에 게시글 목록 연결
    path('posts/', views.post_list, name='post_list'),  # 게시글 목록
    path('posts/<int:pk>/', views.post_detail, name='post_detail'),  # 상세 페이지
    path('posts/create/', views.post_create, name='post_create'),  # 게시글 작성
    path('posts/<int:pk>/edit/', views.post_edit, name='post_edit'),  # 게시글 수정
    path('posts/<int:pk>/delete/', views.post_delete, name='post_delete'),  # 게시글 삭제
    path('comments/<int:pk>/delete/', views.comment_delete, name='comment_delete'),  # 댓글 삭제 URL
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),  # 로그인
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),  # 로그아웃
]
