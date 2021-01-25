import json
import threading
import time
from datetime import datetime

import requests
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from api.models import User, Problem


def save_problems(solver, problems):
    added_problem = []
    for problem_json in Problem.objects.all():
        if problem_json.submissions:
            for submission in problem_json.submissions:
                if submission['user_id'] == solver.id:
                    added_problem.append(problem_json.problem_name)
                    break
    for problem_json in problems:
        problem_json = problems[problem_json]
        problem_name = problem_json['problem_name']
        problem_link = problem_json['problem_link']
        if problem_name in added_problem or problem_json['accepted'] == 0:
            continue
        try:
            Problem.objects.get_or_create(problem_name=problem_name, problem_link=problem_link)
            problem = Problem.objects.get(problem_name=problem_name, problem_link=problem_link)
            if not problem.submissions or solver.id not in [x['user_id'] for x in problem.submissions]:
                update_problem(problem, problem_json, solver)
            else:
                print('double error')
        except Problem.MultipleObjectsReturned:
            print('multiple object error')
            for problem in Problem.objects.filter(problem_name=problem_name, problem_link=problem_link)[1:]:
                problem.delete()
            pass
    print("**** all problem for ", solver.cf_handle, "added successfully ****")


def update_problem(problem, problem_json, solver):
    submission = problem_json.copy()
    submission['user_id'] = solver.id
    submission.pop('problem_name')
    submission.pop('problem_link')

    problem.score = problem_json['score']
    problem.total_solve = problem.total_solve + 1
    problem.accepted = problem_json['accepted'] + problem.accepted
    problem.wrong = problem_json['wrong'] + problem.wrong
    problem.limit = problem_json['limit'] + problem.limit
    problem.error = problem_json['error'] + problem.error
    problem.other = problem_json['other'] + problem.other

    submissions = problem.submissions
    if submissions:
        submissions.append(submission)
    else:
        submissions = [submission]
    problem.submissions = submissions

    problem.save()


def _process_submissions(solver):
    res = requests.get(f'https://codeforces.com/api/user.status?handle={solver.cf_handle}&from=1').json()
    problems = {}
    if res['status'] == 'OK':
        submissions = res['result']
    else:
        print("Error in Link")
        submissions = []
    for sub in submissions:
        contest_id = sub['contestId']
        submission_id = sub['id']
        problem_index = sub['problem']['index']
        problem_name = sub['problem']['name']
        score = sub['problem'].get('rating', 5000)
        language = sub['programmingLanguage']
        verdict = sub['verdict']
        date = str(datetime.fromtimestamp(sub['creationTimeSeconds']).date())
        submission_link = f'https://codeforces.com/contest/{contest_id}/submission/{submission_id}'
        problem_link = f'https://codeforces.com/contest/{contest_id}/problem/{problem_index}'
        problems[problem_name] = problems.get(problem_name,
                                              {'accepted': 0, 'wrong': 0, 'error': 0, 'other': 0,
                                               'limit': 0, 'submission_link': submission_link,
                                               'date': date, 'problem_name': problem_name,
                                               'problem_link': problem_link, 'language': language, 'score': score})

        if verdict == 'OK' or verdict == 'PARTIAL':
            problems[problem_name][submission_link] = submission_link
            problems[problem_name]['accepted'] += 1
        elif verdict == 'WRONG_ANSWER' or verdict == 'CHALLENGED':
            problems[problem_name]['wrong'] += 1
        elif 'LIMIT' in verdict:
            problems[problem_name]['limit'] += 1
        elif 'ERROR' in verdict:
            problems[problem_name]['error'] += 1
        else:
            problems[problem_name]['other'] += 1
    update_solver(solver, problems)
    save_problems(solver, problems)


def update_solver(solver, problems):
    wrong, solve, accepted, error, limit, other = 0, 0, 0, 0, 0, 0
    for problem in problems:
        sp = problems[problem]
        if sp['accepted']:
            solve += 1
        accepted += sp['accepted']
        wrong += sp['wrong']
        error += sp['error']
        limit += sp['limit']
        other += sp['other']
    solver.solve = solve
    solver.accepted = accepted
    solver.wrong = wrong
    solver.error = error
    solver.limit = limit
    solver.other = other
    solver.save()


def _all_user():
    users = User.objects.exclude(cf_handle="not_added").order_by('accepted')
    for user in users:
        thread = threading.Thread(target=_process_submissions, args=[user])
        thread.start()
        time.sleep(5)


def all_user(request):
    thread = threading.Thread(target=_all_user)
    thread.start()
    return JsonResponse({"detail": "success"})


def single_user(request, handle_name):
    user = get_object_or_404(User, cf_handle=handle_name)
    thread = threading.Thread(target=_process_submissions, args=[user])
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


def send_problems(request):
    problem_data = []
    for problem in Problem.objects.all():
        for submission in problem.submissions:
            solver = User.objects.get(id=submission['user_id']).cf_handle
            pb = {'name': problem.problem_name, 'link': problem.problem_link, 'solver': solver}
            problem_data.append(pb)
    res = requests.post('http://mah20.pythonanywhere.com/cf/add_problems/', json={'problems': problem_data}).json()
    return JsonResponse(res)
