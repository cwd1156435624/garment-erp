from django.urls import path
from .views import SearchView, SearchSuggestionView, AdvancedSearchView

urlpatterns = [
    # 全局搜索
    path('', SearchView.as_view(), name='global_search'),
    # 搜索建议
    path('suggestions/', SearchSuggestionView.as_view(), name='search_suggestions'),
    # 高级搜索
    path('advanced/', AdvancedSearchView.as_view(), name='advanced_search'),
]