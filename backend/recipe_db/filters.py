from django_filters import rest_framework as filters

from .models import Recipe


class M2MFilter(filters.Filter):

    def filter(self, queryset, filter_value):
        if not filter_value:
            return queryset
        filter_values = filter_value.split(",")
        for value in filter_values:
            queryset = queryset.filter(labels=value)
        return queryset


class RecipeFilter(filters.FilterSet):
    min_preparation_time = filters.NumberFilter(
        field_name="preparation_time", lookup_expr="gte"
    )
    max_preparation_time = filters.NumberFilter(
        field_name="preparation_time", lookup_expr="lte"
    )
    labels = M2MFilter(field_name="labels")

    class Meta:
        model = Recipe
        fields = ["min_preparation_time", "max_preparation_time", "labels"]
