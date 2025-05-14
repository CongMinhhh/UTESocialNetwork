from django import forms
from .models import BaiViet  # Import model BaiViet

class BaiVietForm(forms.ModelForm):
    class Meta:
        model = BaiViet
        fields = ['noi_dung', 'hinh_anh', 'trang_thai', 'ten_nhom']
        widgets = {
            'noi_dung': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Bạn đang nghĩ gì?'}),
            'trang_thai': forms.Select(),
            'ten_nhom': forms.TextInput(attrs={'placeholder': 'Tên nhóm (nếu có)'}),
        }