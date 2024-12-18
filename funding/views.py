from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt  # CSRF 비활성화 (개발 단계에서만 사용)
from django.contrib.auth.decorators import login_required  # 로그인 여부 확인
from .models import Post, Support, Comment  # 필요한 모델 임포트
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

# 기본 페이지
def index(request):
    return HttpResponse("Hello, world! Funding 앱에 오신 것을 환영합니다.")

# 게시글 목록
def post_list(request):
    try:
        # 모든 게시글 조회
        posts = Post.objects.all()

        # 검색 처리
        query = request.GET.get('q', '')
        if query:
            posts = posts.filter(title__icontains=query)

        # 필터 처리
        min_price = request.GET.get('min_price', None)
        max_price = request.GET.get('max_price', None)
        min_capacity = request.GET.get('min_capacity', None)
        max_capacity = request.GET.get('max_capacity', None)

        if min_price:
            try:
                posts = posts.filter(price__gte=float(min_price))  # 입력값 검증
            except ValueError:
                raise ValueError("최소 가격은 숫자여야 합니다.")
        if max_price:
            try:
                posts = posts.filter(price__lte=float(max_price))
            except ValueError:
                raise ValueError("최대 가격은 숫자여야 합니다.")
        if min_capacity:
            try:
                posts = posts.filter(capacity__gte=int(min_capacity))
            except ValueError:
                raise ValueError("최소 모집 인원은 정수여야 합니다.")
        if max_capacity:
            try:
                posts = posts.filter(capacity__lte=int(max_capacity))
            except ValueError:
                raise ValueError("최대 모집 인원은 정수여야 합니다.")

        # 정렬 처리
        sort_by = request.GET.get('sort', 'created_at')
        valid_sort_fields = ['created_at', 'price', 'capacity']
        if sort_by not in valid_sort_fields:
            raise ValueError("유효하지 않은 정렬 기준입니다.")
        posts = posts.order_by(sort_by)

        # 페이지네이션 처리
        paginator = Paginator(posts, 10)  # 한 페이지에 10개의 게시글
        page_number = request.GET.get('page')
        try:
            page_obj = paginator.get_page(page_number)
        except PageNotAnInteger:
            raise ValueError("페이지 번호는 정수여야 합니다.")
        except EmptyPage:
            page_obj = paginator.get_page(paginator.num_pages)  # 마지막 페이지 반환

    except ValueError as e:
        # 예외 발생 시 오류 메시지 반환
        messages.error(request, f"오류: {e}")
        page_obj = None  # 게시글이 비어있는 페이지를 반환

    except Exception as e:
        # 기타 예기치 못한 에러 처리
        messages.error(request, "알 수 없는 오류가 발생했습니다.")
        page_obj = None

    return render(request, 'funding/post_list.html', {'page_obj': page_obj, 'query': query})

# 게시글 상세 페이지
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.all()

    if request.method == 'POST':
        # 댓글 작성 처리
        if 'comment' in request.POST:
            content = request.POST.get('content', '')
            try:
                if not content.strip():
                    messages.error(request, "댓글 내용을 입력해주세요.")
                else:
                    Comment.objects.create(post=post, user=request.user, content=content)
                    messages.success(request, "댓글이 추가되었습니다.")
            except Exception as e:  # 예기치 못한 에러 처리
                messages.error(request, "알 수 없는 오류가 발생했습니다.")
            return redirect('post_detail', pk=post.pk)

        # 지원 처리
        if post.is_full():
            messages.error(request, "모집이 마감되었습니다.")
            return redirect('post_detail', pk=post.pk)

        if Support.objects.filter(post=post, user=request.user).exists():
            messages.warning(request, "이미 지원하셨습니다.")
            return redirect('post_detail', pk=post.pk)

        Support.objects.create(post=post, user=request.user)
        post.current_applicants += 1
        post.save()
        messages.success(request, "지원이 완료되었습니다!")
        return redirect('post_detail', pk=post.pk)

    return render(request, 'funding/post_detail.html', {'post': post, 'comments': comments})

# 게시글 작성 기능
@login_required
@csrf_exempt
def post_create(request):
    if request.method == 'POST':
        title = request.POST['title']
        content = request.POST['content']
        price = request.POST['price']
        capacity = request.POST['capacity']

        Post.objects.create(
            title=title,
            content=content,
            price=price,
            capacity=capacity,
            author=request.user
        )
        messages.success(request, "게시글이 성공적으로 작성되었습니다.")
        return redirect('post_list')

    return render(request, 'funding/post_create.html')

# 게시글 수정 기능
@login_required
@csrf_exempt
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        messages.error(request, "작성자만 수정할 수 있습니다.")
        return redirect('post_detail', pk=pk)

    if request.method == 'POST':
        post.title = request.POST['title']
        post.content = request.POST['content']
        post.save()
        messages.success(request, "게시글이 성공적으로 수정되었습니다.")
        return redirect('post_detail', pk=post.pk)

    return render(request, 'funding/post_edit.html', {'post': post})

# 게시글 삭제 기능: 작성자만 삭제할 수 있도록 예외처리리
@login_required
@csrf_exempt
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        messages.error(request, "작성자만 삭제할 수 있습니다.")
        return redirect('post_detail', pk=pk)

    if request.method == 'POST':
        post.delete()
        messages.success(request, "게시글이 성공적으로 삭제되었습니다.")
        return redirect('post_list')

    return render(request, 'funding/post_delete.html', {'post': post})

# 댓글 삭제 기능: 작성자만 삭제할 수 있도록 예외처리리
@login_required
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if comment.user != request.user:
        messages.error(request, "작성자만 댓글을 삭제할 수 있습니다.")
        return redirect('post_detail', pk=comment.post.pk)

    if request.method == 'POST':
        comment.delete()
        messages.success(request, "댓글이 삭제되었습니다.")
        return redirect('post_detail', pk=comment.post.pk)

    return render(request, 'funding/comment_delete.html', {'comment': comment})

