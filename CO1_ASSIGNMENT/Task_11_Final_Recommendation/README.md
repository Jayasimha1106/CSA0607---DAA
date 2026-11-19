# Task 11: Final Design Recommendation (4 marks)

**Recommended (general case, before the Day-4 constraints): binary search on a sorted array.**

- **Why over linear search:** measured 3.0 microseconds vs 23.7 ms per search at n = 10^6 (about 7,800x faster); only 19.4 comparisons vs 723,410. Sorting (2.38 s) is recovered after about 100 searches.
- **Why over hashing at this stage:** the update rate was unknown. Binary search has a deterministic O(log n) worst case with no collision risk, minimal memory (just the array), and supports ordered operations such as range queries on registration numbers (for example, a whole batch). Hash search is faster in raw time (0.62 microseconds) and cheaper to build (0.86 s), so this choice trades some speed for predictability and ordered access.
- **Theoretical efficiency:** preprocessing Theta(n log n), search Theta(log n).
- **Experimental performance:** comparisons 9.5 / 13.1 / 16.3 / 19.4 for n = 10^3 to 10^6, matching log2 n; time per search only 3.1x higher for 1000x more data.
- **Preprocessing cost:** 2.38 s at n = 10^6 (18.7 million comparisons).
- **Trade-offs and limitations:** inserting into a sorted array costs O(n); frequent updates need a balanced tree or a merge strategy. Recursion uses O(log n) stack (about 20 frames at 10^6).
- **Scalability:** a 1000x larger database only doubles the comparisons, so it remains practical as the database grows.
