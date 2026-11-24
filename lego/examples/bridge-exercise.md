# Exercise: one set of numbers, three annual answers

A self-contained exercise on frequency bridges, for a workshop or on your own. It needs only Python 3.9 or later and this repository. It takes about 20 minutes.

**The point.** The quarterly values 1, 2, 3, 4 have no single "annual value". As a flow they sum to 10, as an end-of-quarter stock the year-end value is 4, and as a rate the annual average is 2.5. A bridge that only reports an annual number hides which of these it computed, so the studio records the method. And four rows are not necessarily a year: if Q2 appears twice and Q3 is missing, a correct bridge refuses before doing any arithmetic.

## Part 1: the same numbers in three roles
```
python tools/known_answer.py make bridge-flow    --out ex/flow
python tools/known_answer.py make bridge-stock   --out ex/stock
python tools/known_answer.py make bridge-average --out ex/rate
```
Each folder has `quarterly.csv` (1, 2, 3, 4) and a `TASK.md`. Convert each one with your own code, or with the studio's:
```
python tools/bridge.py convert ex/flow/quarterly.csv  --method sum     --from Q --to A
python tools/bridge.py convert ex/stock/quarterly.csv --method last    --from Q --to A
python tools/bridge.py convert ex/rate/quarterly.csv  --method average --from Q --to A
```
Write each answer to `RESULT.json` as the task says, then check it:
```
python tools/known_answer.py check bridge-flow ex/flow/RESULT.json
```
Try giving the stock answer (4) for the flow: the check fails. The method is part of the answer.

## Part 2: four rows that are not a year
```
python tools/known_answer.py make bridge-incomplete --out ex/incomplete
python tools/bridge.py convert ex/incomplete/quarterly.csv --method sum --from Q --to A
```
The conversion is refused, naming the duplicated quarter (2025Q2) and the missing one (2025Q3). It would be refused for any method: completeness is checked before aggregation.

## Part 3: a bridge inside a model
1. Copy `lego/examples/small-open-economy.lego.json` to `ex/model.lego.json`.
2. In the copy, change the `fiscal-debt-rule` brick's `"freq"` from `"Q"` to `"A"`, and run `python tools/lego.py check ex/model.lego.json`. You get a warning: no bridge is declared. `check --strict` fails.
3. Set `"bridge": "annual fiscal data"` (a text note) and check again: still a warning, because a note cannot be tested.
4. Declare the methods:
   ```json
   "bridge": {"methods": {"gdp_growth": "average", "output_gap": "average", "inflation_cpi": "average",
                          "policy_rate": "average", "fiscal_impulse": "split"}}
   ```
   Check again. Now remove `output_gap` from the list: that is an error, because a port crosses the frequency boundary without a method. Put it back, and change `policy_rate` to `"sum"`: a warning, because the port is declared a rate in `lego/ports.json`.
5. Run the bridge tests, then on data:
   ```
   python tools/lego.py bridge-test ex/model.lego.json
   python tools/lego.py bridge-test ex/model.lego.json --data output_gap=ex/incomplete/quarterly.csv
   ```
   The first passes. The second fails on the duplicated quarter.
6. Record a passing test with `--apply`. Only then will `python tools/lego.py validate` accept the brick, and only after that will `python tools/lego.py approve ex/model.lego.json fiscal-debt-rule --by "Your name"` record a sign-off. Run `check` to see the three records side by side: wiring, numbers and sign-off.

## Questions for discussion
- Which of your model's variables are flows, stocks and rates? Are any ambiguous, such as ratios to GDP?
- Growth rates do not aggregate by any of these methods exactly. How does your model convert them?
- Who in your team gives the sign-off, and what should withdraw it?
