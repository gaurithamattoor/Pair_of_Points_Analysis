import java.util.*;

public class Main {

    static class Point {
        double x, y;

        Point(double x, double y) {
            this.x = x;
            this.y = y;
        }

        @Override
        public String toString() {
            return String.format(Locale.US, "(%.2f, %.2f)", x, y);
        }
    }

    static class Result {
        Point p1, p2;
        double distance;

        Result(Point p1, Point p2, double distance) {
            this.p1 = p1;
            this.p2 = p2;
            this.distance = distance;
        }
    }

    // Calculate Euclidean distance between two points
    static double distance(Point p1, Point p2) {
        double dx = p1.x - p2.x;
        double dy = p1.y - p2.y;
        return Math.hypot(dx, dy);
    }

    // ---------------- BRUTE FORCE ----------------
    static Result bruteForce(Point[] points) {
        if (points.length < 2) {
            return new Result(null, null, Double.POSITIVE_INFINITY);
        }

        Result best = new Result(
            points[0], points[1], distance(points[0], points[1])
        );

        for (int i = 0; i < points.length; i++) {
            for (int j = i + 1; j < points.length; j++) {
                double d = distance(points[i], points[j]);

                if (d < best.distance) {
                    best = new Result(points[i], points[j], d);
                }
            }
        }

        return best;
    }

    // ---------------- DIVIDE AND CONQUER ----------------

    static Result closestPair(Point[] points) {
        int n = points.length;

        if (n < 2) {
            return new Result(null, null, Double.POSITIVE_INFINITY);
        }

        Point[] byX = points.clone();
        Arrays.sort(byX, Comparator
            .comparingDouble((Point p) -> p.x)
            .thenComparingDouble(p -> p.y));

        Point[] byY = points.clone();
        Arrays.sort(byY, Comparator
            .comparingDouble((Point p) -> p.y)
            .thenComparingDouble(p -> p.x));

        return divide(byX, byY);
    }

    static Result divide(Point[] byX, Point[] byY) {
        int n = byX.length;

        // Base case: use brute force for small groups
        if (n <= 3) {
            return bruteForce(byX);
        }

        int mid = n / 2;
        Point[] leftX = Arrays.copyOfRange(byX, 0, mid);
        Point[] rightX = Arrays.copyOfRange(byX, mid, n);

        double midX = byX[mid].x;

        Set<Point> leftSet = Collections.newSetFromMap(
            new IdentityHashMap<Point, Boolean>()
        );
        leftSet.addAll(Arrays.asList(leftX));

        List<Point> leftYList = new ArrayList<>();
        List<Point> rightYList = new ArrayList<>();

        for (Point p : byY) {
            if (leftSet.contains(p)) {
                leftYList.add(p);
            } else {
                rightYList.add(p);
            }
        }

        Point[] leftY = leftYList.toArray(new Point[0]);
        Point[] rightY = rightYList.toArray(new Point[0]);

        Result leftResult = divide(leftX, leftY);
        Result rightResult = divide(rightX, rightY);

        Result best = leftResult.distance <= rightResult.distance
            ? leftResult : rightResult;

        double bestDistance = best.distance;

        // Collect points near the dividing line
        List<Point> strip = new ArrayList<>();

        for (Point p : byY) {
            if (Math.abs(p.x - midX) < bestDistance) {
                strip.add(p);
            }
        }

        // Points are already sorted by y.
        // Only compare points whose y difference is less than best distance.
        for (int i = 0; i < strip.size(); i++) {
            for (int j = i + 1;
                 j < strip.size()
                 && strip.get(j).y - strip.get(i).y < bestDistance;
                 j++) {

                double d = distance(strip.get(i), strip.get(j));

                if (d < best.distance) {
                    best = new Result(strip.get(i), strip.get(j), d);
                    bestDistance = d;
                }
            }
        }

        return best;
    }

    // ---------------- OUTPUT ----------------

    static void printResult(String name, Result result) {
        if (result.p1 == null || result.p2 == null) {
            System.out.println(name + ": Not enough points (N < 2).");
            return;
        }

        System.out.printf(
            Locale.US,
            "%s: %.6f, %s and %s%n",
            name,
            result.distance,
            result.p1,
            result.p2
        );
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        System.out.print("Enter number of points (N): ");
        int n = sc.nextInt();

        if (n < 0) {
            System.out.println("N cannot be negative.");
            sc.close();
            return;
        }

        Point[] points = new Point[n];
        Random random = new Random();

        // Generate random integer coordinates
        // Range: 0 to 9999
        for (int i = 0; i < n; i++) {
            int x = random.nextInt(10000);
            int y = random.nextInt(10000);
            points[i] = new Point(x, y);
        }

        System.out.println("\nGenerated Points:");
        for (int i = 0; i < n; i++) {
            System.out.println(i + ": " + points[i]);
        }

        // Measure Brute Force execution time
        long startBrute = System.nanoTime();
        Result bruteResult = bruteForce(points);
        long endBrute = System.nanoTime();

        // Measure Divide and Conquer execution time
        long startDC = System.nanoTime();
        Result dcResult = closestPair(points);
        long endDC = System.nanoTime();

        double bruteTimeMs = (endBrute - startBrute) / 1_000_000.0;
        double dcTimeMs = (endDC - startDC) / 1_000_000.0;

        System.out.println("\n--- RESULTS ---");
        printResult("Brute Force", bruteResult);
        printResult("Divide and Conquer", dcResult);

        System.out.printf(
            Locale.US,
            "Execution Time: Brute Force = %.3f ms, Divide and Conquer = %.3f ms%n",
            bruteTimeMs,
            dcTimeMs
        );

        // Verify both algorithms agree on minimum distance
        if (n < 2 ||
            Math.abs(bruteResult.distance - dcResult.distance) < 1e-9) {
            System.out.println("Verification: Both algorithms agree.");
        } else {
            System.out.println("Verification: Results do not match!");
        }

        sc.close();
    }
}