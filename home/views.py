from django.shortcuts import render,redirect
from home.models import poll
from django.template import loader
from django.http import HttpResponse
from home.forms import VoteForm
from django.contrib.auth.decorators import login_required# Create your views here.

@ login_required
def all_polls(request):
    all_polls = poll.objects.all()

    context = {
        'all_polls':all_polls,
    }
    template = loader.get_template('all_polls.html')

    return HttpResponse(template.render(context,request))

@login_required
def poll_detail(request,poll_id):
    req_poll = poll.objects.get(id=poll_id)

    if request.method == 'POST':
        form = VoteForm(request.POST)
        if form.is_valid():
            selected_choice = form.cleaned_data['choice']

            if selected_choice == '1':
                req_poll.vote1+=1
            elif selected_choice == '2':
                req_poll.vote2+=1
            elif selected_choice == '3':
                req_poll.vote3+=1
        
            req_poll.save()
            return redirect(f'/home/polls/{poll_id}/')
    else:
        form=VoteForm()

    context = {
        'req_poll':req_poll,
        'form':form,
    }

    template = loader.get_template('poll_detail.html')

    return HttpResponse(template.render(context,request))