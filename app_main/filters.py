from django_filters import rest_framework as filters
from .models import *


class ConversationDataFilter(filters.FilterSet):
    from_date = filters.DateFilter(field_name='created', lookup_expr="gte")
    to_date = filters.DateFilter(field_name='created', lookup_expr="lte")

    class Meta:
        model = Conversation
        fields = ['from_date', 'to_date',  ]


class MessageDataFilter(filters.FilterSet):
    from_date = filters.DateFilter(field_name='created', lookup_expr="gte")
    to_date = filters.DateFilter(field_name='created', lookup_expr="lte")

    class Meta:
        model = Message
        fields = ['from_date', 'to_date',  ]




