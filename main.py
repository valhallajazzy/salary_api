import os
from itertools import chain

from dotenv import load_dotenv
import requests
from terminaltables import AsciiTable

LANGUAGES = ['JavaScript', 'Java', 'Python', 'Ruby', 'PHP', 'C++', 'Go', 'Swift', '1С']


def get_average_salary(salary_from, salary_to):
    if salary_from and salary_to != 0:
        return (salary_from + salary_to) / 2
    if salary_from == 0 and salary_to != 0:
        return salary_to * 0.8
    if salary_from != 0 and salary_to == 0:
        return salary_from * 1.2
    if salary_from == 0 and salary_to == 0:
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


def predict_rub_salaries_and_count_all_vacancies_hh(language):
    all_pages_with_vacancies = get_all_vacancies_by_prog_language_hh(language)
    found_vacancies = all_pages_with_vacancies[0]['found']
    middle_salaries = []
    for page in all_pages_with_vacancies:
        vacancies = page['items']
        salaries = [vacancy['salary'] for vacancy in vacancies]
        for salary in salaries:
            if salary:
                if salary['currency'] != 'RUR':
                    continue
                if not salary['from']:
                    salary['from'] = 0
                if not salary['to']:
                    salary['to'] = 0
                average_salary = get_average_salary(salary['from'], salary['to'])
                if average_salary is not None:
                    middle_salaries.append(average_salary)
                else:
                    continue
            else:
                continue
    return middle_salaries, found_vacancies


def get_job_statistics_hh(languages=LANGUAGES):
    processed_statistics = {}
    for language in languages:
        rub_salaries_and_vacancies_found = predict_rub_salaries_and_count_all_vacancies_hh(language)
        if len(rub_salaries_and_vacancies_found[0]) == 0:
            len_salaries = 1
        else:
            len_salaries = len(rub_salaries_and_vacancies_found[0])
        processed_language = {
            "vacancies_found": rub_salaries_and_vacancies_found[1],
            "vacancies_processed": len(rub_salaries_and_vacancies_found[0]),
            "average_salary": int(sum(rub_salaries_and_vacancies_found[0]) / len_salaries)
        }
        processed_statistics[language] = processed_language
    return processed_statistics


def get_all_vacancies_by_industry_sj(token):
    all_pages_by_request = []
    count_of_vacancies = 1
    verified_count_of_vacancies = 0
    page = 0
    while verified_count_of_vacancies < count_of_vacancies:
        url = 'https://api.superjob.ru/2.0/vacancies/'
        catalog_number_by_industry = 48
        headers = {
            'X-Api-App-Id': token}
        params = {'catalogues': catalog_number_by_industry,
                  'town': 'Москва',
                  'page': page}
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        response_objects = response.json()['objects']
        all_pages_by_request.append(response_objects)
        page += 1
        verified_count_of_vacancies += len(response_objects)
        if count_of_vacancies == 1:
            count_of_vacancies = response.json()['total']
    all_pages_by_request = list(chain.from_iterable(all_pages_by_request))
    return all_pages_by_request


def predict_rub_salary_sj(token, vacancy):
    vacancies = get_all_vacancies_by_industry_sj(token)
    middle_salaries = []
    for doc in vacancies:
        split_phrase = doc['profession'].split()
        if vacancy in split_phrase:
            if doc['currency'] == 'rub':
                average_salary = get_average_salary(doc['payment_from'], doc['payment_to'])
                if average_salary is not None:
                    middle_salaries.append(average_salary)
                else:
                    continue
            else:
                continue
    return middle_salaries


def count_vacancies_by_request_sj(token, vacancy):
    vacancies = get_all_vacancies_by_industry_sj(token)
    vacancies_found = 0
    for doc in vacancies:
        split_phrase = doc['profession'].split()
        if vacancy in split_phrase:
            vacancies_found += 1
    return vacancies_found


def get_job_statistics_sj(token, languages=LANGUAGES):
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
    hh_statistic = get_job_statistics_hh()
    sj_statistic = get_job_statistics_sj(token)
    create_table(hh_statistic, 'HeadHunter Moscow')
    print()
    create_table(sj_statistic, 'SuperJob Moscow')


if __name__ == '__main__':
    main()
