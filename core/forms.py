from django import forms
from .models import BaiViet  # Import model BaiViet

class BaiVietForm(forms.ModelForm):
    class Meta:
        model = BaiViet
        fields = ['noi_dung', 'hinh_anh', 'trang_thai', 'id_nhom']  # Chỉ định các trường cần sử dụng trong form

    # Bạn có thể thêm validation hoặc điều chỉnh widget nếu cần
    noi_dung = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Bạn đang nghĩ gì?', 'rows': 3}), required=True)
    hinh_anh = forms.ImageField(required=False)
    trang_thai = forms.ChoiceField(choices=[('public', 'Công khai'), ('friends', 'Chỉ bạn bè'), ('private', 'Riêng tư')], required=True)
    id_nhom = forms.IntegerField(required=False)  # Giả sử đây là ID của nhóm
