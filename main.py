import os

from dotenv import load_dotenv
import requests
from terminaltables import AsciiTable

LANGUAGES = [
    'JavaScript',
    'Java', 'Python',
    'Ruby', 'PHP',
    'C++', 'Go',
    'Swift', '1С'
]


def get_average_salary(salary_from, salary_to):
    if salary_from and salary_to:
        return (salary_from + salary_to) / 2
    if not salary_from and salary_to:
        return salary_to * 0.8
    if salary_from and not salary_to:
        return salary_from * 1.2
    if not salary_from and salary_to:
        return None


def get_all_vacancies_by_prog_language_hh(language):
    all_pages_by_request = []
    url = 'https://api.hh.ru/vacancies'
    region_number = 1
    page = 0
    pages_number = 1
    while page < pages_number:
        params = {'area': region_number,
                  'text': f'программист {language}',
                  'page': page}
        response = requests.get(url, params=params)
        response.raise_for_status()
        page_request = response.json()
        pages_number = page_request['pages']
        page += 1
        all_pages_by_request.append(page_request)
    return all_pages_by_request


def predict_rub_salaries_hh(all_pages_with_vacancies):
    middle_salaries = []
    for page in all_pages_with_vacancies:
        vacancies = page['items']
        for vacancy in vacancies:
            salary = vacancy['salary']
            if not salary or salary['currency'] != 'RUR':
                continue
            average_salary = get_average_salary(salary['from'], salary['to'])
            if average_salary:
                middle_salaries.append(average_salary)
    return middle_salaries


def get_job_statistics_hh(languages=LANGUAGES):
    processed_statistics = {}
    for language in languages:
        all_pages_with_vacancies_hh = get_all_vacancies_by_prog_language_hh(language)
        salaries = predict_rub_salaries_hh(all_pages_with_vacancies_hh)
        if not len(salaries):
            len_salaries = 1
        else:
            len_salaries = len(salaries)
        processed_language = {
            "vacancies_found": all_pages_with_vacancies_hh[0]['found'],
            "vacancies_processed": len(salaries),
            "average_salary": int(sum(salaries) / len_salaries)
        }
        processed_statistics[language] = processed_language
    return processed_statistics


def get_all_vacancies_by_prog_language_sj(token, language):
    all_pages_by_request = []
    more_results = True
    page = 0
    while more_results:
        url = 'https://api.superjob.ru/2.0/vacancies/'
        catalog_number_by_industry = 48
        headers = {'X-Api-App-Id': token}
        params = {'catalogues': catalog_number_by_industry,
                  'town': 'Москва',
                  'page': page,
                  'keyword': language}
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        page_by_request = response.json()
        all_pages_by_request.append(page_by_request)
        page += 1
        more_results = page_by_request['more']
    return all_pages_by_request


def predict_rub_salary_sj(all_pages_with_vacancies_sj):
    middle_salaries = []
    for page in all_pages_with_vacancies_sj:
        vacancies = page['objects']
        for vacancy in vacancies:
            average_salary = get_average_salary(vacancy['payment_from'], vacancy['payment_to'])
            if not average_salary or vacancy['currency'] != 'rub':
                continue
            middle_salaries.append(average_salary)
    return middle_salaries


def get_job_statistics_sj(token, languages=LANGUAGES):
    processed_statistics = {}
    for language in languages:
        all_pages_with_vacancies_sj = get_all_vacancies_by_prog_language_sj(token, language)
        count_vacancies = all_pages_with_vacancies_sj[0]['total']
        salaries = predict_rub_salary_sj(all_pages_with_vacancies_sj)
        if not len(salaries):
            len_salaries = 1
        else:
            len_salaries = len(salaries)

        processed_language = {
            "vacancies_found": count_vacancies,
            "vacancies_processed": len_salaries,
            "average_salary": int(sum(salaries) / len_salaries)
        }
        processed_statistics[language] = processed_language
    return processed_statistics


def create_table(statistic, header, languages=LANGUAGES):
    table_columns = [[languages[n], statistic[languages[n]]['vacancies_found'],
                   statistic[languages[n]]['vacancies_processed'],
                   statistic[languages[n]]['average_salary']] for n in range(len(languages))]
    table = [
        ['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата'],
        *table_columns
        ]
    return AsciiTable(table, header)


def main():
    load_dotenv()
    token = os.environ["TOKEN_SUPER_JOB"]
    hh_statistic = get_job_statistics_hh()
    sj_statistic = get_job_statistics_sj(token)
    table_hh = create_table(hh_statistic, 'HeadHunter Moscow')
    print(table_hh.table)
    print()
    table_sj = create_table(sj_statistic, 'SuperJob Moscow')
    print(table_sj.table)


if __name__ == '__main__':
    main()
