"""Metric registry for managing and organizing metrics."""

from typing import Dict, List, Optional

from mmap_eval.core.metric import BaseMetric


class MetricRegistry:
    """Registry for managing evaluation metrics.

    Organizes metrics by layer and provides lookup functionality.
    """

    def __init__(self) -> None:
        """Initialize the metric registry."""
        self._metrics: Dict[int, List[BaseMetric]] = {1: [], 2: [], 3: [], 4: [], 5: []}
        self._metrics_by_name: Dict[str, BaseMetric] = {}

    def register(self, metric: BaseMetric) -> None:
        """Register a metric.

        Args:
            metric: Metric to register

        Raises:
            ValueError: If metric name already registered
        """
        if metric.name in self._metrics_by_name:
            raise ValueError(f"Metric '{metric.name}' is already registered")

        self._metrics[metric.layer].append(metric)
        self._metrics_by_name[metric.name] = metric

    def unregister(self, metric_name: str) -> None:
        """Unregister a metric by name.

        Args:
            metric_name: Name of metric to unregister

        Raises:
            KeyError: If metric not found
        """
        if metric_name not in self._metrics_by_name:
            raise KeyError(f"Metric '{metric_name}' not found in registry")

        metric = self._metrics_by_name[metric_name]
        self._metrics[metric.layer].remove(metric)
        del self._metrics_by_name[metric_name]

    def get_metrics_by_layer(self, layer: int) -> List[BaseMetric]:
        """Get all metrics for a specific layer.

        Args:
            layer: Layer number (1-5)

        Returns:
            List of metrics for the layer
        """
        if layer not in self._metrics:
            raise ValueError(f"Invalid layer: {layer}")
        return self._metrics[layer].copy()

    def get_metric(self, name: str) -> Optional[BaseMetric]:
        """Get a metric by name.

        Args:
            name: Metric name

        Returns:
            Metric if found, None otherwise
        """
        return self._metrics_by_name.get(name)

    def get_all_metrics(self) -> List[BaseMetric]:
        """Get all registered metrics.

        Returns:
            List of all metrics
        """
        all_metrics = []
        for layer_metrics in self._metrics.values():
            all_metrics.extend(layer_metrics)
        return all_metrics

    def count(self) -> int:
        """Get total number of registered metrics."""
        return len(self._metrics_by_name)

    def count_by_layer(self, layer: int) -> int:
        """Get number of metrics in a specific layer."""
        return len(self._metrics.get(layer, []))

    def clear(self) -> None:
        """Clear all registered metrics."""
        self._metrics = {1: [], 2: [], 3: [], 4: [], 5: []}
        self._metrics_by_name.clear()

    def __repr__(self) -> str:
        layer_counts = {layer: len(metrics) for layer, metrics in self._metrics.items()}
        return f"MetricRegistry(total={self.count()}, by_layer={layer_counts})"
