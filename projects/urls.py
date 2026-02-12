from django.urls import path

from .views import InactiveProjectListView, ProjectCreateView, ProjectDetailView, ProjectListView, ProjectUpdateView

urlpatterns = [
    path("", ProjectListView.as_view(), name="projects"),
    path("inactive", InactiveProjectListView.as_view(), name="inactive-projects"),
    path("<slug:slug>", ProjectDetailView.as_view(), name="project"),
    path(
        "<slug:slug>/update",
        ProjectUpdateView.as_view(),
        name="project_update",
    ),
    path("new/", ProjectCreateView.as_view(), name="submit_project"),
]
