from django.urls import path

from .placement import feature_project
from .views import InactiveProjectListView, ProjectCreateView, ProjectDetailView, ProjectListView, ProjectUpdateView

urlpatterns = [
    path("<slug:slug>/feature", feature_project, name="feature_project"),
    path("", ProjectListView.as_view(), name="projects"),
    path("inactive", InactiveProjectListView.as_view(), name="inactive-projects"),
    path("new/", ProjectCreateView.as_view(), name="submit_project"),
    path("<slug:slug>", ProjectDetailView.as_view(), name="project"),
    path(
        "<slug:slug>/update",
        ProjectUpdateView.as_view(),
        name="project_update",
    ),
]
