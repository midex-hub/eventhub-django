from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Event, Category


class HomeView(ListView):
    model = Event
    template_name = 'events/home.html'
    context_object_name = 'hosted_events'

    def get_queryset(self):
        from django.utils import timezone
        # Show completed/hosted events (events that have already happened)
        # Either status='completed' OR end_date has passed
        return Event.objects.filter(
            status='completed'
        ).order_by('-end_date')[:6]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Featured events - also show completed/hosted featured events
        ctx['featured_events'] = Event.objects.filter(
            status='completed', is_featured=True
        )[:3]
        ctx['categories'] = Category.objects.all()
        # Add total events count for dynamic stats
        ctx['total_events'] = Event.objects.filter(status='completed').count()
        return ctx


class EventListView(ListView):
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'
    paginate_by = 9

    def get_queryset(self):
        from django.utils import timezone
        qs = Event.objects.filter(status='published')
        q = self.request.GET.get('q', '')
        category = self.request.GET.get('category', '')
        sort = self.request.GET.get('sort', 'date')
        location = self.request.GET.get('location', '')
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(location__icontains=q))
        if category:
            qs = qs.filter(category__slug=category)
        if location:
            qs = qs.filter(location__icontains=location)
        if sort == 'date':
            qs = qs.order_by('start_date')
        elif sort == 'category':
            qs = qs.order_by('category__name')
        elif sort == 'location':
            qs = qs.order_by('location')
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = Category.objects.all()
        ctx['q'] = self.request.GET.get('q', '')
        ctx['selected_category'] = self.request.GET.get('category', '')
        ctx['sort'] = self.request.GET.get('sort', 'date')
        return ctx


class EventDetailView(DetailView):
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['ticket_types'] = self.object.ticket_types.all()
        ctx['speakers'] = self.object.speakers.all()
        ctx['related_events'] = Event.objects.filter(
            category=self.object.category, status='published'
        ).exclude(pk=self.object.pk)[:3]
        return ctx
