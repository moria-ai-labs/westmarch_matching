import matplotlib.pyplot as plt
import numpy as np

def generate_performance_plot():
    """
    Generates a plot comparing performance of difflib and rapidfuzz
    with 10% exact matches.
    """
    # Averaged Data for Plot (10% Exact Matches, Avg Word Len = 7)
    # N*M values (product of target list size and choice list size)
    nm_values = np.array([1000, 10000, 100000, 500000])

    # Average Time (s) for difflib
    difflib_times = np.array([
        0.002904,  # N*M = 1,000
        0.031906,  # N*M = 10,000
        0.277241,  # N*M = 100,000
        1.412573   # N*M = 500,000
    ])

    # Average Time (s) for rapidfuzz
    rapidfuzz_times = np.array([
        0.000946,  # N*M = 1,000
        0.009041,  # N*M = 10,000
        0.087245,  # N*M = 100,000
        0.422434   # N*M = 500,000
    ])

    plt.figure(figsize=(10, 6))

    plt.plot(nm_values, difflib_times, marker='o', linestyle='-', label='difflib (optimized)')
    plt.plot(nm_values, rapidfuzz_times, marker='s', linestyle='-', label='rapidfuzz (optimized)')

    plt.title('Performance Comparison (10% Exact Matches, Avg Word Len 7)')
    plt.xlabel('N*M (Product of Target List Size and Choice List Size)')
    plt.ylabel('Average Time (s)')

    # Using a log scale for y-axis can be helpful if times vary widely,
    # but for these values, linear might be okay. Let's try linear first.
    # If the small values are hard to distinguish, consider log scale for y.
    # plt.yscale('log')

    # Using a log scale for x-axis as N*M grows exponentially
    plt.xscale('log')

    plt.xticks(nm_values, [f'{val:,}' for val in nm_values]) # Format x-axis labels
    plt.minorticks_off() # Turn off minor ticks for x-axis with log scale if too cluttered

    plt.legend()
    plt.grid(True, which="both", ls="--", alpha=0.7) # Grid for both major and minor ticks if log scale
    plt.tight_layout()

    # Suggest filename for saving
    output_filename = "wordmatcher_performance_10perc_exact.png"
    plt.savefig(output_filename)
    print(f"Plot saved as {output_filename}")

    # plt.show() # Uncomment to display the plot directly if running locally

if __name__ == "__main__":
    # Check if matplotlib is installed, if not, provide a message.
    try:
        import matplotlib
    except ImportError:
        print("Matplotlib is not installed. Please install it to generate the plot:")
        print("  pip install matplotlib")
        exit()

    generate_performance_plot()
