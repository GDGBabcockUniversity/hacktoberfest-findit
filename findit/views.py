from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.views import LoginView
from .forms import AuthForm, RegistrationForm, LostItemForm, updateProfileForm, FoundItemForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import logout
from .models import LostItem, FoundItem, Notification

# Create your views here.

class index(LoginRequiredMixin, TemplateView):
    template_name = 'findit/app.html'
    login_url = '/login/'

class login_view(LoginView):
    authentication_form = AuthForm
    template_name = 'findit/login.html' 
    redirect_authenticated_user = True
    
class register(UserPassesTestMixin, CreateView):
    form_class = RegistrationForm
    template_name = 'findit/register.html'
    success_url = reverse_lazy('login')
    login_url = '/app/'
    raise_exception = False

    def test_func(self):
        return not self.request.user.is_authenticated

class app(LoginRequiredMixin,TemplateView):
    template_name = 'findit/app.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = LostItemForm()
        context['recent_lost_items'] = LostItem.objects.order_by('-time_created')[:3]
        context['recent_found_items'] = FoundItem.objects.order_by('-time_created')[:3]
        return context
    def post(self, request, *args, **kwargs):
        form = LostItemForm(request.POST, request.FILES)
        if form.is_valid():
            lost_item = form.save(commit=False)
            lost_item.user = request.user
            lost_item.save()
            return redirect('app')
        else:
            return self.render_to_response(self.get_context_data(form=form))

class lostitems(LoginRequiredMixin, TemplateView):
    template_name = 'findit/lostitems.html'
    login_url = '/login/'

class viewItems(LoginRequiredMixin, TemplateView):
    template_name = 'findit/view_item.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lost_items'] = LostItem.objects.all()
        context['found_items'] = FoundItem.objects.all()
        return context

class reportItem(LoginRequiredMixin,TemplateView):
    template_name = 'findit/report_item.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = FoundItemForm()
        return context
    def post(self, request, *args, **kwargs):
        form = FoundItemForm(request.POST, request.FILES)
        if form.is_valid():
            lost_item = form.save(commit=False)
            lost_item.user = request.user
            lost_item.save()
            return redirect('reportItem')
        else:
            return self.render_to_response(self.get_context_data(form=form))


class notification(LoginRequiredMixin,TemplateView):
    template_name = 'findit/notification.html'
    login_url = '/login/'

class manageReport(LoginRequiredMixin, UserPassesTestMixin,TemplateView):
    def test_func(self):
        return self.request.user.is_staff

    template_name = 'findit/manage_report.html'
    login_url = '/login/'

class edit_profile(LoginRequiredMixin, UpdateView):
    form_class = updateProfileForm
    template_name = 'findit/edit_profile.html'
    success_url = reverse_lazy('app')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)
    
    # def get_initial(self):
    #     initial = super().get_initial()
    #     initial['first_name'] = self.request.user.first_name
    #     initial['last_name'] = self.request.user.last_name
    #     initial['username'] = self.request.user.username
    #     initial['profile_image'] = self.request.user.profile_image
    #     initial['phone_number'] = self.request.user.phone_number
    #     return initial

def logout_view(request):
    logout(request)
    return redirect('login')


class Notifications(LoginRequiredMixin, TemplateView):
    template_name = 'findit/notification.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notifications'] = Notification.objects.filter(to_user=self.request.user)
        return context
    def get_queryset(self):
        return self.request.user.notifications.order_by('-time_created')

def claim_item(request, item_id):
    item = LostItem.objects.get(id=item_id)

    Notification.objects.create(
        to_user=item.user,
        from_user=request.user,
        message=f" {request.user.username} has claimed the item you found : {item.description}"
    )
    messages.success(request, 'You have successfully submitted a claim for the item. The owner will be notified.')
    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))