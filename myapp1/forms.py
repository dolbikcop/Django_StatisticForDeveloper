from myapp1.models import Vacancy, HH
from django.forms import ModelForm, TextInput, NumberInput, DateTimeInput


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
            'published_at': NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Год'
            })
        }


class HHForm(ModelForm):
    class Meta:
        model = HH
        fields = ["date"]
        widgets = {
            "date": DateTimeInput(attrs={
                'class': 'form-control custom-date-control',
                'id': 'date_day',
                'type': 'date'
            })
        }
