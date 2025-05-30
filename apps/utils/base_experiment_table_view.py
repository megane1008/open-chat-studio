from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q
from django_tables2 import SingleTableView

from apps.teams.mixins import LoginAndTeamRequiredMixin
from apps.utils.search import similarity_search


class BaseExperimentTableView(LoginAndTeamRequiredMixin, SingleTableView, PermissionRequiredMixin):
    paginate_by = 25
    template_name = "table/single_table.html"

    def get_queryset(self):
        query_set = (
            self.model.objects.get_all()
            .filter(team=self.request.team, working_version__isnull=True)
            .order_by("is_archived")
        )
        show_archived = self.request.GET.get("show_archived") == "on"
        if not show_archived:
            query_set = query_set.filter(is_archived=False)

        search = self.request.GET.get("search")
        if search:
            query_set = similarity_search(
                query_set,
                search_phase=search,
                columns=["name", "description"],
                extra_conditions=Q(owner__username__icontains=search),
            )
        return query_set
