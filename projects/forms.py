from django.forms import ModelForm

from .models import Comment, Project


class AddProject(ModelForm):
    def __init__(self, *args, **kwargs):
        super(AddProject, self).__init__(*args, **kwargs)

    class Meta:
        model = Project
        fields = [
            "title",
            "short_description",
            "url",
            "twitter_url",
            "github_url",
            "technology_suggestions_by_user",
        ]


class AddComment(ModelForm):
    def __init__(self, *args, **kwargs):
        super(AddComment, self).__init__(*args, **kwargs)

        for fieldname in ["comment"]:
            self.fields[fieldname].help_text = None
            self.fields[fieldname].widget.attrs.update(
                {
                    "class": "block border border-solid w-full p-2 mb-2 border-gray-300 rounded-md \
                              shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "rows": "3",
                }
            )

    class Meta:
        model = Comment
        fields = [
            "comment",
        ]


class ProjectUpdateViewForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProjectUpdateViewForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.help_text = None
            field.widget.attrs["class"] = "bw-form-checkbox" if name == "is_for_sale" else "bw-form-input"
            if name in {"description", "technology_suggestions_by_user"}:
                field.widget.attrs["rows"] = 6

    class Meta:
        model = Project
        fields = [
            "title",
            "url",
            "short_description",
            "description",
            "homepage_screenshot",
            "twitter_url",
            "github_url",
            "technology_suggestions_by_user",
            "is_for_sale",
            "sale_link",
        ]
