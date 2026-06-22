"""Animated single-layer perceptron from scratch using NumPy.

Mathematical update rule:
For each training example ``(x_i, y_i)`` where ``y_i`` is either ``-1`` or
``1``, the perceptron computes ``z_i = w . x_i + b``. If the point is
misclassified, meaning ``y_i * z_i <= 0``, the parameters are updated as:

    w <- w + learning_rate * y_i * x_i
    b <- b + learning_rate * y_i

Correctly classified samples do not change the parameters. This rule pushes
the decision boundary toward separating the two classes.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.collections import LineCollection
from matplotlib.colors import to_rgb
from matplotlib.widgets import Button, Slider


class Perceptron:
    """Elementary single-layer perceptron for binary labels {-1, 1}."""

    def __init__(self, learning_rate=0.01, n_iterations=1000):
        self.learning_rate = learning_rate
        self.n_iterations = n_iterations
        self.weights = None
        self.bias = 0.0
        self._rng = np.random.default_rng(42)
        self.update_history = []
        self.epoch_history = []

    def fit(self, X, y):
        """Train the perceptron and record snapshots for animation."""
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=int)

        if X.ndim != 2:
            raise ValueError("X must be a 2D NumPy array.")
        if y.ndim != 1 or y.shape[0] != X.shape[0]:
            raise ValueError("y must be a 1D array with one label per sample.")
        if not np.all(np.isin(y, [-1, 1])):
            raise ValueError("All labels in y must be either -1 or 1.")

        n_features = X.shape[1]
        self.weights = self._rng.normal(loc=0.0, scale=0.01, size=n_features)
        self.bias = 0.0
        self.update_history = [self._snapshot(X, y, epoch=0, update_count=0)]
        self.epoch_history = []
        update_count = 0

        for epoch in range(1, self.n_iterations + 1):
            epoch_updates = 0

            for sample_index, (x_i, y_i) in enumerate(zip(X, y)):
                linear_output = np.dot(x_i, self.weights) + self.bias

                if y_i * linear_output <= 0:
                    self.weights += self.learning_rate * y_i * x_i
                    self.bias += self.learning_rate * y_i
                    epoch_updates += 1
                    update_count += 1
                    self.update_history.append(
                        self._snapshot(
                            X,
                            y,
                            epoch=epoch,
                            update_count=update_count,
                            sample_index=sample_index,
                        )
                    )

            self.epoch_history.append(
                {
                    "epoch": epoch,
                    "updates": epoch_updates,
                    "accuracy": accuracy(y, self.predict(X)),
                }
            )

        return self

    def predict(self, X):
        """Return class predictions {-1, 1} using a step activation."""
        if self.weights is None:
            raise ValueError("The perceptron must be fitted before prediction.")

        X = np.asarray(X, dtype=float)
        linear_output = np.dot(X, self.weights) + self.bias
        return np.where(linear_output >= 0, 1, -1)

    def decision_boundary(self, x1):
        """Return x2 values for the boundary w1*x1 + w2*x2 + b = 0."""
        if self.weights is None:
            raise ValueError("The perceptron must be fitted before plotting.")
        if len(self.weights) != 2:
            raise ValueError("Decision boundary plotting requires 2D data.")
        if np.isclose(self.weights[1], 0.0):
            raise ValueError("Cannot compute x2 when the second weight is zero.")

        return -(self.weights[0] * x1 + self.bias) / self.weights[1]

    def _snapshot(self, X, y, epoch, update_count, sample_index=None):
        """Capture the model state needed to replay training visually."""
        scores = np.dot(X, self.weights) + self.bias
        predictions = np.where(scores >= 0, 1, -1)

        return {
            "epoch": epoch,
            "update_count": update_count,
            "sample_index": sample_index,
            "weights": self.weights.copy(),
            "bias": self.bias,
            "accuracy": accuracy(y, predictions),
            "misclassified": predictions != y,
        }


def generate_linearly_separable_data(n_samples=100, random_seed=7):
    """Generate reproducible 2D data separated by a hidden linear boundary."""
    rng = np.random.default_rng(random_seed)
    half = n_samples // 2
    true_weights = np.array([1.2, -0.85])
    true_bias = -0.15
    margin = 0.35
    class_negative = []
    class_positive = []

    while len(class_negative) < half or len(class_positive) < n_samples - half:
        candidate = rng.uniform(low=-4.0, high=4.0, size=2)
        score = np.dot(candidate, true_weights) + true_bias

        if score < -margin and len(class_negative) < half:
            class_negative.append(candidate)
        elif score > margin and len(class_positive) < n_samples - half:
            class_positive.append(candidate)

    class_negative = np.array(class_negative)
    class_positive = np.array(class_positive)
    X = np.vstack((class_negative, class_positive))
    y = np.hstack((-np.ones(half, dtype=int), np.ones(n_samples - half, dtype=int)))

    shuffled_indices = rng.permutation(n_samples)
    return X[shuffled_indices], y[shuffled_indices]


def train_test_split(X, y, train_ratio=0.8):
    """Split already-shuffled arrays into train and test partitions."""
    split_index = int(train_ratio * len(X))
    return X[:split_index], X[split_index:], y[:split_index], y[split_index:]


def accuracy(y_true, y_pred):
    """Compute classification accuracy."""
    return np.mean(y_true == y_pred)


def apply_visual_style():
    """Set a focused instrument-panel style without requiring custom fonts."""
    plt.rcParams.update(
        {
            "figure.facecolor": "#0B1115",
            "axes.facecolor": "#101A20",
            "axes.edgecolor": "#354A52",
            "axes.labelcolor": "#E6ECE8",
            "axes.titlecolor": "#F2B94B",
            "xtick.color": "#A9B8B4",
            "ytick.color": "#A9B8B4",
            "grid.color": "#273840",
            "font.family": ["Segoe UI", "DejaVu Sans", "Arial"],
            "font.size": 10,
            "axes.titlesize": 12,
            "axes.titleweight": "bold",
        }
    )


def boundary_values(weights, bias, x1_values):
    """Return boundary y-values for an arbitrary parameter snapshot."""
    if np.isclose(weights[1], 0.0):
        return np.full_like(x1_values, np.nan)

    return -(weights[0] * x1_values + bias) / weights[1]


class PerceptronDashboard:
    """Interactive Matplotlib dashboard for retraining a perceptron."""

    def __init__(
        self,
        X_train,
        y_train,
        X_test,
        y_test,
        learning_rate=0.01,
        n_iterations=60,
    ):
        self.X_train = X_train
        self.y_train = y_train
        self.X_test = X_test
        self.y_test = y_test
        self.default_learning_rate = learning_rate
        self.default_n_iterations = n_iterations
        self.animation = None

        self.palette = {
            "paper": "#E6ECE8",
            "muted": "#A9B8B4",
            "panel": "#101A20",
            "panel_alt": "#0F171C",
            "rail": "#354A52",
            "negative": "#43B3C5",
            "positive": "#FF7058",
            "boundary": "#F2B94B",
            "warning": "#F7E37B",
            "trail": "#79D0B7",
            "button": "#182832",
            "button_hover": "#223743",
        }

        self._train(learning_rate, n_iterations)
        self._build_figure()
        self._draw_static_field()
        self._build_trace()
        self._refresh_trace_limits()
        self._start_animation()

    def _train(self, learning_rate, n_iterations):
        self.perceptron = Perceptron(
            learning_rate=float(learning_rate),
            n_iterations=int(n_iterations),
        )
        self.perceptron.fit(self.X_train, self.y_train)
        self.epochs = np.array([item["epoch"] for item in self.perceptron.epoch_history])
        self.epoch_accuracy = np.array(
            [item["accuracy"] for item in self.perceptron.epoch_history]
        )
        self.epoch_updates = np.array(
            [item["updates"] for item in self.perceptron.epoch_history]
        )

    def _build_figure(self):
        apply_visual_style()
        self.fig = plt.figure(figsize=(14.8, 8.8), constrained_layout=False)
        grid = self.fig.add_gridspec(
            nrows=2,
            ncols=2,
            left=0.055,
            right=0.965,
            bottom=0.08,
            top=0.805,
            width_ratios=(2.45, 1.0),
            height_ratios=(3.15, 1.08),
            wspace=0.17,
            hspace=0.34,
        )
        self.ax_space = self.fig.add_subplot(grid[0, 0])
        self.ax_panel = self.fig.add_subplot(grid[0, 1])
        self.ax_trace = self.fig.add_subplot(grid[1, :])
        self.ax_updates = self.ax_trace.twinx()

        self.fig.text(
            0.055,
            0.965,
            "Perceptron Learning Console",
            color=self.palette["paper"],
            fontsize=22,
            fontweight="bold",
            ha="left",
            va="top",
        )
        self.fig.text(
            0.055,
            0.925,
            "Adjust the learning parameters, retrain, and watch the boundary update.",
            color=self.palette["muted"],
            fontsize=10.5,
            ha="left",
            va="top",
        )
        self.status_text = self.fig.text(
            0.055,
            0.838,
            "Ready",
            color=self.palette["muted"],
            fontsize=9.5,
            ha="left",
            va="top",
        )

        self._build_controls()

    def _build_controls(self):
        ax_learning_rate = self.fig.add_axes([0.13, 0.865, 0.22, 0.035])
        ax_iterations = self.fig.add_axes([0.45, 0.865, 0.22, 0.035])
        ax_apply = self.fig.add_axes([0.685, 0.858, 0.105, 0.048])
        ax_reset = self.fig.add_axes([0.81, 0.858, 0.105, 0.048])

        self.learning_rate_slider = Slider(
            ax=ax_learning_rate,
            label="Learning rate",
            valmin=0.001,
            valmax=0.2,
            valinit=self.default_learning_rate,
            valstep=0.001,
            valfmt="%.3f",
            color=self.palette["boundary"],
            track_color="#22343C",
        )
        self.iterations_slider = Slider(
            ax=ax_iterations,
            label="Iterations",
            valmin=5,
            valmax=250,
            valinit=self.default_n_iterations,
            valstep=1,
            valfmt="%0.0f",
            color=self.palette["trail"],
            track_color="#22343C",
        )
        self.apply_button = Button(
            ax_apply,
            "Apply",
            color=self.palette["button"],
            hovercolor=self.palette["button_hover"],
        )
        self.reset_button = Button(
            ax_reset,
            "Reset",
            color=self.palette["button"],
            hovercolor=self.palette["button_hover"],
        )

        for slider in (self.learning_rate_slider, self.iterations_slider):
            slider.label.set_color(self.palette["paper"])
            slider.label.set_fontsize(9.5)
            slider.valtext.set_color(self.palette["paper"])
            slider.valtext.set_fontsize(9)
            for spine in slider.ax.spines.values():
                spine.set_edgecolor(self.palette["rail"])

        for button in (self.apply_button, self.reset_button):
            button.label.set_color(self.palette["paper"])
            button.label.set_fontweight("bold")

        self.learning_rate_slider.on_changed(self._mark_changes_pending)
        self.iterations_slider.on_changed(self._mark_changes_pending)
        self.apply_button.on_clicked(self._apply_parameters)
        self.reset_button.on_clicked(self._reset_parameters)

    def _draw_static_field(self):
        x1_min = min(self.X_train[:, 0].min(), self.X_test[:, 0].min()) - 0.6
        x1_max = max(self.X_train[:, 0].max(), self.X_test[:, 0].max()) + 0.6
        x2_min = min(self.X_train[:, 1].min(), self.X_test[:, 1].min()) - 0.6
        x2_max = max(self.X_train[:, 1].max(), self.X_test[:, 1].max()) + 0.6
        self.x1_values = np.linspace(x1_min, x1_max, 200)

        self.ax_space.set_title(
            "Training field",
            loc="left",
            pad=12,
        )
        self.ax_space.set_xlabel("Feature x1")
        self.ax_space.set_ylabel("Feature x2")
        self.ax_space.set_xlim(x1_min, x1_max)
        self.ax_space.set_ylim(x2_min, x2_max)
        self.ax_space.grid(True, alpha=0.5)

        scatter_specs = [
            (self.X_train, self.y_train, -1, "Train -1", self.palette["negative"], "o", 0.92),
            (self.X_train, self.y_train, 1, "Train +1", self.palette["positive"], "o", 0.92),
            (self.X_test, self.y_test, -1, "Test -1", self.palette["negative"], "s", 0.32),
            (self.X_test, self.y_test, 1, "Test +1", self.palette["positive"], "s", 0.32),
        ]

        for X_split, y_split, class_label, label, color, marker, alpha in scatter_specs:
            points = X_split[y_split == class_label]
            self.ax_space.scatter(
                points[:, 0],
                points[:, 1],
                label=label,
                marker=marker,
                s=76,
                c=color,
                alpha=alpha,
                edgecolors="#0B1115",
                linewidths=0.75,
            )

        self.trail_collection = LineCollection([], linewidths=1.15)
        self.ax_space.add_collection(self.trail_collection)
        self.boundary_line, = self.ax_space.plot(
            [],
            [],
            color=self.palette["boundary"],
            linewidth=3.0,
            label="Current boundary",
        )
        self.mistake_scatter = self.ax_space.scatter(
            [],
            [],
            s=180,
            facecolors="none",
            edgecolors=self.palette["warning"],
            linewidths=2.1,
            label="Wrong now",
        )
        self.current_scatter = self.ax_space.scatter(
            [],
            [],
            s=360,
            facecolors="none",
            edgecolors=self.palette["paper"],
            linewidths=2.3,
            label="Latest update",
        )

        legend = self.ax_space.legend(
            loc="upper left",
            frameon=True,
            ncols=2,
            facecolor=self.palette["panel_alt"],
            edgecolor=self.palette["rail"],
            labelcolor=self.palette["paper"],
            fontsize=8.8,
            borderpad=0.65,
            handletextpad=0.45,
            columnspacing=0.9,
        )
        legend.get_frame().set_alpha(0.92)

    def _build_trace(self):
        self.ax_trace.set_title("Epoch trace", loc="left", pad=12)
        self.ax_trace.set_xlabel("Epoch")
        self.ax_trace.set_ylabel("Training accuracy", color=self.palette["paper"])
        self.ax_trace.set_ylim(0.0, 1.05)
        self.ax_trace.grid(True, alpha=0.5)
        self.trace_background_line, = self.ax_trace.plot(
            [],
            [],
            color=self.palette["trail"],
            alpha=0.18,
            linewidth=2,
        )
        self.accuracy_line, = self.ax_trace.plot(
            [],
            [],
            color=self.palette["boundary"],
            linewidth=2.7,
        )

        self.ax_updates.set_ylabel("Updates in epoch", color=self.palette["muted"])
        self.ax_updates.tick_params(axis="y", colors=self.palette["muted"])
        self.update_background_line, = self.ax_updates.plot(
            [],
            [],
            color=self.palette["positive"],
            alpha=0.16,
            linewidth=2,
        )
        self.update_line, = self.ax_updates.plot(
            [],
            [],
            color=self.palette["positive"],
            linewidth=2.1,
        )

    def _refresh_trace_limits(self):
        max_updates = max(1, int(self.epoch_updates.max(initial=1)))
        self.ax_trace.set_xlim(1, max(1, self.perceptron.n_iterations))
        self.ax_updates.set_ylim(0, max_updates + 1)
        self.trace_background_line.set_data(self.epochs, self.epoch_accuracy)
        self.update_background_line.set_data(self.epochs, self.epoch_updates)
        self.accuracy_line.set_data([], [])
        self.update_line.set_data([], [])

    def _draw_panel(self, snapshot):
        self.ax_panel.clear()
        self.ax_panel.set_facecolor(self.palette["panel"])
        self.ax_panel.set_xticks([])
        self.ax_panel.set_yticks([])
        for spine in self.ax_panel.spines.values():
            spine.set_edgecolor(self.palette["rail"])

        weights = snapshot["weights"]
        train_predictions = np.where(
            np.dot(self.X_train, weights) + snapshot["bias"] >= 0,
            1,
            -1,
        )
        test_predictions = np.where(
            np.dot(self.X_test, weights) + snapshot["bias"] >= 0,
            1,
            -1,
        )
        train_accuracy = accuracy(self.y_train, train_predictions)
        test_accuracy = accuracy(self.y_test, test_predictions)
        wrong_count = int(snapshot["misclassified"].sum())

        self.ax_panel.text(
            0.07,
            0.93,
            "Live state",
            color=self.palette["boundary"],
            fontsize=13,
            fontweight="bold",
            transform=self.ax_panel.transAxes,
        )
        self.ax_panel.text(
            0.07,
            0.87,
            f"lr {self.perceptron.learning_rate:.3f}   iterations {self.perceptron.n_iterations}",
            color=self.palette["muted"],
            fontsize=8.8,
            transform=self.ax_panel.transAxes,
        )

        stats = [
            ("Epoch", f"{snapshot['epoch']:d}", self.palette["paper"]),
            ("Corrections", f"{snapshot['update_count']:d}", self.palette["paper"]),
            ("Wrong now", f"{wrong_count:d}", self.palette["warning"]),
            ("Train accuracy", f"{train_accuracy:.2%}", self.palette["paper"]),
            ("Test accuracy", f"{test_accuracy:.2%}", self.palette["paper"]),
        ]
        y_position = 0.74
        for label, value, color in stats:
            self.ax_panel.text(
                0.08,
                y_position,
                label,
                color=self.palette["muted"],
                fontsize=9.2,
                transform=self.ax_panel.transAxes,
            )
            self.ax_panel.text(
                0.92,
                y_position,
                value,
                color=color,
                fontsize=11,
                fontweight="bold",
                ha="right",
                transform=self.ax_panel.transAxes,
            )
            y_position -= 0.105

        weights_rows = [
            ("w1", f"{weights[0]: .3f}"),
            ("w2", f"{weights[1]: .3f}"),
            ("bias", f"{snapshot['bias']: .3f}"),
        ]
        y_position = 0.21
        for label, value in weights_rows:
            self.ax_panel.text(
                0.08,
                y_position,
                label,
                color=self.palette["muted"],
                fontsize=9.2,
                transform=self.ax_panel.transAxes,
            )
            self.ax_panel.text(
                0.92,
                y_position,
                value,
                color=self.palette["paper"],
                fontsize=10.2,
                fontfamily="DejaVu Sans Mono",
                ha="right",
                transform=self.ax_panel.transAxes,
            )
            y_position -= 0.08

    def _update(self, frame_index):
        snapshot = self.perceptron.update_history[frame_index]
        weights = snapshot["weights"]
        self.boundary_line.set_data(
            self.x1_values,
            boundary_values(weights, snapshot["bias"], self.x1_values),
        )

        trail_start = max(0, frame_index - 14)
        trail_segments = []
        trail_colors = []
        trail_count = max(1, frame_index - trail_start)
        for index, old_snapshot in enumerate(
            self.perceptron.update_history[trail_start:frame_index]
        ):
            y_values = boundary_values(
                old_snapshot["weights"],
                old_snapshot["bias"],
                self.x1_values,
            )
            trail_segments.append(np.column_stack((self.x1_values, y_values)))
            alpha = 0.08 + 0.38 * ((index + 1) / trail_count)
            trail_colors.append((*to_rgb(self.palette["trail"]), alpha))

        self.trail_collection.set_segments(trail_segments)
        self.trail_collection.set_color(trail_colors)

        wrong_points = self.X_train[snapshot["misclassified"]]
        self.mistake_scatter.set_offsets(
            wrong_points if len(wrong_points) else np.empty((0, 2))
        )

        sample_index = snapshot["sample_index"]
        if sample_index is None:
            self.current_scatter.set_offsets(np.empty((0, 2)))
        else:
            self.current_scatter.set_offsets(self.X_train[sample_index].reshape(1, 2))

        current_epoch = max(1, snapshot["epoch"])
        epoch_mask = self.epochs <= current_epoch
        self.accuracy_line.set_data(
            self.epochs[epoch_mask],
            self.epoch_accuracy[epoch_mask],
        )
        self.update_line.set_data(
            self.epochs[epoch_mask],
            self.epoch_updates[epoch_mask],
        )
        self._draw_panel(snapshot)

        return (
            self.boundary_line,
            self.trail_collection,
            self.mistake_scatter,
            self.current_scatter,
            self.accuracy_line,
            self.update_line,
        )

    def _start_animation(self):
        if self.animation is not None:
            event_source = getattr(self.animation, "event_source", None)
            if event_source is not None:
                event_source.stop()

        frame_count = len(self.perceptron.update_history)
        interval = 140 if frame_count < 120 else 70
        self.animation = FuncAnimation(
            self.fig,
            self._update,
            frames=frame_count,
            interval=interval,
            repeat=False,
            blit=False,
        )
        self._update(0)
        self.fig.canvas.draw_idle()

    def _mark_changes_pending(self, _):
        self.status_text.set_text("Changes ready. Click Apply to retrain.")
        self.status_text.set_color(self.palette["boundary"])
        self.fig.canvas.draw_idle()

    def _apply_parameters(self, _):
        learning_rate = float(self.learning_rate_slider.val)
        n_iterations = int(self.iterations_slider.val)
        self._train(learning_rate, n_iterations)
        self._refresh_trace_limits()
        self._start_animation()
        self.status_text.set_text(
            f"Retrained with learning_rate={learning_rate:.3f}, iterations={n_iterations}"
        )
        self.status_text.set_color(self.palette["muted"])
        self.fig.canvas.draw_idle()

    def _reset_parameters(self, _):
        self.learning_rate_slider.set_val(self.default_learning_rate)
        self.iterations_slider.set_val(self.default_n_iterations)
        self._apply_parameters(None)


def plot_training_dashboard(perceptron, X_train, y_train, X_test, y_test):
    """Create the interactive dashboard for a fitted or configured perceptron."""
    return PerceptronDashboard(
        X_train,
        y_train,
        X_test,
        y_test,
        learning_rate=perceptron.learning_rate,
        n_iterations=perceptron.n_iterations,
    )


def main():
    X, y = generate_linearly_separable_data(n_samples=100, random_seed=7)
    X_train, X_test, y_train, y_test = train_test_split(X, y, train_ratio=0.8)

    perceptron = Perceptron(learning_rate=0.01, n_iterations=60)
    perceptron.fit(X_train, y_train)

    train_predictions = perceptron.predict(X_train)
    test_predictions = perceptron.predict(X_test)

    print("Final weights:", perceptron.weights)
    print("Final bias:", perceptron.bias)
    print(f"Training accuracy: {accuracy(y_train, train_predictions):.2%}")
    print(f"Test accuracy: {accuracy(y_test, test_predictions):.2%}")
    print(f"Recorded training updates: {len(perceptron.update_history) - 1}")

    animation = plot_training_dashboard(perceptron, X_train, y_train, X_test, y_test)
    plt.show()
    return animation


if __name__ == "__main__":
    main()
