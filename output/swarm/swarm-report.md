# Track eco

Goal: calibrate the economy: unemployment 6%, inflation 2%, wealth Gini 0.35
Status: open. Kind: economy. Writes: 6. State: 6a9d35822af0. Score: 0.115891.

## The economy now
1000 households, 50 firms, 120 periods.
Parameters: benefit = 0.4, cash_buffer = 1, debt_target = 0.6, default_after = 6, dep_share = 0, firm_w0 = 20, fiscal_rho = 0.05, g_share = 0.18, inv_target = 0.15, lam = 0.5, markup = 0.15, markup_lo = 0.02, mpc_w = 0.03426, mpc_y = 0.85, payout = 0.9, phi_pi = 1.5, phi_u = 0.5, pistar = 0.02, prod = 1, rate_sens = 5.952, res_decay = 0.1, rstar = 0.02, search = 4, spread = 0.03, tau = 0.22, theta_p = 0.1135, theta_w = 0.04259, ustar = 0.06, w0 = 6, z_sigma = 0.72
Last run: cons_share 0.8243, debt_gdp 0.7839, default_rate 0.00075, growth_ac1 -0.5952, growth_sd 0.03065, inflation 0.01451, output 934.5, policy_rate 0.04888, unemployment 0.0482, wealth_gini 0.3293

## What people have set
- Frozen: theta_w
- Constraint: keep the tax rate as it is

## What happened
20 operation(s) by 9 agent(s), 1 refused. The latest, oldest first:
- [1] 20:19:08 person: started track eco
- [2] 20:19:08 person: evolve.start
- [103] 20:19:25 evolve:calib: wrote a new state (score 1.4732189688441122)
- [104] 20:19:25 critic-007: posted a note: champion 12: unemployment is furthest from target (0.002 vs 0.06); try the parameters that drive it
- [105] 20:19:27 validator-002: posted a progress: checked champion 12: money conserved, known answers pass
- [106] 20:20:02 evolve:calib: wrote a new state (score 1.2766881833317292)
- [107] 20:20:02 critic-007: posted a note: champion 54: unemployment is furthest from target (0.003 vs 0.06); try the parameters that drive it
- [108] 20:20:06 validator-001: posted a progress: checked champion 54: money conserved, known answers pass
- [109] 20:20:41 evolve:calib: wrote a new state (score 0.7747582144999894)
- [110] 20:20:41 critic-009: posted a note: champion 69: unemployment is furthest from target (0.015 vs 0.06); try the parameters that drive it
- [111] 20:20:42 validator-005: posted a progress: checked champion 69: money conserved, known answers pass
- [113] 20:20:43 person: froze theta_w
- [114] 20:21:24 evolve:calib: wrote a new state (score 0.36940623057528066) - REFUSED [unread from person]
- [115] 20:21:24 evolve:calib: wrote a new state (score 0.36940623057528066)
- [116] 20:21:24 critic-010: posted a note: champion 129: wealth_gini is furthest from target (0.159 vs 0.35); try the parameters that drive it
- [117] 20:21:25 validator-002: posted a progress: checked champion 129: money conserved, known answers pass
- [118] 20:22:03 evolve:calib: wrote a new state (score 0.15983307326986432)
- [119] 20:22:03 critic-010: posted a note: champion 204: inflation is furthest from target (0.014 vs 0.02); try the parameters that drive it
- [120] 20:22:04 validator-003: posted a progress: checked champion 204: money conserved, known answers pass
- [121] 20:22:48 evolve:calib: wrote a new state (score 0.11589121533538317)

## Improvement studies on this track
- calib (open): aims at unemployment 0.06, inflation 0.02, wealth_gini 0.35; round 6, 540 of 2000 evaluations used; 2 candidate(s) refused because they did worse on the hidden cases.
  Champion: candidate 247 by explorer-050, distance to targets 0.1159 (hidden cases 0.109), with mpc_w = 0.03426, rate_sens = 5.952, theta_p = 0.1135.
  Candidates by proposer (best distance): explorer-083 2 (0.108), explorer-050 2 (0.116), explorer-045 2 (0.117), explorer-037 5 (0.144), explorer-093 3 (0.144), explorer-059 7 (0.152), explorer-038 5 (0.159), explorer-020 3 (0.16), explorer-042 2 (0.16), explorer-047 2 (0.16), explorer-075 3 (0.16), explorer-081 3 (0.16), explorer-085 3 (0.16), explorer-090 4 (0.16), explorer-097 3 (0.172), explorer-036 3 (0.175), explorer-016 5 (0.181), explorer-026 2 (0.184), explorer-051 2 (0.187), explorer-049 2 (0.193), explorer-080 3 (0.197), explorer-071 3 (0.205), explorer-053 2 (0.206), explorer-070 2 (0.213), explorer-064 2 (0.221), explorer-018 2 (0.23), explorer-076 5 (0.238), explorer-057 3 (0.256), explorer-078 2 (0.268), explorer-060 3 (0.269), explorer-095 3 (0.29), explorer-087 3 (0.293), explorer-048 4 (0.297), explorer-031 4 (0.311), explorer-074 3 (0.311), explorer-088 4 (0.311), explorer-043 4 (0.311), explorer-025 3 (0.313), explorer-046 2 (0.319), explorer-029 5 (0.325), explorer-052 5 (0.325), explorer-063 3 (0.334), explorer-065 3 (0.334), explorer-039 3 (0.334), explorer-019 2 (0.336), explorer-035 3 (0.349), explorer-084 5 (0.353), explorer-044 2 (0.356), explorer-023 2 (0.359), explorer-021 4 (0.369), explorer-058 2 (0.369), explorer-062 3 (0.369), explorer-067 2 (0.369), explorer-072 6 (0.369), explorer-082 2 (0.369), explorer-094 5 (0.369), explorer-099 2 (0.369), explorer-028 2 (0.373), explorer-024 2 (0.403), explorer-040 4 (0.404), explorer-066 4 (0.416), explorer-068 3 (0.42), explorer-073 2 (0.43), explorer-079 3 (0.441), explorer-056 3 (0.445), explorer-086 4 (0.448), explorer-054 2 (0.476), explorer-096 2 (0.478), explorer-061 2 (0.483), explorer-098 3 (0.501), explorer-022 2 (0.529), explorer-027 2 (0.618), explorer-034 4 (0.651), explorer-089 4 (0.661), explorer-032 5 (0.849), explorer-069 2 (0.866), explorer-091 3 (0.975), explorer-077 4 (1.2), explorer-030 2 (1.26), explorer-041 3 (1.27), explorer-017 4 (1.28), explorer-033 5 (1.3), loop 2 (1.31), explorer-055 2 (1.5), start 1 (1.66), explorer-092 2 (2.06).

Most active: evolve:calib (7), person (3), validator-002 (2), critic-010 (2), critic-007 (2).
