from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from django.contrib.auth import authenticate, login, logout

from api.models import User, Problem, Submission
from api.serializer import UserSerializer, ProblemSerializer, SubmissionSerializer
from common import jwt_writer


class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ProblemList(generics.ListAPIView):
    def get_queryset(self):
        if self.kwargs.get('cf_handle', False):
            user_id = get_object_or_404(User, cf_handle=self.kwargs.get('cf_handle', False)).id
            to_return = []
            problems = Problem.objects.all()
            for problem in problems:
                for submission in problem.submissions:
                    if submission['user_id'] == user_id:
                        to_return.append(problem)
                        break
            return to_return
        if self.kwargs.get('batch', False):
            users_id = [user.id for user in User.objects.filter(batch=self.kwargs.get('batch'))]
            problems = Problem.objects.all()
            to_return = []
            for problem in problems:
                for submission in problem.submissions:
                    if submission['user_id'] in users_id:
                        to_return.append(problem)
                        break
            return to_return
        return Problem.objects.all()

    serializer_class = ProblemSerializer


class CfSubmissionList(generics.ListAPIView):
    def get_queryset(self):
        if self.kwargs.get('cf_handle', False):
            user_id = get_object_or_404(User, cf_handle=self.kwargs.get('cf_handle', False)).id
            submissions = []
            problems = Problem.objects.all()
            for problem in problems:
                for submission in problem.submissions:
                    if submission['user_id'] == user_id:
                        submissions.append(Submission(**submission, problem_id=problem.id))
                        break
            return submissions
        if self.kwargs.get('batch', False):
            users_id = [user.id for user in User.objects.filter(batch=self.kwargs.get('batch'))]
            problems = Problem.objects.all()
            submissions = []
            for problem in problems:
                for submission in problem.submissions:
                    if submission['user_id'] in users_id:
                        submissions.append(Submission(**submission, problem_id=problem.id))
                        break
            return submissions
        problems = Problem.objects.all()
        submissions = []
        for problem in problems:
            for submission in problem.submissions:
                submissions.append(Submission(**submission, problem_id=problem.id))
        return submissions

    serializer_class = SubmissionSerializer


def login_user(request):
    user = authenticate(request=request)
    if user:
        name = user.get_full_name()
        user_id = user.id
        cf_handle = user.cf_handle
        batch = user.batch
        is_staff = user.is_staff
        expire = (datetime.utcnow() + relativedelta(months=1)).strftime("%Y-%m-%d")
        jwt_str = jwt_writer(expire=expire, username=user.username, email=user.email, name=name, is_staff=is_staff,
                             cf_handle=cf_handle, batch=batch, user_id=user_id)
        return JsonResponse({"jwt": jwt_str})
    else:
        return JsonResponse({"errors": "Wrong username or password"}, status=400)


def logout_user(request):
    logout(request)
    return JsonResponse({"details": "success"})


def test_params(request):
    print(dict(request.GET))
    return JsonResponse({'status': True})


def users_dict():
    users = {}
    for user in User.objects.all():
        name = user.first_name + " " + user.last_name
        users[user.id] = user.cf_handle if not name or len(name) <= 4 else name
    return users


def get_list(request, start=0, end=30):
    if start >= end:
        return JsonResponse({'status': False, 'reason': 'Wrong start or end'})
    if abs(end - start) > 100:
        return JsonResponse({'status': False, 'reason': 'Too many problem fetch. Maximum 100'})
    try:
        to_send = Problem.objects.all()[start:end]
    except IndexError:
        return JsonResponse({'status': False, 'reason': 'Wrong start or end'})
    res = {'status': True, 'total': Problem.objects.all().count(), 'showing': str(start) + ' - ' + str(end)}
    users = users_dict()
    for problem in to_send:
        info = {'total_solvers': problem.total_solve, 'link': problem.problem_link}
        solvers = []
        for submission in problem.submissions:
            solvers.append(users[submission['user_id']])
        info['solvers'] = solvers
        res[problem.problem_name] = info
    return JsonResponse(res)
