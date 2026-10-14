import math
import random
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

# =====================================================
# 1. INPUT POINTS FROM YOUR JAVA PROGRAM
# =====================================================

POINTS = [
    (2676.00, 4964.00),
    (535.00, 9998.00),
    (9085.00, 4561.00),
    (6465.00, 3379.00),
    (9976.00, 9828.00)
]

SHOW_ANIMATION = True

# Each point has a unique ID, even when coordinates are duplicates.
def make_points(coordinates):
    return [(x, y, i) for i, (x, y) in enumerate(coordinates)]


def distance(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


# =====================================================
# 2. BRUTE FORCE ALGORITHM
# =====================================================

def brute_force(points):
    if len(points) < 2:
        return float("inf"), None, None

    best_distance = float("inf")
    best_pair = (None, None)

    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            d = distance(points[i], points[j])

            if d < best_distance:
                best_distance = d
                best_pair = (points[i], points[j])

    return best_distance, best_pair[0], best_pair[1]


# =====================================================
# 3. DIVIDE AND CONQUER ALGORITHM
# =====================================================

def divide_and_conquer(points):
    if len(points) < 2:
        return float("inf"), None, None

    by_x = sorted(points, key=lambda p: (p[0], p[1], p[2]))
    by_y = sorted(points, key=lambda p: (p[1], p[0], p[2]))

    return solve(by_x, by_y)


def solve(by_x, by_y):
    n = len(by_x)

    # Base case
    if n <= 3:
        return brute_force(by_x)

    mid = n // 2
    left_x = by_x[:mid]
    right_x = by_x[mid:]
    mid_x = right_x[0][0]

    left_ids = {p[2] for p in left_x}

    left_y = [p for p in by_y if p[2] in left_ids]
    right_y = [p for p in by_y if p[2] not in left_ids]

    # Recursively solve both halves
    d1, a1, b1 = solve(left_x, left_y)
    d2, a2, b2 = solve(right_x, right_y)

    if d1 <= d2:
        best_distance, p1, p2 = d1, a1, b1
    else:
        best_distance, p1, p2 = d2, a2, b2

    # Build the strip around the dividing line
    strip = [
        p for p in by_y
        if abs(p[0] - mid_x) < best_distance
    ]

    # Compare nearby points in y-sorted order
    for i in range(len(strip)):
        j = i + 1

        while (
            j < len(strip)
            and strip[j][1] - strip[i][1] < best_distance
        ):
            d = distance(strip[i], strip[j])

            if d < best_distance:
                best_distance = d
                p1, p2 = strip[i], strip[j]

            j += 1

    return best_distance, p1, p2


# =====================================================
# 4. FIND THE DIVIDING LINE AND STRIP FOR THE PLOT
# =====================================================

def get_strip_information(points):
    by_x = sorted(points, key=lambda p: (p[0], p[1], p[2]))

    if len(by_x) < 2:
        return None

    mid = len(by_x) // 2
    left_half = by_x[:mid]
    right_half = by_x[mid:]
    mid_x = right_half[0][0]

    d_left, _, _ = brute_force(left_half)
    d_right, _, _ = brute_force(right_half)

    d = min(d_left, d_right)

    return mid_x, d


# =====================================================
# 5. PLOT ALL POINTS AND THE CLOSEST PAIRS
# =====================================================

def visualize_points(points, brute_result, dc_result):
    fig, ax = plt.subplots(figsize=(11, 7))

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]

    ax.scatter(
        xs, ys, color="black", s=80,
        zorder=5, label="Input points"
    )

    # Label every point
    for i, p in enumerate(points):
        ax.annotate(
            f"P{i}: ({p[0]:.0f}, {p[1]:.0f})",
            (p[0], p[1]),
            xytext=(7, 7),
            textcoords="offset points",
            fontsize=8
        )

    # Brute Force pair
    _, b1, b2 = brute_result
    if b1 is not None and b2 is not None:
        ax.plot(
            [b1[0], b2[0]], [b1[1], b2[1]],
            color="red", linewidth=3, linestyle="-",
            label="Brute Force pair", zorder=3
        )

    # Divide and Conquer pair
    _, d1, d2 = dc_result
    if d1 is not None and d2 is not None:
        ax.plot(
            [d1[0], d2[0]], [d1[1], d2[1]],
            color="blue", linewidth=2.5, linestyle="--",
            label="Divide and Conquer pair", zorder=4
        )

    # Dividing line and strip
    strip_info = get_strip_information(points)

    if strip_info is not None:
        mid_x, d = strip_info
        ymin, ymax = min(ys), max(ys)
        height = max(ymax - ymin, 1)

        ax.axvline(
            mid_x, color="green", linestyle=":",
            linewidth=2, label="Dividing line"
        )

        if math.isfinite(d):
            ax.add_patch(Rectangle(
                (mid_x - d, ymin),
                2 * d,
                height,
                facecolor="orange",
                alpha=0.18,
                edgecolor="orange",
                label=f"Strip region (width = 2d = {2*d:.2f})"
            ))

    ax.set_title("Closest Pair of Points: Brute Force vs Divide and Conquer")
    ax.set_xlabel("X coordinate")
    ax.set_ylabel("Y coordinate")
    ax.grid(True, linestyle=":", alpha=0.5)
    ax.legend(loc="best", fontsize=8)
    fig.tight_layout()


# =====================================================
# 6. RUNNING TIME VS INPUT SIZE
# =====================================================

def benchmark():
    sizes = [50, 100, 200, 400, 800, 1200]
    brute_times = []
    dc_times = []

    random.seed(42)

    print("\nRunning performance tests...")

    for n in sizes:
        # Same points are used for both algorithms at each N.
        test_points = make_points([
            (random.uniform(0, 10000),
             random.uniform(0, 10000))
            for _ in range(n)
        ])

        # Warm-up runs reduce some initial overhead.
        divide_and_conquer(test_points[:min(n, 10)])

        start = time.perf_counter()
        brute_result = brute_force(test_points)
        brute_ms = (time.perf_counter() - start) * 1000

        start = time.perf_counter()
        dc_result = divide_and_conquer(test_points)
        dc_ms = (time.perf_counter() - start) * 1000

        brute_times.append(brute_ms)
        dc_times.append(dc_ms)

        agrees = math.isclose(
            brute_result[0], dc_result[0],
            rel_tol=1e-9, abs_tol=1e-9
        )

        print(
            f"N={n:4d} | Brute Force={brute_ms:9.3f} ms | "
            f"Divide & Conquer={dc_ms:9.3f} ms | "
            f"Agree={agrees}"
        )

        if not agrees:
            raise AssertionError(
                f"Algorithms disagree for N={n}"
            )

    fig, ax = plt.subplots(figsize=(9, 6))

    ax.plot(
        sizes, brute_times, marker="o",
        color="red", label="Brute Force O(N²)"
    )
    ax.plot(
        sizes, dc_times, marker="s",
        color="blue", label="Divide and Conquer O(N log N)"
    )

    ax.set_title("Running Time vs Number of Points")
    ax.set_xlabel("Number of points (N)")
    ax.set_ylabel("Execution time (milliseconds)")
    ax.grid(True, linestyle=":", alpha=0.5)
    ax.legend()
    fig.tight_layout()


# =====================================================
# 7. OPTIONAL RECURSIVE SPLITTING ANIMATION
# =====================================================

def animate_splitting(points):
    if len(points) < 2:
        print("Animation needs at least two points.")
        return

    by_x = sorted(points, key=lambda p: (p[0], p[1], p[2]))
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]

    # Collect each recursive region and its split position.
    frames = []

    def collect_splits(region):
        if len(region) <= 1:
            return

        mid = len(region) // 2
        mid_x = region[mid][0]

        frames.append((region[:], mid_x, "Split"))
        collect_splits(region[:mid])
        collect_splits(region[mid:])
        frames.append((region[:], mid_x, "Merge"))

    collect_splits(by_x)

    fig, ax = plt.subplots(figsize=(9, 6))

    def update(frame_index):
        region, split_x, stage = frames[frame_index]
        ax.clear()

        ax.scatter(xs, ys, color="lightgray", s=45, label="All points")
        ax.scatter(
            [p[0] for p in region],
            [p[1] for p in region],
            color="blue" if stage == "Split" else "green",
            s=75, label="Current region"
        )

        for i, p in enumerate(points):
            ax.annotate(
                f"P{i}", (p[0], p[1]),
                xytext=(4, 4), textcoords="offset points"
            )

        ax.axvline(
            split_x, color="red", linestyle="--",
            label="Split position"
        )

        ax.set_title(
            f"Divide and Conquer Animation: {stage} "
            f"(step {frame_index + 1}/{len(frames)})"
        )
        ax.set_xlabel("X coordinate")
        ax.set_ylabel("Y coordinate")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="best")

    animation = FuncAnimation(
        fig, update, frames=len(frames),
        interval=900, repeat=True
    )

    # Keep a reference so the animation is not garbage-collected.
    fig._animation = animation
    fig.tight_layout()


# =====================================================
# 8. MAIN PROGRAM
# =====================================================

def main():
    points = make_points(POINTS)

    print("Generated Points:")
    for i, p in enumerate(points):
        print(f"{i}: ({p[0]:.2f}, {p[1]:.2f})")

    start = time.perf_counter()
    brute_result = brute_force(points)
    brute_ms = (time.perf_counter() - start) * 1000

    start = time.perf_counter()
    dc_result = divide_and_conquer(points)
    dc_ms = (time.perf_counter() - start) * 1000

    print("\n--- RESULTS ---")
    print(
        f"Brute Force: {brute_result[0]:.6f}, "
        f"{brute_result[1][:2]} and {brute_result[2][:2]}"
        if brute_result[1] is not None else
        "Brute Force: Not enough points"
    )
    print(
        f"Divide and Conquer: {dc_result[0]:.6f}, "
        f"{dc_result[1][:2]} and {dc_result[2][:2]}"
        if dc_result[1] is not None else
        "Divide and Conquer: Not enough points"
    )

    print(
        f"Execution Time: Brute Force = {brute_ms:.3f} ms, "
        f"Divide and Conquer = {dc_ms:.3f} ms"
    )

    if math.isclose(
        brute_result[0], dc_result[0],
        rel_tol=1e-9, abs_tol=1e-9
    ):
        print("Verification: Both algorithms agree.")
    else:
        print("Verification: Results do not match!")

    visualize_points(points, brute_result, dc_result)
    benchmark()

    if SHOW_ANIMATION:
        animate_splitting(points)

    # Display all figures
    plt.show()


if __name__ == "__main__":
    main()