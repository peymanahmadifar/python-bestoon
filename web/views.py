from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import json
from web.models import Token, Expense, Income, User
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt


# Create your views here.

@csrf_exempt
def submit_expense(request):
    # TODO; validation form
    this_token = request.POST['token']
    this_user = User.objects.filter(token__token=this_token)[0]
    if 'date' in request.POST:
        date = request.POST['date']
    else:
        date = timezone.now()
    Expense.objects.create(user=this_user, amount=request.POST['amount'], text=request.POST['text'],
                           date=date)

    return JsonResponse({
        'status': True
    }, encoder=json.JSONEncoder)
    # return HttpResponse('we are here')
