from django.shortcuts import render, redirect
from django.contrib import messages
import hashlib
from .forms import BaiVietForm  
from .models import BaiViet  
from .models import NguoiDung


def index(request):
    return render(request, 'SignUpPage.html')  # Trang đăng ký


def home(request):
    # Kiểm tra nếu chưa đăng nhập, yêu cầu đăng nhập
    if 'user_id' not in request.session:
        messages.error(request, "Bạn cần đăng nhập để truy cập!")
        return redirect('login')
    return render(request, 'MainPage.html')  # Trang chủ


def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Kiểm tra mật khẩu và xác nhận mật khẩu
        if password != confirm_password:
            messages.error(request, "Mật khẩu không khớp!")
            return redirect('signup')

        # Kiểm tra username đã tồn tại chưa
        if NguoiDung.objects.filter(ten=username).exists():
            messages.error(request, "Tên người dùng đã tồn tại!")
            return redirect('signup')

        # Kiểm tra email đã tồn tại chưa
        if NguoiDung.objects.filter(email=email).exists():
            messages.error(request, "Email đã tồn tại!")
            return redirect('signup')

        # Mã hóa mật khẩu bằng SHA256
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        # Tạo người dùng mới
        NguoiDung.objects.create(
            ten=username,
            email=email,
            mat_khau_hash=password_hash
        )

        messages.success(request, "Đăng ký thành công! Hãy đăng nhập.")
        return redirect('login')

    return render(request, 'SignUpPage.html')  # Trang đăng ký (GET)


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = NguoiDung.objects.get(ten=username)  # lấy theo username
            password_hash = hashlib.sha256(password.encode()).hexdigest()

            if user.mat_khau_hash == password_hash:
                # Đăng nhập thành công
                request.session['user_id'] = user.id  # Lưu ID người dùng vào session
                request.session['user_name'] = user.ten  # Lưu username vào session
                messages.success(request, "Đăng nhập thành công!")
                return redirect('home')
            else:
                messages.error(request, "Mật khẩu không đúng!")
        except NguoiDung.DoesNotExist:
            messages.error(request, "Tên người dùng không tồn tại!")

    return render(request, 'SignInPage.html')  # Trang đăng nhập (GET)


def logout_view(request):
    # Xóa thông tin đăng nhập khỏi session
    request.session.flush()
    messages.success(request, "Đăng xuất thành công!")
    return redirect('login')

def post_bai_viet(request):
    if 'user_id' not in request.session:
        messages.error(request, "Bạn cần đăng nhập để đăng bài!")
        return redirect('login')

    if request.method == 'POST':
        content = request.POST.get('content')  # Lấy nội dung bài viết
        image = request.FILES.get('image')  # Lấy ảnh (nếu có)

        # Tạo đối tượng BaiViet
        bai_viet = BaiViet(
            noi_dung=content,
            id_nguoi_dung=request.session['user_id'],
            hinh_anh=image if image else None,  # Lưu ảnh nếu có
            trang_thai='public'  # Hoặc trang_thai khác tùy ý
        )
        bai_viet.save()  # Lưu bài viết vào cơ sở dữ liệu

        messages.success(request, "Đăng bài thành công!")
        return redirect('home')  # Quay lại trang chính sau khi đăng bài thành công

    return render(request, 'MainPage.html')  # Nếu GET thì render lại trang chủ