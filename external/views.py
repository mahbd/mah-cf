import json
import threading
import time
from math import log2
from dateutil import parser
#
from bs4 import BeautifulSoup
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from common import get_url_content

from api.models import User, Problem


def get_submission_page_number_cf(cf_handle):
    page_num = 1
    res = get_url_content(f'https://codeforces.com/submissions/{cf_handle}/page/1')
    res = BeautifulSoup(res, 'html.parser')
    for page in res.findAll('span', attrs={'class': 'page-index'}):
        page_num = max(page_num, int(page.text.strip()))
    print(f'{cf_handle} has {page_num} pages')
    return page_num


def get_submission_cf_page(url):
    problems_page = {}
    res = get_url_content(url)
    res = BeautifulSoup(res, 'html.parser')
    submission_table = res.find('table', attrs={'class': 'status-frame-datatable'})
    all_problem_row = submission_table.findAll('tr')[1:]
    for problem_row in all_problem_row:
        verdict = problem_row.find('td', attrs={'class': 'status-cell status-small status-verdict-cell'}).text.strip()
        if len(verdict) != 0:
            try:
                columns = problem_row.findAll('td')
                try:
                    submission_link = 'https://codeforces.com' + columns[0].find('a')['href']
                except (TypeError, IndexError, KeyError):
                    submission_link = 'not_found'
                date = columns[1].text.strip()
                plo = columns[3]
                problem_name = str(plo.text).strip()[4:]
                problem_link = 'https://codeforces.com' + str(plo.find('a')['href'])
                language = columns[4].text.strip()
            except (IndexError, KeyError):
                continue
            problems_page[problem_name] = problems_page.get(problem_name,
                                                            {'accepted': 0, 'wrong': 0, 'error': 0, 'extra': 0,
                                                             'limit': 0, 'submission_link': submission_link,
                                                             'date': date, 'problem_name': problem_name,
                                                             'problem_link': problem_link, 'language': language})
            if verdict == 'Accepted' or verdict == 'Happy New Year!':
                problems_page[problem_name][submission_link] = submission_link
                problems_page[problem_name]['accepted'] += 1
            elif 'Wrong answer' in verdict:
                problems_page[problem_name]['wrong'] += 1
            elif 'limit' in verdict:
                problems_page[problem_name]['limit'] += 1
            elif 'error' in verdict:
                problems_page[problem_name]['error'] += 1
            else:
                problems_page[problem_name]['extra'] += 1
    return problems_page


def save_problems(model, problems, solver):
    solver = User.objects.get(id=solver.id)
    added_problem = []
    for problem in Problem.objects.all():
        if problem.submissions:
            for submission in problem.submissions:
                if submission['user_id'] == solver.id:
                    added_problem.append(problem.problem_name)
                    break
    for problem in problems:
        problem = problems[problem]
        problem_name = problem['problem_name']
        if problem_name in added_problem:
            continue
        problem_link = problem['problem_link']
        # noinspection PyBroadException
        try:
            Problem.objects.get_or_create(problem_name=problem_name, problem_link=problem_link)
            problem_obj = Problem.objects.get(problem_name=problem_name, problem_link=problem_link)
            if not problem_obj.submissions or solver.id not in [x['user_id'] for x in problem_obj.submissions]:
                submission = {
                    "user_id": solver.id,
                    "language": problem['language'],
                    "date": str(parser.parse(problem['date']).date()),
                    "accepted": problem['accepted'],
                    "wrong": problem['wrong'],
                    "limit": problem['limit'],
                    "error": problem['error'],
                    "other": problem['extra']
                }
                score = (5 - (problem['wrong'] + problem['limit'] + problem['error'] + problem['extra'])) / 5
                if score < 0.2:
                    score = 0.2
                score *= 13 - log2(solver.solve)
                problem_obj.score = score + problem_obj.score
                problem_obj.total_solve = problem_obj.total_solve + 1
                problem_obj.accepted = problem['accepted'] + problem_obj.accepted
                problem_obj.wrong = problem['wrong'] + problem_obj.wrong
                problem_obj.limit = problem['limit'] + problem_obj.limit
                problem_obj.error = problem['error'] + problem_obj.error
                problem_obj.other = problem['extra'] + problem_obj.other
                submissions = problem_obj.submissions
                if submissions:
                    submissions.append(submission)
                else:
                    submissions = [submission]
                problem_obj.submissions = submissions
                problem_obj.save()
            else:
                print('de')
        except Problem.MultipleObjectsReturned:
            print('me')
            for m in Problem.objects.filter(problem_name=problem_name, problem_link=problem_link)[1:]:
                m.delete()
            pass
    print("**** all problem for ", solver.cf_handle, "added successfully ****")


def single_user_cf(solver, pages=1, single=False):
    all_problem, ac_problems = {}, {}
    solve, accepted, wrong, limit, error, other = 0, 0, 0, 0, 0, 0
    for page in range(1, pages + 1):
        problems_page = get_submission_cf_page(f'https://codeforces.com/submissions/{solver.cf_handle}/page/{page}')
        for problem in problems_page:
            all_problem[problem] = all_problem.get(problem, {'accepted': 0, 'wrong': 0, 'error': 0, 'extra': 0,
                                                             'limit': 0, 'submission_link': '',
                                                             'date': '', 'problem_name': '',
                                                             'problem_link': '', 'language': ''})
            sp, pp = all_problem[problem], problems_page[problem]
            if not sp['accepted']:
                sp['submission_link'] = pp['submission_link']
                sp['problem_name'] = pp['problem_name']
                sp['date'] = pp['date']
                sp['problem_link'] = pp['problem_link']
                if 'Clang++' in pp['language'] or 'C++' in pp['language'] or 'GCC' in pp['language'] or 'GNU' in pp[
                    'language']:
                    sp['language'] = 'C/C++'
                elif 'Kotlin' in pp['language'] or 'Java' in pp['language']:
                    sp['language'] = 'Kotlin/Java'
                elif 'Python' in pp['language'] or 'PyPy' in pp['language']:
                    sp['language'] = 'Python'
                else:
                    sp['language'] = 'Others'
            if 'Python' in pp['language'] or 'PyPy' in pp['language']:
                sp['language'] = 'Python'
            sp['accepted'] += pp['accepted']
            sp['wrong'] += pp['wrong']
            sp['error'] += pp['error']
            sp['limit'] += pp['limit']
            sp['extra'] += pp['extra']
    for problem in all_problem:
        sp = all_problem[problem]
        if sp['accepted']:
            solve += 1
            ac_problems[problem] = sp
        accepted += sp['accepted']
        wrong += sp['wrong']
        error += sp['error']
        limit += sp['limit']
        other += sp['extra']
    if not single:
        solver.solve = solve
        solver.accepted = accepted
        solver.wrong = wrong
        solver.error = error
        solver.limit = limit
        solver.other = other
        solver.save()
    save_problems(Problem, ac_problems, solver)


def all_user_single_page(request):
    users = User.objects.exclude(cf_handle="not_added")
    for user in users:
        thread = threading.Thread(target=single_user_cf, args=[user])
        thread.start()
    return JsonResponse({"detail": "success"})


def all_user_all_page_fun():
    users = User.objects.exclude(cf_handle="not_added").order_by('accepted')
    for user in users:
        pages = get_submission_page_number_cf(user.cf_handle)
        if pages > 150:
            print("******User " + user.cf_handle + " changed handle name*********")
            return
        thread = threading.Thread(target=single_user_cf, args=[user, pages])
        thread.start()
        time.sleep(5)


def all_user_all_page(request):
    thread = threading.Thread(target=all_user_all_page_fun)
    thread.start()
    return JsonResponse({"detail": "success"})


def single_user_single_page(request, handle_name):
    user = get_object_or_404(User, cf_handle=handle_name)
    single_user_cf(user)
    return JsonResponse({"detail": "success"})


def single_user_all_page(request, handle_name):
    user = get_object_or_404(User, cf_handle=handle_name)
    pages = get_submission_page_number_cf(user.cf_handle)
    thread = threading.Thread(target=single_user_cf, args=[user, pages])
    thread.start()
    return JsonResponse({"detail": "success"})


def add_cf_handle(request):
    data = json.loads(request.body)['data']
    for handle in data:
        if User.objects.filter(cf_handle=handle):
            print(handle, 'pre')
            pass
        else:
            print(handle, 'added')
            User.objects.create(cf_handle=handle)
    return JsonResponse({'result': 'Successful'})
