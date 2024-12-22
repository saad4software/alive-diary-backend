from django.contrib import admin
from django.urls import path, include


from rest_framework.documentation import include_docs_urls # new
from rest_framework.schemas import get_schema_view # new

from drf_yasg.views import get_schema_view # new
from drf_yasg import openapi # new

schema_view = get_schema_view(
    openapi.Info(
        title="Swagger API",
        default_version='v1',
    ),
    public=True,
)
API_DESCRIPTION = 'A Web API for creating and editing.' # new
API_TITLE = 'API' # new

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/account/', include('app_account.urls')),
    path('api/', include('app_main.urls')),

    path('docs/', include_docs_urls(title=API_TITLE,description=API_DESCRIPTION)), # new
    path('swagger/', schema_view.with_ui('swagger',cache_timeout=0),name="swagger-schema"), # new

]
