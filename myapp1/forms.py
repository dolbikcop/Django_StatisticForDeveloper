from myapp1.models import Vacancy
from django.forms import ModelForm, TextInput, NumberInput


class VacancyForm(ModelForm):
    class Meta:
        model = Vacancy
        fields = ['name', 'key_skills', 'salary', 'area_name', 'published_at']
        widgets = {
            'name': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Имя'
            }),
            'key_skills': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ключевые навыки'
            }),
            'salary': NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Зарплата'
            }),
            'area_name': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Город'
            }),
            'published_at': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Год-месяц'
            })
        }
