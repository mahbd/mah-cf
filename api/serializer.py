import requests
from rest_framework import serializers

from api.models import User, Problem, Submission


def cf_handle_validator(value):
    res = requests.get('https://codeforces.com/api/user.status?handle=Fefer_Ivan&from=1&count=1').json()
    if res['status'] != 'OK':
        raise serializers.ValidationError(f'Wrong username. {value}')


# noinspection PyMethodMayBeStatic
class UserSerializer(serializers.ModelSerializer):
    cf_handle = serializers.CharField(max_length=50, validators=[cf_handle_validator])
    name = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'cf_handle', 'username', 'name', 'email', 'uri_id', 'batch', 'solve', 'accepted', 'wrong', 'limit',
            'error', 'other', 'user')

    def get_name(self, user):
        return user.first_name + " " + user.last_name

    def get_user(self, user):
        return None


def users_dict():
    users = {}
    for user in User.objects.all():
        name = user.first_name + " " + user.last_name
        users[user.id] = user.cf_handle if not name or len(name) <= 4 else name
    return users


class ProblemSerializer(serializers.ModelSerializer):
    solver_list = serializers.SerializerMethodField()

    class Meta:
        model = Problem
        fields = ['problem_name', 'problem_link', 'total_solve', 'solver_list', 'accepted', 'wrong',
                  'limit', 'error']

    # noinspection PyMethodMayBeStatic
    def get_solver_list(self, info):
        users = users_dict()
        return [users[submission['user_id']] for submission in info.submissions]


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = '__all__'
