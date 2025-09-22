import django_filters
from .models import Profile

class ProfileFilter(django_filters.FilterSet):
    gender = django_filters.CharFilter(field_name="gender", lookup_expr="iexact")
    pronouns = django_filters.CharFilter(field_name="pronouns", lookup_expr="iexact")
    context = django_filters.CharFilter(field_name="context", lookup_expr="icontains")

    class Meta:
        model = Profile
        fields = ["visibility", "gender", "pronouns", "context"]
