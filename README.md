# WordleBot
A strategic solver for Wordle's Hard Mode, utilizing cryptographic letter distribution analysis to crack puzzles effectively.


# Results
| Metric              | Value          |
|---------------------|----------------|
| **Percent Solved**        | 98.79%           |
| **Average Guesses** | 3.77           |
| **Total Words**     | 2309           |
| **Total Solved**    | 2281           |
| **Total Failed**    | 28             |

# Efficiency 
| Time Metric         | Duration          |
|---------------------|----------------|
| **Total Time**      | 12.98 seconds  |
| **Average Time**    | 0.01 seconds per word |


# Approach
My approach was to choose words based on letter frequency distributions common in cryptography. The sum of their letter distribution values is the words score for that guess, and it chooses the highest scoring word. 
My goal was to deviate from the popular information theory approach of minimizing entropy (by selecting guesses that are as informative as possible).


## Cryptography Distribution
| Letter | A    | B    | C    | D    | E     | F    | G    | H    | I    | J    | K    | L    |
|--------|------|------|------|------|-------|------|------|------|------|------|------|------|
| Freq % | 8.2% | 1.5% | 2.8% | 4.3% | 12.7% | 2.2% | 2.0% | 6.1% | 7.0% | 0.2% | 0.8% | 4.0% |

| Letter | M    | N    | O    | P    | Q    | R    | S    | T    | U    | V    | W    | X    |
|--------|------|------|------|------|------|------|------|------|------|------|------|------|
| Freq % | 2.4% | 6.7% | 7.5% | 1.9% | 0.1% | 6.0% | 6.3% | 9.1% | 2.8% | 1.0% | 2.4% | 0.2% |

| Letter | Y    | Z    |
|--------|------|------|
| Freq % | 2.0% | 0.1% |
