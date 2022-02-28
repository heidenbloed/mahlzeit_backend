from rest_framework import viewsets, parsers, mixins
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .serializers import *
from .models import Recipe, Ingredient, QuantifiedIngredient, IngredientCategory, Unit, Label, RecipeImage
from .filters import RecipeFilter


class RecipeView(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = RecipeFilter
    search_fields = ['name']
    ordering_fields = ['name', 'preparation_time']
    ordering = ['name']

    def get_serializer_class(self):
        if self.action == 'list':
            return RecipeShortSerializer
        if self.action == 'retrieve':
            return RecipeFullSerializer
        else:
            return RecipeEditSerializer

    # def retrieve(self, request, *args, **kwargs):
    #     # time.sleep(1)
    #     return super().retrieve(request, *args, **kwargs)


class QuantifiedIngredientView(viewsets.ModelViewSet):
    serializer_class = QuantifiedIngredientSerializer
    queryset = QuantifiedIngredient.objects.all()


class IngredientView(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = '__all__'
    ordering = ['name']

    def get_serializer_class(self):
        if self.action == 'list':
            return IngredientShortSerializer
        if self.action == 'retrieve':
            return IngredientFullSerializer
        else:
            return IngredientEditSerializer


class UnitView(viewsets.ReadOnlyModelViewSet):
    serializer_class = UnitSerializer
    queryset = Unit.objects.all()


class IngredientCategoryView(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientCategorySerializer
    queryset = IngredientCategory.objects.all()


class LabelView(viewsets.ReadOnlyModelViewSet):
    serializer_class = LabelSerializer
    queryset = Label.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = '__all__'
    ordering = ['name']


class RecipeImageView(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    parser_classes = (parsers.MultiPartParser,)
    serializer_class = RecipeImageFullSerializer
    queryset = RecipeImage.objects.all()
