from abc import abstractmethod

from dagster._core.asset_graph_view.asset_graph_view import AssetSlice

from .asset_condition import AssetCondition, AssetConditionResult
from .scheduling_condition_evaluation_context import SchedulingConditionEvaluationContext


class SliceSchedulingCondition(AssetCondition):
    """Base class for simple conditions which compute a simple slice of the asset graph."""

    @abstractmethod
    def compute_slice(self, context: SchedulingConditionEvaluationContext) -> AssetSlice: ...

    def evaluate(self, context: SchedulingConditionEvaluationContext) -> AssetConditionResult:
        # don't compute anything if there are no candidates
        if context.candidate_slice.is_empty:
            true_slice = context.asset_graph_view.create_empty_slice(context.asset_key)
        else:
            true_slice = self.compute_slice(context)

        return AssetConditionResult.create(context, true_slice.convert_to_valid_asset_subset())


class MissingSchedulingCondition(SliceSchedulingCondition):
    @property
    def description(self) -> str:
        return "Missing"

    def compute_slice(self, context: SchedulingConditionEvaluationContext) -> AssetSlice:
        return context.asset_graph_view.compute_missing_subslice(
            context.asset_key, from_slice=context.candidate_slice
        )


class InLatestTimeWindowCondition(SliceSchedulingCondition):
    @property
    def description(self) -> str:
        return "Within latest time window"

    def compute_slice(self, context: SchedulingConditionEvaluationContext) -> AssetSlice:
        return context.asset_graph_view.create_latest_time_window_slice(context.asset_key)