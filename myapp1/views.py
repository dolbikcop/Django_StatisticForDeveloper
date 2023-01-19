from django.shortcuts import render, redirect
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Q, Avg, Count

from myapp1.forms import VacancyForm, HHForm
from myapp1.models import Vacancy

from collections import Counter

import time
import requests
import json
import pandas as pd
from math import ceil
import datetime
from bs4 import BeautifulSoup


# Create your views here.

def index_page(request: WSGIRequest) -> render:
    data = {
        'title': 'Главная страница',
        'profession_name': "C# программист"
    }
    return render(request, 'main.html', data)


def relevance_page(request: WSGIRequest) -> render:
    prerender = True
    profession_name = "C# программист"
    data = {
        'prerender': prerender,
        'profession_name': profession_name,
        'title': "Статистика по годам"
    }
    if not prerender:
        header_year = ["Год", "Средняя зарплата", f"Средняя зарплата - {profession_name}", "Количество вакансий",
                       f"Количество вакансий - {profession_name}"]
        prof_filter = Q(name__icontains=f'{profession_name}') | Q(name__icontains='C#') | Q(name__icontains='С#') | Q(
            name__icontains='си шарп')
        prof_count = Count('id', filter=prof_filter)
        prof_salary = Avg('salary', filter=prof_filter)
        statistics_by_years = list(Vacancy.objects
                                   .values('published_at')
                                   .annotate(total_count=Count('id'), avg_salary=Avg('salary'),
                                             prof_count=prof_count, prof_salary=prof_salary)
                                   .values('published_at', 'total_count', 'avg_salary', 'prof_count', 'prof_salary')
                                   .order_by('-published_at'))
        data.update({
            'header_year': header_year,
            'statistics_by_years': statistics_by_years
        })
    return render(request, 'relevance.html', data)


def geography_page(request: WSGIRequest) -> render:
    prerender = True
    profession_name = "C# программист"
    data = {
        'prerender': prerender,
        'profession_name': profession_name,
        'title': "Статистика по городам"
    }
    if not prerender:
        header = ["Город", "Всего вакансий", "Средняя зарплата", f"Вакансий {profession_name}"]

        prof_filter = Q(name__icontains=f'{profession_name}') | Q(name__icontains='C#') | Q(name__icontains='С#') | Q(
            name__icontains='си шарп')
        prof_count = Count('id', filter=prof_filter)
        statistics_by_cities = list(Vacancy.objects
                                    .values('area_name')
                                    .annotate(total_count=Count('id'),
                                              avg_salary=Avg('salary'),
                                              prof_count=prof_count)
                                    .values('area_name', 'total_count', 'avg_salary', 'prof_count')
                                    .order_by('-prof_count')[:10])
        data.update({
            "profession_name": profession_name,
            "header_city": header,
            "statistics_by_cities": statistics_by_cities
        })
    return render(request, 'geography.html', data)


def skills_page(request: WSGIRequest) -> render:
    prerender = True
    data = {
        "prerender": prerender,
        'title': "Востребованные навыки по годам"
    }
    if not prerender:
        header = ["Год", 'Навыки']
        all_skills = Vacancy.objects.exclude(key_skills=None).values('key_skills', 'published_at')
        skills_by_year = {}
        for c_skill in all_skills:
            year = c_skill["published_at"]
            if year not in skills_by_year.keys():
                skills_by_year[year] = c_skill["key_skills"].split('\n')
            else:
                skills_by_year[year].extend(c_skill["key_skills"].split('\n'))

        for year, skills in skills_by_year.items():
            c = Counter(skills)
            skills_by_year[year] = [(name, c[name] / len(skills) * 100.0) for name, count in c.most_common(10)]
        data.update({
            "skills_by_year": dict(sorted(skills_by_year.items(), reverse=True)),
            'headers': header
        })
    return render(request, 'skills.html', data)


def recent_vacancies_page(request: WSGIRequest) -> render:
    error_message = ""
    max_vacancies_count = 10
    vacancies, header = [], []
    if request.method == "POST":
        received_form = HHForm(request.POST)
        if received_form.is_valid():
            date = received_form.cleaned_data.get('date')
            header = ["Название", "Описание", "Навыки", "Компания", "Оклад", "Название региона", "Дата публикации"]
            vacancies = Parser(date, max_vacancies_count).vacancies.to_dict(orient='records')
        else:
            error_message = "Неправильно заполненная форма."
    form = HHForm()
    data = {
        'vacancies': vacancies,
        'headers': header,
        'error_msg': error_message,
        'form': form
    }
    return render(request, 'recent_vacancies.html', data)


def add_vacancy(request: WSGIRequest) -> render:
    error_message = ""
    if request.method == "POST":
        received_form = VacancyForm(request.POST)
        if received_form.is_valid():
            received_form.save()
            return redirect('home')
        else:
            error_message = "Неправильно заполненная форма."

    form = VacancyForm(initial={"published_at": None, "salary": None})
    data = {
        'form': form,
        'error_message': error_message
    }
    return render(request, 'add_vacancy.html', data)


def vue_page(request: WSGIRequest) -> render:
    return render(request, "vue.html")


# class ExampleView(ModelViewSet):
#     queryset: QuerySet = Vacancy.objects.all()
#     serializer_class = VacancySerializer

# region HH_Parser
def get_page(params: dict, id: str = '') -> dict:
    """
    Получает ответ от api.hh.ru/vacancies с заданными параметрами params.

    :param params: Параметры для поиска вакансий.
    :param id: ID вакансии.

    :returns: Словарь, полученный в результате обработки полученного JSON-объекта.
    """

    req = requests.get('https://api.hh.ru/vacancies/' + id, params)
    data = req.content.decode()
    return json.loads(data)


def get_relevant_vacancy_fields(vacancy_data: dict) -> list:
    """
    Возвращает только те поля вакансии, которые были указаны в ТЗ (name, salary_from, salary_to, salary_currency,
    area_name, published_at).

    :param vacancy_data: Словарь с данными об одной вакансии.

    :returns: Список из полей вакансии вида [name, salary_from, salary_to, salary_currency, area_name, published_at].
    """

    more_info = get_page({}, vacancy_data['id'])

    name = vacancy_data["name"]

    raw_desc = more_info["description"]
    soup = BeautifulSoup(raw_desc, 'html.parser')
    description = soup.get_text()

    key_skills = ", ".join([s for d in more_info["key_skills"] for s in d.values()])

    company = vacancy_data["employer"]["name"]
    area_name = vacancy_data["area"]["name"]
    published_at = vacancy_data["published_at"]

    salary = vacancy_data["salary"]
    if salary is not None:
        salary_from = salary["from"]
        salary_to = salary["to"]
        salary_currency = salary["currency"]
    else:
        salary_from, salary_to, salary_currency = None, None, None
    return [name, description, key_skills, salary_from, salary_to, salary_currency, company, area_name, published_at]


def get_fields_from_vacancies_page(vac_data: dict) -> pd.DataFrame:
    """
    Обрабатывает словарь страницы с вакансиями.

    :param vac_data: Словарь страницы с вакансиями.

    :returns: DataFrame со столбцами ["name", "salary_from", "salary_to", "salary_currency", "area_name",
    "published_at"] из словаря с вакансиями.
    """

    parsed_relevant_vacancies_fields = [get_relevant_vacancy_fields(values) for values in vac_data["items"]]

    t = pd.DataFrame(parsed_relevant_vacancies_fields,
                     columns=["name", "description", "key_skills", "salary_from", "salary_to", "salary_currency",
                              "company", "area_name",
                              "published_at"])
    return t


def get_vacancies(date_from: datetime.datetime, date_to: datetime.datetime, max_vacancies_count: int,
                  per_page: int = 100, pages: int = 20) -> pd.DataFrame:
    """
    Получает вакансии с hh.ru за последние n_hours часов. Для правильного подсчёта необходимо указать максимально
    возможное количество получаемых вакансий. Per_page * pages не должно быть больше 2000.

    :param date_from: Дата, с момента которой будут получены вакансии.
    :param date_to: Дата, до которого момента будут получены вакансии.
    :param max_vacancies_count: Максимально возможное количество получаемых вакансий. Из-за ограничения на выгрузку
    более чем 2000 вакансий их получение организовано через некоторые периоды времени, величина которых зависит от этого
     параметра.
    :param per_page: Количество вакансий, получаемых на одной странице. Не может быть больше 100.
    :param pages: Количество страниц, получаемых за один период времени.

    :returns: DataFrame с полученными вакансиями за последние n_hours со столбцами ["name", "salary_from", "salary_to",
    "salary_currency", "area_name", "published_at"].
    """

    df = pd.DataFrame(
        columns=["name", "description", "key_skills", "salary_from", "salary_to", "salary_currency", "company",
                 "area_name", "published_at"])

    parsing_iterations = 100  # ceil(max_vacancies_count / (per_page * pages))
    timedelta = date_to - date_from
    n_hours = timedelta.days * 24 + timedelta.seconds / 3600
    time_chunk = ceil(n_hours / parsing_iterations)
    time_from = date_from.replace(second=0, microsecond=0)

    for iteration in range(parsing_iterations):
        time_to = time_from + datetime.timedelta(hours=time_chunk)

        if time_to > date_to or df.shape[0] >= max_vacancies_count:
            break

        for page in range(pages):
            params = {
                'text': 'c# OR c-sharp OR шарп OR с# OR Си шарп OR си-шарп',
                'search_field': "name",
                'per_page': per_page,
                'page': page,
                'specialization': 1,
                'date_from': time_from.isoformat(),
                'date_to': time_to.isoformat(),
                'only_with_salary': True,
                'currency': 'RUR'
            }

            vacancies_page = get_page(params)
            if page == vacancies_page["pages"]:
                break

            t = get_fields_from_vacancies_page(vacancies_page)
            df = pd.concat([df, t], ignore_index=True)

            # print(df.shape)
            time.sleep(0.1)

        time_from = time_to
    return df


class Parser:
    date_from: datetime.datetime
    date_to: datetime.datetime
    max_vacancies_count: int
    vacancies: pd.DataFrame

    def __init__(self, date_from: datetime.datetime, max_vacancies_count: int):
        self.date_from = date_from
        self.date_to = date_from + datetime.timedelta(days=1)
        self.max_vacancies_count = max_vacancies_count
        df = get_vacancies(self.date_from, self.date_to, self.max_vacancies_count)
        self.vacancies = (df
                          .assign(published_at=df["published_at"].astype('datetime64'),
                                  salary_from=df[["salary_from", "salary_to"]]
                                  .mean(axis=1).astype('int32'))
                          .rename({"salary_from": "salary"}, axis="columns")
                          .drop(columns=["salary_currency", "salary_to"])
                          .sort_values(by=['published_at'], ascending=True)
                          )[:max_vacancies_count]

# endregion
