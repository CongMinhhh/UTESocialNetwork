from django.db import models

# Model NguoiDung
class NguoiDung(models.Model):
    ten = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    mat_khau_hash = models.CharField(max_length=255)
    anh_dai_dien = models.CharField(max_length=500, blank=True, null=True)
    ngay_tao = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'NGUOIDUNG'  

    def __str__(self):
        return self.ten

# Model BaiViet
class BaiViet(models.Model):
    # Các trường dữ liệu
    noi_dung = models.TextField()  # Nội dung bài viết
    hinh_anh = models.CharField(max_length=500, blank=True, null=True)  # Đường dẫn hình ảnh (giới hạn 500 ký tự)
    trang_thai_choices = [
        ('public', 'Public'),
        ('friends', 'Friends'),
        ('private', 'Private'),
    ]
    trang_thai = models.CharField(max_length=10, choices=trang_thai_choices, default='public')  # Trạng thái bài viết
    ngay_tao = models.DateTimeField(auto_now_add=True)  # Thời gian tạo bài viết
    id_nhom = models.IntegerField(null=True, blank=True)  # ID nhóm, có thể null nếu không thuộc nhóm

    # Liên kết với bảng người dùng (NguoiDung)
    id_nguoi_dung = models.ForeignKey(NguoiDung, on_delete=models.CASCADE)  # Liên kết tới người dùng

    def __str__(self):
        return f"Bài viết của {self.id_nguoi_dung.ten} - {self.ngay_tao}"

    class Meta:
        db_table = 'BAIVIET'  
