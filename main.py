import os
from itertools import chain

from dotenv import load_dotenv
import requests
from terminaltables import AsciiTable

LANGUAGES = ['JavaScript', 'Java', 'Python', 'Ruby', 'PHP', 'C++', 'Go', 'Swift', '1С']


def get_request_by_prog_language_hh(language):
    all_pages_by_request = []
    url = 'https://api.hh.ru/vacancies'
    page = 0
    pages_number = 1
    while page < pages_number:
        params = {'area': 1,
                  'text': f'программист {language}',
                  'page': page}
        response = requests.get(url, params=params)
        response.raise_for_status()
        page_request = response.json()
        pages_number = page_request['pages']
        page += 1
        all_pages_by_request.append(page_request)
    return all_pages_by_request


def predict_rub_salary_hh(language):
    response_doc = get_request_by_prog_language_hh(language)
    middle_salary = []
    for doc in response_doc:
        vacancies = doc['items']
        salaries = [vacancy['salary'] for vacancy in vacancies]
        for salary in salaries:
            if salary:
                if salary['currency'] != 'RUR':
                    continue
                if salary['from'] and salary['to']:
                    middle_salary.append((salary['from']+salary['to'])/2)
                if not salary['from']:
                    middle_salary.append(salary['to']*0.8)
                if not salary['to']:
                    middle_salary.append(salary['from']*1.2)
            else:
                continue
    return middle_salary


def job_statistics_hh(languages=LANGUAGES):
    processed_statistics = {}
    for language in languages:
        rub_salary = predict_rub_salary_hh(language)
        processed_language = {
            "vacancies_found": get_request_by_prog_language_hh(language)[0]['found'],
            "vacancies_processed": len(rub_salary),
            "average_salary": int(sum(rub_salary) / len(rub_salary))
        }
        processed_statistics[language] = processed_language
    return processed_statistics


def get_request_by_industry_sj(token):
    all_pages_by_request = []
    number_of_results = 1
    verified_number_of_results = 0
    page = 0
    while verified_number_of_results < number_of_results:
        url = 'https://api.superjob.ru/2.0/vacancies/'
        headers = {
            'X-Api-App-Id': token}
        params = {'catalogues': 48,
                  'town': 'Москва',
                  'page': page}
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        response_objects = response.json()['objects']
        all_pages_by_request.append(response_objects)
        page += 1
        verified_number_of_results += len(response_objects)
        if number_of_results == 1:
            number_of_results = response.json()['total']
    all_pages_by_request = list(chain.from_iterable(all_pages_by_request))
    return all_pages_by_request


def predict_rub_salary_sj(token, vacancy):
    vacancies = get_request_by_industry_sj(token)
    middle_salaries = []
    for doc in vacancies:
        split_phrase = doc['profession'].split()
        if vacancy in split_phrase:
            if doc['currency'] == 'rub':
                if doc['payment_from'] and doc['payment_to'] != 0:
                    middle_salaries.append((doc['payment_from'] + doc['payment_to']) / 2)
                if doc['payment_from'] == 0 and doc['payment_to'] != 0:
                    middle_salaries.append(doc['payment_to'] * 0.8)
                if doc['payment_from'] != 0 and doc['payment_to'] == 0:
                    middle_salaries.append(doc['payment_from'] * 1.2)
                if doc['payment_from'] == 0 and doc['payment_to'] == 0:
                    continue
            else:
                continue
    return middle_salaries


def count_vacancies_by_request_sj(token, vacancy):
    vacancies = get_request_by_industry_sj(token)
    vacancies_found = 0
    for doc in vacancies:
        split_phrase = doc['profession'].split()
        if vacancy in split_phrase:
            vacancies_found += 1
    return vacancies_found


def job_statistics_sj(token, languages=LANGUAGES):
    processed_statistics = {}
    for language in languages:
        count_vacancies = count_vacancies_by_request_sj(token, language)
        salaries = predict_rub_salary_sj(token, language)
        if len(salaries) == 0:
            len_salaries = 1
        else:
            len_salaries = len(salaries)

        processed_language = {
            "vacancies_found": count_vacancies,
            "vacancies_processed": count_vacancies,
            "average_salary": int(sum(salaries) / len_salaries)
        }
        processed_statistics[language] = processed_language
    return processed_statistics


def create_table(statistic, header, languages=LANGUAGES):
    table_data = [[languages[n], statistic[languages[n]]['vacancies_found'],
                   statistic[languages[n]]['vacancies_processed'],
                   statistic[languages[n]]['average_salary']] for n in range(len(languages))]
    table = [
        ['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата'],
        *table_data
        ]
    table = AsciiTable(table, header)
    print(table.table)


def main():
    load_dotenv()
    token = os.environ["TOKEN_SUPER_JOB"]
    hh_statistic = job_statistics_hh()
    sj_statistic = job_statistics_sj(token)
    create_table(hh_statistic, 'HeadHunter Moscow')
    print()
    create_table(sj_statistic, 'SuperJob Moscow')


if __name__ == '__main__':
    main()
